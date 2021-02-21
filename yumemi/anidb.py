import socket
import ctypes
import multiprocessing
import time
import hashlib
import re
import zlib

try:
    from Crypto.Cipher import AES
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

from .exceptions import (SocketError, SocketTimeout, ServerError, ClientError,
                         EncryptError)


class Socket:
    """
    AniDB socket with thread safe `flood protection`_.

    .. _flood protection: https://wiki.anidb.net/w/UDP_API_Definition#Flood_Protection
    """

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
        Send data to AniDB and wait for and return response from AniDB.

        Data length is limited to 1400 bytes and if this limit is exceeded,
        :class:`SocketError` is raised.

        This function is thread safe so multiple processes or threads can send
        data to AniDB and packets are correctly delayed (according to AniDB
        flood protection policy) and paired (request-response).

        .. note::
            This method is thread safe.

        :param data: data to send to AniDB
        :type data: bytes
        :return: response from AniDB, note that reponse may be copressed or encrypted
        :rtype: bytes
        :raises SocketError: when data size is greater than 1400 bytes
        :raises SocketTimeout: on socket timeout, server is probably down
        """
        with self._lock:
            if len(data) > 1400:
                raise SocketError('Can\'t send more than 1400 bytes')

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


class Codec:
    """
    Class for encoding and decoding strings to bytes with compression support.

    :param encoding: string encoding

    :ivar encoding: string encoding
    """

    def __init__(self, encoding):
        self.encoding = encoding

    def encode(self, data):
        """Encode given string data to bytes."""
        return data.encode(self.encoding)

    def decode(self, data):
        """Decode data from given bytes to string."""
        if data.startswith(b'\0\0'):
            data = zlib.decompressobj().decompress(data[2:])
        return data.decode(self.encoding)


class EncryptCodec(Codec):
    """
    Codec with AES encryption (AES 128-bit, ECB, PKCS5).

    :param api_key: "UDP API key", can be found at AniDB in Settings > Account
    :param salt: salt returned by `ENCRYPT` command
    :param encoding: string encoding

    :raises ImportError: If package pycrypto is not installed.

    :ivar encoding: string encoding
    """

    def __init__(self, key, encoding):
        if not HAS_CRYPTO:
            raise EncryptError('Package `pycrypto` is not installed')
        super().__init__(encoding)
        self._aes = AES.new(self._hash_key(key), AES.MODE_ECB)

    def _hash_key(self, key):
        return hashlib.new('md5', key.encode(self.encoding)).digest()

    def _encrypt(self, data):
        """Pad bytes data for encrypting."""
        data += (16 - len(data) % 16) * bytes([16 - len(data) % 16])
        return self._aes.encrypt(data)

    def _decrypt(self, data):
        """Unpad bytes data after decrypting."""
        data = self._aes.decrypt(data)
        return data[:-data[-1]]

    def encode(self, data):
        """Encode given string data to bytes and encrypt them."""
        return self._encrypt(super().encode(data))

    def decode(self, data):
        """Decode data from given bytes to string and decrypt them."""
        return super().decode(self._decrypt(data))


class Response:
    """Class which wraps data from response."""

    def __init__(self, code, message, data=None):
        self._code = code
        self._message = message
        self._data = data or tuple()

    @property
    def code(self):
        """
        Response code.

        :type: int
        """
        return self._code

    @property
    def message(self):
        """
        Textual representation of response code.

        :type: str
        """
        return self._message

    @property
    def data(self):
        """
        Data from response.

        Tuple of tuples with fields (``tuple[tuple[str, ...], ...]``) or empty
        tuple on error.

        :type: tuple
        """
        return self._data

    def data_asdict(self, keys):
        """
        Convert :attr:`data` to tuple of dicts.

        :param: list of keys for created dicts

        :raises ValueError: If number of provided keys not match number of
                            fields in :attr:`data`
        """
        def fields_asdict(fields):
            if len(keys) != len(fields):
                raise ValueError('Number of keys not match number of fields')
            return dict(zip(keys, fields))
        return tuple(fields_asdict(fields) for fields in self.data)

    def __str__(self):
        return self._message


class Client:
    """
    Main class for communication with AniDB.

    Implements some basic commands and provides interface to use all other
    commands via :meth:`call` method.

    This class can be used in `with` statement. ::

        with yumemi.Client() as c:
            ...
    """

    PROTOVER = 3
    CLIENT = 'yumemi'
    VERSION = 3
    ENCODING = 'UTF-8'

    # Default connection parameters
    SERVER = ('api.anidb.net', 9000)
    LOCALPORT = 8888

    # Valid username regex.
    USERNAME_CRE = re.compile(r'^[a-zA-Z0-9_-]{3,16}$')

    def __init__(self, server=None, localport=None, session=None, encoding=None):
        self._socket = Socket(server or self.SERVER, localport or self.LOCALPORT)
        self._codec = Codec(encoding or self.ENCODING)
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
        """
        See:
            :meth:`call`
        """
        return self.call(*args, **kwargs)

    def call(self, command, params=None, retry=1):
        """
        Send command to AniDB and return response.

        When sending command that require login session, parameter 's' is
        automatically set. If user is not logged in and sending some command
        that requires login then :class:`ClientError` is raised even without
        sending any packet.

        .. note::
            This method itself is thread safe since it do not change state of
            `self`.

        :param command: AniDB command, case insensitive
        :type command: str
        :param params: command parameters
        :type params: dict
        :param retry: number of retries
        :type retry: int

        :returns: decoded and parsed response from AniDB
        :rtype: :class:`Response`

        :raises SocketError: socket errors
        :raises ClientError: client side error or when not loggen in and
                             command require session (response code 500-599)
        :raises ServerError: server side error (response code 600-699)

        See:
            https://wiki.anidb.net/w/UDP_API_Definition
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

        for k, v in params.items():
            if v is None:
                v = ''
            elif isinstance(v, bool):
                v = int(v)
            params[k] = str(v).replace('&', '&amp;').replace('\n', '<br />')

        query = '&'.join('{}={}'.format(k, v) for k, v in params.items())
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
        data = tuple(
            tuple(field.replace('<br />', '\n') for field in line.split('|'))
            for line in lines[1:]
        )

        response = Response(code, message, data)
        if 500 <= response.code <= 599:
            raise ClientError.from_response(response)
        if 600 <= response.code <= 699:
            raise ServerError.from_response(response)
        return response

    def ping(self):
        """
        Test connection to server or keep connection alive.

        Uses :meth:`call` with ``PING`` command.

        :returns: `True` if connection and server is okay, otherwise `False`
        """
        try:
            return self.call('PING').code == 300
        except SocketTimeout:
            return False

    def encrypt(self, api_key, username):
        """
        Start encrypted session.

        Uses :meth:`call` with ``ENCRYPT`` command.

        :param api_key: API key, defined in profile settings
        :param username: user name

        :returns: :class:`Response`

        :raises EncryptError: when encrypted session could not be established
        """
        response = self.call('ENCRYPT', {
            'user': username,
            'type': 1,
        }, retry=0)

        if response.code == 209:
            salt, _ = response.message.split(' ', maxsplit=1)
            self._codec = EncryptCodec(api_key + salt, self._codec.encoding)
        elif response.code in {309, 394}:
            raise EncryptError.from_response(response)

        return response

    def auth(self, username, password):
        """
        Authorize to AniDB.

        Uses :meth:`call` with ``AUTH`` command.

        :param username: user name
        :param password: user's password

        :returns: :class:`Response`
        """
        response = self.call('AUTH', {
            'user': username,
            'pass': password,
            'protover': self.PROTOVER,
            'client': self.CLIENT,
            'clientver': self.VERSION,
            'enc': self._codec.encoding,
            'comp': '1',
        }, retry=0)

        self._session = None
        if response.code in {200, 201}:
            self._session, _ = response.message.split(' ', maxsplit=1)

        return response

    def encoding(self, encoding):
        """
        Change encoding for session. This command does not require session.

        Uses :meth:`call` with ``ENCODING`` command.

        .. note::
            Encoding is reset to default ASCII on logout or on timeout.

        :param encoding: encoding name

        :returns: `True` if encoding was changed, otherwise `False`

        List of supported encodings:
            http://java.sun.com/j2se/1.5.0/docs/guide/intl/encoding.doc.html
        """
        response = self.call('ENCODING', {'name': encoding})
        if response.code == 219:
            self._codec.encoding = encoding
            return True
        return False

    def logout(self):
        """
        Logout from AniDB.

        Uses :meth:`call` with ``LOGOUT`` command.

        :returns: :class:`Response`
        """
        response = self.call('LOGOUT')
        if response.code == 203:
            self._session = None
            self._codec = Codec(self.ENCODING)
        return response

    def is_logged_in(self):
        """
        Check if user is logged in (session key is set). To check if session is
        active use :meth:`check_session`.

        :returns: bool
        """
        return self._session is not None

    def check_session(self):
        """
        Check if session is still active on server. If this method return
        `False` then auth sequence (:meth:`encrypt`, :meth:`encoding` and
        :meth:`auth`) must be resubmitted.

        Uses :meth:`call` with ``UPTIME`` command.

        .. note::
            This method can be used to keep session alive by calling it every
            15 minutes or so.

        :returns: `True` if session is active, otherwise `False`
        """
        return self.call('UPTIME').code == 208
