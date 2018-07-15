import socket
import ctypes
import multiprocessing
import time
import hashlib
import re

from .exceptions import (SocketError, SocketTimeout, ServerError, ClientError,
                         EncryptError)


class Socket:
    """AniDB socket with thread safe flood protection."""

    _lock = multiprocessing.Lock()
    _last_time = multiprocessing.Value(ctypes.c_double, time.time())
    _send_count = multiprocessing.Value(ctypes.c_int, 0)
    _drop_count = multiprocessing.Value(ctypes.c_int, 0)

    def __init__(self, server, localport):
        self.server = server
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(('0.0.0.0', localport))
        self._socket.settimeout(4)

    def __del__(self):
        self._socket.close()

    def send_recv(self, data):
        """
        Send some bytes to AniDB and receive some bytes (joins socket.sendto()
        and socket.recv() into one method).

        Data length is limited to 1400 bytes and if this limit is exceeded,
        SockerError is raised.

        This function is thread save so multiple processes or threads can send
        data to AniDB and packets are correctly delayed (according to AniDB
        flood protection policy) and paired (request-response).

        Raises:
            SocketError
            SocketTimeout
        """
        with self._lock:
            if len(data) > 1400:
                raise SocketError('Cant send more than 1400 bytes')

            delay_secs = 0
            if self._send_count.value > 2:
                # "Short Term" policy (1 packet per 2 seconds).
                # Enforced after the first 5 packets.
                delay_secs = 2
            if self._drop_count.value > 2:
                # "Long Term" policy (1 packet per 4 seconds).
                # Used when server starts dropping packets.
                delay_secs = 4

            t = time.time()
            if t < self._last_time.value + delay_secs:
                time.sleep(self._last_time.value + delay_secs - t)

            try:
                self._socket.sendto(data, self.server)
            finally:
                self._send_count.value += 1
                self._last_time.value = time.time()
            # Must be splitted into two try blocks because _last_time update.
            try:
                # Replies from the server will never exceed 1400 bytes.
                return self._socket.recv(1400)
            except socket.timeout as e:
                self._drop_count.value += 1
                raise SocketTimeout from e
            else:
                if self._drop_count.value > 0:
                    self._drop_count.value -= 1


class Response:
    """Class which wraps data from response."""

    def __init__(self, code, message, data=None):
        self._code = code
        self._message = message
        self._data = data

    @property
    def code(self):
        """Response code."""
        return self._code

    @property
    def message(self):
        """Textual representation of response code."""
        return self._message

    @property
    def data(self):
        """
        Data from response, split to lines and then divided by field
        separators. Returns list of lists or None if error occured.
        """
        return self._data

    def __str__(self):
        return self._message


class Codec:
    """Class for encoding and decoding strings to bytes."""

    def __init__(self, encoding='ASCII'):
        self.encoding = encoding

    def encode(self, data):
        return data.encode(self.encoding)

    def decode(self, data):
        return data.decode(self.encoding)


class EncryptCodec(Codec):
    """
    Codec with AES encryption (AES 128-bit, ECB, PKCS5).

    To use encryption, package `pycrypto` is required. Raises ImportError if
    package `pycrypto` is not installed.
    """

    def __init__(self, api_key, salt, **kwargs):
        super().__init__(**kwargs)
        from Crypto.Cipher import AES
        self._aes = AES.new(self._hash_key(api_key + salt), AES.MODE_ECB)

    def _hash_key(self, key):
        return hashlib.new('md5', key.encode(self.encoding)).digest()

    def _pad(self, data):
        return data + (16 - len(data) % 16) * chr(16 - len(data) % 16)

    def _unpad(self, data):
        return data[0:-ord(data[-1])]

    def encode(self, data):
        return self._aes.encrypt(super().encode(self._pad(data)))

    def decode(self, data):
        return self._unpad(super().decode(self._aes.decrypt(data)))


