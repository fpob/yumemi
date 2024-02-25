import datetime
import multiprocessing
import os
import re
import string
import time
from pathlib import Path

import click

from . import AnidbError, Client
from . import _rhash as rhash


CLIENT_NAME = 'yumemi'
CLIENT_VERSION = 4

# Parameters for FILE command.
FILE_FMASK = '78380000'
FILE_AMASK = '30E0F0C0'
# Data keys in FILE command response.
FILE_KEYS = [
    'fid', 'aid', 'eid', 'gid', 'lid', 'md5', 'sha1', 'crc32', 'ayear', 'atype',
    'aname', 'aname_kanji', 'aname_english', 'epno', 'epname', 'epname_romaji',
    'epname_kanji', 'gname', 'gsname',
]
"""
- ``fid``, ``aid``, ``eid``, ``gid``, ``lid`` -- AniDB IDs for the file, anime,
  episode, group, mylist entry
- ``md5``, ``sha1``, ``crc32`` -- file hashes from the AniDB
- ``ayear`` -- year the anime was airing
- ``atype`` -- anime type, TV Series / Movie / Web / ...
- ``aname``, ``aname_kanji``, ``aname_english`` -- anime title in romaji, kanji,
  english
- ``epno`` -- episode number
- ``epname`` -- episode name in english, romaji, kanji
- ``gname`` -- group that released the episode file (eg. SubsPlease)
- ``gsname`` -- short group name
"""


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


class DateTime(click.ParamType):
    name = 'datetime'

    def __init__(self, format):
        super().__init__()
        self.format = format

    def convert(self, value, param, ctx):
        try:
            return datetime.datetime.strptime(value, self.format)
        except ValueError:
            self.fail(f"format must be '{self.format}'")


class TemplateString(click.ParamType):
    name = 'template'

    def __init__(self, mapping_keys):
        super().__init__()
        self.mapping_keys = mapping_keys

    def convert(self, value, param, ctx):
        tpl = string.Template(value)
        # TODO `get_identifiers()` in Python >=3.11
        try:
            tpl.substitute(dict.fromkeys(self.mapping_keys, 'test'))
            return tpl
        except (KeyError, ValueError) as e:
            self.fail(f'Template is not valid, {e}')


def sanitize_filename(filename):
    filename = filename.replace('/', '-')
    filename = re.sub(r'\s+', ' ', filename).strip()
    filename = re.sub(r'[\x00-\x1f]', '', filename)
    return filename


def safe_rename(old, new):
    if new.exists():
        raise FileExistsError(f'file "{new!s}" exists')
    os.rename(old, new)


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
    type=DateTime('%Y-%m-%d'),
    default=None,
    metavar='YYYY-MM-DD',
    help='Mark files as watched and set watched date to the specified value.',
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
    '-r', '--rename',
    is_flag=True,
    default=False,
    help='Rename files.',
)
@click.option(
    '-R', '--rename-format',
    type=TemplateString(FILE_KEYS),
    default='$aname - $epno',
    show_default=True,
    help=('Format for renaming files. Template vars: '
          + ', '.join(f'${i}' for i in FILE_KEYS)),
)
@click.argument(
    'files',
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def main(username, password, watched, watched_date, deleted, edit, encrypt,
         rename, rename_format, files):
    """AniDB client for adding files to mylist."""
    if watched_date is not None:
        watched = True
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

    mp_pool = multiprocessing.Pool(1)

    try:
        files_params = mp_pool.imap(mylistadd_file_params, files)
        for file, file_ed2k, file_size in files_params:
            click.secho(file, bold=True)
            click.echo(f'  - ed2k={file_ed2k} size={file_size}')

            mylistadd_result = client.command('MYLISTADD', {
                'ed2k': file_ed2k,
                'size': file_size,
                'state': 3 if deleted else 1,  # 1 = internal storage (hdd)
                'viewed': watched,
                'viewdate': int(watched_date.timestamp()) if watched_date else 0,
                'edit': edit,
            })

            click.echo(f'  - {mylistadd_result.message.lower()}')

            if not rename or mylistadd_result.code == 320:
                continue

            file_result = client.command('FILE', {
                'ed2k': file_ed2k,
                'size': file_size,
                'fmask': FILE_FMASK,
                'amask': FILE_AMASK,
            })

            if file_result.code != 220:
                click.echo(f'  - {file_result.message.lower()}')
                continue

            file_vars = dict(zip(FILE_KEYS, file_result.data[0]))

            file_path_old = Path(file)
            file_path_new = file_path_old.parent / sanitize_filename(
                rename_format.substitute(file_vars) + file_path_old.suffix
            )

            try:
                safe_rename(file_path_old, file_path_new)
                click.echo(f'  - renamed to "{file_path_new!s}"')
            except Exception as e:
                click.echo(f'  - failed to rename, {e!s}')

    except AnidbError as e:
        click.secho(str(e), fg='red', err=True)

    mp_pool.close()
    mp_pool.join()

    client.logout()


if __name__ == '__main__':
    main()
