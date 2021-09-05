import socket
import threading
import time
import typing as t
import zlib

import attrs
from cryptography.hazmat.primitives import ciphers, hashes, padding

from .exceptions import ClientError, ServerError


@attrs.define
class Connection:
    """
    Low-level conection to the AniDB UDP API with thread safe `flood
    protection <https://wiki.anidb.net/w/UDP_API_Definition#Flood_Protection>`_
    (packet rate limit, one packet every two seconds).
    """

    server_host: str = 'api.anidb.net'
    server_port: int = 9000
    local_port: int = 8888

    _lock: threading.RLock = attrs.field(init=False)
    _socket: socket.socket = attrs.field(init=False)
    _send_time: float = attrs.field(init=False)
    _send_count: int = attrs.field(init=False)
    _send_drop_count: int = attrs.field(init=False)

    def __attrs_post_init__(self):
        self._lock = threading.RLock()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(('0.0.0.0', self.local_port))
        self._socket.settimeout(4)

        self._send_time = 0
        self._send_count = 0
        self._send_drop_count = 0

    def send(self, data: bytes) -> None:
        if len(data) > 1400:
            raise ClientError("Can't send more than 1400 bytes")

        with self._lock:
            delay_secs = 0
            if self._send_count > 4:
                # "Short Term" policy (1 packet per 2 seconds).
                # Enforced after the first 5 packets.
                delay_secs = 2
            if self._send_drop_count > 4:
                # "Long Term" policy (1 packet per 4 seconds).
                # Used when server starts dropping packets.
                delay_secs = 4

            t = time.time()
            if t < self._send_time + delay_secs:
                time.sleep(self._send_time + delay_secs - t)

            try:
                self._socket.sendto(data, (self.server_host, self.server_port))
            finally:
                self._send_count += 1
                self._send_time = time.time()

    def recv(self) -> bytes:
        data = b''

        try:
            # Replies from the server will never exceed 1400 bytes.
            data = self._socket.recv(1400)
        except socket.timeout:
            with self._lock:
                self._send_drop_count += 1
        else:
            with self._lock:
                if self._send_drop_count > 0:
                    self._send_drop_count -= 1

        if not data:
            raise ServerError('Received no data from the API')
        return data


@attrs.define
class CodecPlain:
    encoding: str

    def encode(self, data: str) -> bytes:
        return data.encode(self.encoding)

    def decode(self, data: bytes) -> str:
        if data.startswith(b'\0\0'):
            data = zlib.decompressobj().decompress(data[2:])
        return data.decode(self.encoding)


@attrs.define
class CodecCrypt(CodecPlain):
    encrypt_key: str = attrs.field(repr=False)

    _cipher: ciphers.Cipher = attrs.field(init=False)
    _padding: padding.PKCS7 = attrs.field(init=False)

    def __attrs_post_init__(self):
        digest = hashes.Hash(hashes.MD5())
        digest.update(self.encrypt_key.encode(self.encoding))
        key_hash = digest.finalize()

        self._cipher = ciphers.Cipher(
            ciphers.algorithms.AES128(key_hash),
            ciphers.modes.ECB(),
        )

        self._padding = padding.PKCS7(128)

    def encode(self, data: str) -> bytes:
        encoded_data = super().encode(data)

        padder = self._padding.padder()
        padded_data = padder.update(encoded_data)
        padded_data += padder.finalize()

        encryptor = self._cipher.encryptor()
        encrypted_data = encryptor.update(padded_data)
        encrypted_data += encryptor.finalize()

        return encrypted_data

    def decode(self, data: bytes) -> str:
        decryptor = self._cipher.decryptor()
        decrypted_data = decryptor.update(data)
        decrypted_data += decryptor.finalize()

        unpadder = self._padding.unpadder()
        unpadded_data = unpadder.update(decrypted_data)
        unpadded_data += unpadder.finalize()

        decoded_data = super().decode(unpadded_data)

        return decoded_data


@attrs.define
class Result:
    command: str
    params: dict[str, t.Any]
    code: int
    message: str
    data: tuple[tuple[str, ...], ...]


