import typing as t


if t.TYPE_CHECKING:
    from . import Result


class AnidbError(Exception):
    result: t.Optional['Result']
    """
    If an exception was caused by a command, this attribute will contain the
    result of the command.
    """

    def __init__(self, *args, result: t.Optional['Result'] = None):
        super().__init__(*args)
        self.result = result

    @classmethod
    def from_result(cls, result: 'Result') -> 'AnidbError':
        return cls(result.message, result=result)


class ServerError(AnidbError):
    pass


class ClientError(AnidbError):
    pass
