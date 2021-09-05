import click.testing
import pytest

import yumemi
import yumemi.cli


@pytest.fixture
def runner(tmp_path):
    runner = click.testing.CliRunner()
    with runner.isolated_filesystem(tmp_path):
        yield runner


@pytest.fixture
def mp_pool_mock(mocker):
    m = mocker.Mock()
    mocker.patch('multiprocessing.Pool').return_value = m
    yield m


@pytest.fixture
def client_mock(mocker):
    m = mocker.Mock(spec=yumemi.Client)
    mocker.patch('yumemi.cli.Client').return_value = m
    yield m


@pytest.mark.parametrize(
    'cli_args, mylistadd_params',
    [
        pytest.param(
            [],
            {'viewed': False, 'edit': False},
            id='default',
        ),
        pytest.param(
            ['-w'],
            {'viewed': True, 'edit': False},
            id='viewed',
        ),
        pytest.param(
            ['-W', '2020-01-01'],
            {'viewed': True, 'edit': False},
            id='viewdate'
        ),
        pytest.param(
            ['-e', '-W', '2020-01-01'],
            {'viewed': True, 'edit': True},
            id='edit'
        ),
    ],
)
def test_mylistadd(runner, tmp_path, client_mock, mp_pool_mock,
                   cli_args, mylistadd_params):
    client_mock.auth.return_value = yumemi.Result(
        command='',
        params={},
        code=200,
        message='LOGIN ACCEPTED',
        data=tuple(),
    )
    client_mock.command.return_value = yumemi.Result(
        command='',
        params={},
        code=210,
        message='MYLIST ENTRY ADDED',
        data=((1,),),
    )

    mp_pool_mock.imap.return_value = [
        ('test.mkv', '47c61a0fa8738ba77308a8a600f88e4b', 1),
    ]

    file = tmp_path / 'test.mkv'
    file.write_bytes(b'\x00')

    result = runner.invoke(
        yumemi.cli.main,
        [
            '--username', 'testuser',
            '--password', 'testpass',
            '--encrypt', 'enckey',
            *cli_args,
            str(file),
        ],
    )

    assert result.exit_code == 0

    client_mock.auth.assert_called_with('testuser', 'testpass')
    client_mock.encrypt.assert_called_with('testuser', 'enckey')
    client_mock.command.assert_called()
    client_mock.logout.assert_called()

    cmd_command, cmd_params = client_mock.command.call_args.args
    assert cmd_command == 'MYLISTADD'
    assert cmd_params['ed2k'] == '47c61a0fa8738ba77308a8a600f88e4b'
    assert cmd_params['size'] == 1
    for param_key, param_value in mylistadd_params.items():
        assert cmd_params[param_key] == param_value