class Client:
    """
    Main class for communication with AniDB.

    Implements some basic commands and provides interface to use all other
    commands.
    """

    PROTOVER = 3
    CLIENT = 'maichan'  # Old client name; version 1
    VERSION = 3
    ENCODING = 'ASCII'

    # Default connection parameters
    SERVER = ('api.anidb.net', 9000)
    LOCALPORT = 8888

    # Valid username regex.
    USERNAME_CRE = re.compile(r'^[a-zA-Z0-9_-]{3,16}$')

    def __init__(self, server=None, localport=None, session=None):
        self._socket = Socket(server or self.SERVER,
                              localport or self.LOCALPORT)
        self._codec = Codec(encoding=self.ENCODING)
        self._session = session

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # flake8: noqa: E722 (bare except)
        try:
            self.logout()
        except:
            pass
        del self._socket

    def __call__(self, *args, **kwargs):
        """See: call()"""
        return self.call(*args, **kwargs)

    def call(self, command, params=None, retry=1):
        """
        Send command to AniDB and return response.

        When sending command which require login session parameter `s` is
        automatically set. If user is not logged in and sending some command
        which requires login then ClientError is raised even without sending
        any packet.

        This method is thread safe.

        Arguments:
            command -- AniDB command, case insensitive
            params  -- dict with command parameters
            retry   -- if command fails then retry N times
        Returns:
            Response
        Raises:
            SocketTimeout
            ServerError
            ClientError

        See: https://wiki.anidb.net/w/UDP_API_Definition
        """
        command = command.upper()
        retry_count = 0

        if not params:
            params = dict()

        if command not in {'PING', 'ENCODING', 'ENCRYPT', 'AUTH', 'VERSION'}:
            # All other commands requres session.
            if not self._session:
                raise ClientError.from_response(Response(501, 'LOGIN FIRST'))
            params['s'] = self._session

        query = '&'.join('{}={}'.format(str(k), self._escape(str(v)))
                         for k, v in params.items())
        request_bytes = self._codec.encode((command + ' ' + query).strip())

        response_bytes = None
        while not response_bytes:
            try:
                response_bytes = self._socket.send_recv(request_bytes)
            except SocketTimeout:
                response_bytes = None
                if retry_count < retry:
                    retry_count += 1
                else:
                    raise

        if not response_bytes:
            raise ServerError.from_response(Response(603, 'NO DATA'))

        lines = self._codec.decode(response_bytes).splitlines()
        code, message = lines[0].split(' ', maxsplit=1)
        code = int(code)
        data = [[self._unescape(field) for field in line.split('|')]
                for line in lines[1:]]

        response = Response(code, message, data)
        if 500 <= response.code <= 599:
            raise ClientError.from_response(response)
        if 600 <= response.code <= 699:
            raise ServerError.from_response(response)
        return response

    def ping(self):
        """
        Test connection to server.

        Returns:
            True if connection and server is okay, otherwise False

        See: call()
        Command: PING
        """
        try:
            return self.call('PING').code == 300
        except SocketTimeout:
            return False

    def encrypt(self, api_key, username):
        """
        Start encrypted session.

        See: call()
        Command: ENCRYPT
        """
        response = self.call('ENCRYPT', {
            'user': username,
            'type': 1,
        }, retry=0)

        if response.code == 209:
            salt, _ = response.message.split(' ', maxsplit=1)
            self._codec = EncryptCodec(api_key, salt,
                                       encoding=self._codec.encoding)
        elif response.code in {309, 394}:
            raise EncryptError.from_response(response)

        return response

    def auth(self, username, password):
        """
        Authorize to AniDB.

        See: call()
        Command: AUTH
        """
        response = self.call('AUTH', {
            'user': username,
            'pass': password,
            'protover': self.PROTOVER,
            'client': self.CLIENT,
            'clientver': self.VERSION,
            'enc': self.ENCODING,
        }, retry=0)

        self._session = None
        if response.code in {200, 201}:
            self._session, _ = response.message.split(' ', maxsplit=1)

        return response

    def logout(self):
        """
        Logout from AniDB.

        See: call()
        Command: LOGOUT
        """
        response = self.call('LOGOUT')
        if response.code == 203:
            self._session = None
            self._codec = Codec(encoding=self._codec.encoding)
        return response

    def is_logged_in(self):
        """Check if user is logged in (session key is set)."""
        return self._session is not None

    def _escape(self, string):
        """AniDB content encoding (to server)."""
        return (string
                .replace('&', '&amp;')
                .replace('\n', '<br />'))

    def _unescape(self, string):
        """AniDB content decoding (from server)."""
        return (string
                .replace('<br />', '\n')
                .replace('`', "'")
                .replace('/', '|'))
