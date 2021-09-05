import pytest

import yumemi


@pytest.fixture
def connection_mock(mocker):
    m = mocker.Mock(spec=yumemi.Connection)
    mocker.patch('yumemi.anidb.Connection').return_value = m
    yield m


def test_plain_compressed_decode():
    data = b'\0\0x\x9c\xf3H\xcd\xc9\xc9Wp\xcc\xcbtq\x02\x00\x17\x0c\x03\xb3'
    plain = 'Hello AniDB'

    c = yumemi.CodecPlain('UTF-8')
    assert c.decode(data) == plain


def test_crypt_encode():
    key = 'apikeysalt'
    data = b']g\r\xc7\xcc\x04|\x9f\x0f\xa3\xd3\x0eM\x9d~\x0f'
    plain = 'Hello AniDB'

    c = yumemi.CodecCrypt('UTF-8', key)
    assert c.encode(plain) == data


def test_crypt_decode():
    key = 'apikeysalt'
    data = b']g\r\xc7\xcc\x04|\x9f\x0f\xa3\xd3\x0eM\x9d~\x0f'
    plain = 'Hello AniDB'

    c = yumemi.CodecCrypt('UTF-8', key)
    assert c.decode(data) == plain


@pytest.mark.parametrize(
    'expected_result, send_data, recv_data',
    [
        (
            yumemi.Result(
                command='FOO',
                params={'foo': 'bar'},
                code=200,
                message='BAR',
                data=(('foo', 'bar'),),
            ),
            b'FOO foo=bar&s=sesskey',
            b'200 BAR\nfoo|bar',
        ),
        (
            yumemi.Result(
                command='FOO',
                params={'foo': 'bar&abc'},
                code=200,
                message='BAR',
                data=(('foo', 'bar'),),
            ),
            b'FOO foo=bar&amp;abc&s=sesskey',
            b'200 BAR\nfoo|bar',
        ),
        (
            yumemi.Result(
                command='FOO',
                params={'foo': 'bar\nabc'},
                code=200,
                message='BAR',
                data=(('foo', 'bar'),),
            ),
            b'FOO foo=bar<br />abc&s=sesskey',
            b'200 BAR\nfoo|bar',
        ),
        (
            yumemi.Result(
                command='FOO',
                params={'foo': 'bar'},
                code=200,
                message='BAR',
                data=(('foo\nbar', 'abc'),),
            ),
            b'FOO foo=bar&s=sesskey',
            b'200 BAR\nfoo<br />bar|abc',
        ),
        (
            yumemi.Result(
                command='FOO',
                params={'foo': 'bar'},
                code=200,
                message='BAR',
                data=(('foo', 'bar'), ('abc', 'xyz')),
            ),
            b'FOO foo=bar&s=sesskey',
            b'200 BAR\nfoo|bar\nabc|xyz',
        ),
    ]
)
def test_client_command(connection_mock, expected_result, send_data, recv_data):
    connection_mock.recv.return_value = recv_data

    client = yumemi.Client('test', 1)
    client._session_key = 'sesskey'

    result = client.command(expected_result.command, expected_result.params)

    assert result.command == expected_result.command
    assert result.params == expected_result.params
    assert result.code == expected_result.code
    assert result.message == expected_result.message
    assert result.data == expected_result.data

    connection_mock.send.assert_called_with(send_data)


def test_client_command_error(connection_mock):
    connection_mock.recv.return_value = b'600 INTERNAL_SERVER_ERROR'

    client = yumemi.Client('test', 1)
    client._session_key = 'sesskey'

    with pytest.raises(yumemi.ServerError):
        client.command('PING')