@attrs.define
class Client:
    client_name: str
    client_version: int

    _connection: Connection = attrs.field(init=False)
    _lock: threading.RLock = attrs.field(init=False)
    _codec: CodecPlain = attrs.field(init=False)
    _session_key: t.Optional[str] = attrs.field(init=False)

    def __attrs_post_init__(self):
        self._connection = Connection()
        self._lock = threading.RLock()
        self._codec = CodecPlain('ASCII')
        self._session_key = None

    def command(self,
                command: str,
                params: t.Optional[dict[str, t.Any]] = None,
                ) -> Result:
        """
        Sends a command to the API, wait for a response, and return the command
        result.

        Exceptions are raised only for common client and server side errors. You
        still need to check the result code to see if the command succeeded or
        not.

        Commands documentation is on `AniDB Wiki`_.

        .. _AniDB Wiki: https://wiki.anidb.net/w/UDP_API_Definition

        Args:
            command: Command name.
            params: Command parameters.

        Returns:
            Command result.

        Raises:
            ClientError: Raised for common client side errors, like invalid
                command or invalid parameters.
            ServerError: When something went wrong on the server side.
        """
        command = command.upper()
        params = params or {}

        params_copy = params.copy()
        for k, v in params_copy.items():
            if v is None:
                v = ''
            elif isinstance(v, bool):
                v = int(v)
            params_copy[k] = str(v).replace('&', '&amp;').replace('\n', '<br />')

        with self._lock:
            if command not in {'PING', 'ENCODING', 'ENCRYPT', 'AUTH', 'VERSION'}:
                if not self._session_key:
                    result = Result(
                        command=command,
                        params=params,
                        code=501,
                        message='LOGIN FIRST',
                        data=tuple(),
                    )
                    raise ClientError.from_result(result)
                params_copy['s'] = self._session_key

            params_str = '&'.join(f'{k}={v}' for k, v in params_copy.items())
            request = self._codec.encode(f'{command} {params_str}'.strip())

            self._connection.send(request)
            response = self._connection.recv()

            lines = self._codec.decode(response).split('\n')

        code, message = lines[0].split(' ', maxsplit=1)
        data = tuple(
            tuple(field.replace('<br />', '\n') for field in line.split('|'))
            for line in lines[1:]
        )

        result = Result(
            command=command,
            params=params,
            code=int(code),
            message=message,
            data=data,
        )

        if result.code >= 600:
            raise ServerError.from_result(result)
        elif result.code >= 500:
            raise ClientError.from_result(result)

        return result

    def ping(self) -> bool:
        """
        Check if API is available.

        Does not require active session, so it may be called even if a user not
        logged in.

        Returns:
            ``True`` if API is available, ``False`` otherwise.

        See also:
            :meth:`command`
        """
        try:
            return self.command('PING').code == 300
        except Exception:
            return False

    def encrypt(self, username: str, api_key: str) -> None:
        """
        Start encrypted session. A normal authentication is still necessary and
        should follow the `encrypt` call.

        Args:
            username: User name.
            api_key: API key, defined in profile settings.

        Raises:
            ClientError: Raised when encrypted session could not be established.

        See also:
            :meth:`command`
        """
        with self._lock:
            result = self.command('ENCRYPT', {
                'user': username,
                'type': 1,
            })
            if result.code != 209:
                raise ClientError.from_result(result)

            key = api_key + result.message.split()[0]
            self._codec = CodecCrypt(self._codec.encoding, key)

    def auth(self, username: str, password: str) -> Result:
        """
        Authenticate to AniDB.

        Args:
            username: User name.
            password: User password.

        Returns:
            AUTH command result with session key removed from the result
            message.

        Raises:
            ClientError: Raised when authentication failed.

        See also:
            :meth:`command`
        """
        with self._lock:
            result = self.command('AUTH', {
                'user': username,
                'pass': password,
                'protover': 3,
                'client': self.client_name,
                'clientver': self.client_version,
                'enc': 'UTF-8',
                'comp': True,
            })
            if result.code not in {200, 201}:
                raise ClientError.from_result(result)

            self._codec = CodecPlain('UTF-8')
            self._session_key, message = result.message.split(maxsplit=1)
            result.message = message

            return result

    def logout(self) -> None:
        """
        Logout from AniDB.

        See also:
            :meth:`command`
        """
        with self._lock:
            result = self.command('LOGOUT')
            if result.code == 203:
                self._codec = CodecPlain('ASCII')
                self._session_key = None

    def check_session(self) -> bool:
        """
        Check if a user is logged in and the session is still active on the
        server.

        This method can be called once every 30 minutes to keep the connection
        alive.

        See also:
            :meth:`command`
        """
        with self._lock:
            return self._session_key is not None and self.command('UPTIME').code == 208
