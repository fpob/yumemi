import datetime
import multiprocessing
import os
import time

import click
import rhash

from . import AnidbError, Client


CLIENT_NAME = 'yumemi'
CLIENT_VERSION = 4


def ping(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    client = Client(CLIENT_NAME, CLIENT_VERSION)

    start = time.time()
    pong = client.ping()
    end = time.time()

    if pong:
        click.echo(f'OK, {round((end - start) * 1000)} ms', err=True)
    else:
        click.echo('AniDB API server is unavailable', err=True)

    ctx.exit(not pong)


def mylistadd_file_params(file):
    return (
        file,
        rhash.hash_file(file, rhash.ED2K),
        os.path.getsize(file),
    )


@click.command(
    context_settings=dict(
        help_option_names=['-h', '--help'],
        auto_envvar_prefix='YUMEMI',
    ),
)
@click.version_option()
@click.option(
    '--ping',
    is_flag=True,
    callback=ping,
    is_eager=True,
    expose_value=False,
    help='Test connection to AniDB API server.',
)
@click.option(
    '-u', '--username',
    prompt=True,
)
@click.option(
    '-p', '--password',
    prompt=True,
    hide_input=True,
)
@click.option(
    '--encrypt',
    default=None,
    help='Ecrypt connection. Parameter value is API Key.',
)
@click.option(
    '-w', '--watched',
    is_flag=True,
    default=False,
    help='Mark files as watched.',
)
@click.option(
    '-W', '--watched-date',
    default=None,
    metavar='DATE',
    help=(
        'Mark files as watched and set watched date to the specified value. '
        'Format: YYYY-MM-DD.'
    ),
)
@click.option(
    '-d', '--deleted',
    is_flag=True,
    default=False,
    help='Set file state to deleted.',
)
@click.option(
    '-e', '--edit',
    is_flag=True,
    default=False,
    help='Edit watched state and date of files that are already in mylist.',
)
@click.option(
    '-j', '--jobs',
    type=int,
    default=1,
    show_default=True,
    help='Number of processes launched to calculate file hashes.',
)
@click.argument(
    'files',
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def main(username, password, watched, watched_date, deleted, edit, encrypt, jobs,
         files):
    """AniDB client for adding files to mylist."""
    if watched_date:
        watched = True
        try:
            watched_date = datetime.datetime.strptime(watched_date, '%Y-%m-%d')
        except ValueError as e:
            raise click.BadOptionUsage(
                'watched_date',
                f"Date '{watched_date}' does not match format 'YYYY-MM-DD'."
            ) from e
    elif watched:
        watched_date = datetime.datetime.now()

    client = Client(CLIENT_NAME, CLIENT_VERSION)
    try:
        if encrypt:
            client.encrypt(username, encrypt)
        client.auth(username, password)
    except AnidbError as e:
        msg = str(e)
        if e.result and e.result.code in {503, 504}:
            msg = 'Client version is no longer supported, please update.'
        click.secho(msg, fg='red', err=True)
        raise click.Abort

    mp_pool = multiprocessing.Pool(jobs)

    try:
        files_params = mp_pool.imap(mylistadd_file_params, files)
        for file, file_ed2k, file_size in files_params:
            result = client.command('MYLISTADD', {
                'ed2k': file_ed2k,
                'size': file_size,
                'state': 3 if deleted else 1,  # 1 = internal storage (hdd)
                'viewed': watched,
                'viewdate': int(watched_date.timestamp()) if watched_date else 0,
                'edit': edit,
            })

            if result.code in {210, 310, 311}:
                status = click.style(' OK ', fg='green')
            else:
                status = click.style('FAIL', fg='red')

            click.echo(f'[{status}] {result.message}: {click.format_filename(file)}')

    except AnidbError as e:
        click.secho(str(e), fg='red', err=True)

    mp_pool.close()
    mp_pool.join()

    client.logout()


if __name__ == '__main__':
    main()
