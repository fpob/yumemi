import socket


class AnidbError(RuntimeError):
    """Base error."""
    pass


class SocketError(AnidbError):
    pass


class SocketTimeout(SocketError, socket.timeout):
    pass


class AnidbApiError(AnidbError):
    """Error from AniDB API, base Exception."""
    def __init__(self, *args, response=None):
        super().__init__(*args)
        self.response = response

    @classmethod
    def from_response(cls, response):
        return cls(str(response), response=response)


class ServerError(AnidbApiError):
    """AniDB API error with code 6**."""
    pass


class ClientError(AnidbApiError):
    """AniDB API error with code 5** and 4**."""
    pass


class EncryptError(AnidbApiError):
    """Encryption error, encrypted session cannot be established."""
    pass
