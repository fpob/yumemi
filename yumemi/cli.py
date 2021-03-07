import multiprocessing
import os
import re
import time

import click
import dateutil.parser
import dateutil.relativedelta

from . import __version__
from . import anidb
from . import exceptions
from . import ed2k


class AnidbDate(click.ParamType):
    """
    AniDB Date parameter.

    Converts local time to server (UTC) time.
    """

    name = 'anidb_date'

    @staticmethod
    def now():
        return int(time.time())

    @staticmethod
    def from_str(date_time_str, _format=None):
        """Create timestamp from string."""
        relative = re.match(r'^(y|-\d+d?) (.*)$', date_time_str)
        if relative:
            dt = dateutil.parser.parse(relative.group(2))
            if relative.group(1) == 'y':
                dt += dateutil.relativedelta.relativedelta(days=-1)
            else:
                days_delta = int(relative.group(1)[:-1])
                dt += dateutil.relativedelta.relativedelta(days=days_delta)
        else:
            dt = dateutil.parser.parse(date_time_str)
        return int(dt.timestamp())

    def convert(self, value, param, ctx):
        if not value:
            return 0
        try:
            return self.from_str(value)
        except ValueError as e:
            self.fail(' '.join(e.args))


def validate_username(ctx, param, value):
    if not anidb.Client.USERNAME_CRE.match(value):
        raise click.BadParameter('Invalid username')
    return value


def ping(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    client = anidb.Client()

    start = time.time()
    pong = client.ping()
    end = time.time()

    if pong:
        click.echo('OK, {} ms'.format(round((end - start) * 1000)), err=True)
    else:
        click.echo('AniDB API server is unavailable', err=True)

    ctx.exit(not pong)


def mylistadd_file_params(file):
    return file, ed2k.file_ed2k(file), os.path.getsize(file)


@click.command(
    context_settings=dict(
        help_option_names=['-h', '--help'],
        auto_envvar_prefix='YUMEMI',
    ),
)
@click.version_option(version=__version__)
@click.option('--ping', is_flag=True, callback=ping, is_eager=True,
              expose_value=False, help='Test connection to AniDB API server.')
@click.option('-u', '--username', prompt=True, envvar='USERNAME',
              callback=validate_username)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('--encrypt', default=None, envvar='ENCRYPT',
              help='Ecrypt messages. Parameter value is API Key.')
@click.option('-w', '--watched', is_flag=True, default=False,
              help='Mark files as watched.')
@click.option('-W', '--view-date', type=AnidbDate(), default=0, metavar='DATE',
              help='Set viewdate to certain date. Implies -w/--watched.'
              ' Formats: Y-m-d[ H:M] | H:M (today) | y H:M (yesterday)'
              ' | -#[d] H:M (before # days).')
@click.option('-d', '--deleted', is_flag=True, default=False,
              help='Set file state to deleted.')
@click.option('-e', '--edit', is_flag=True, default=False,
              help='Set edit flag to true.')
@click.option('-j', '--jobs', type=int, default=None, envvar='JOBS',
              help='Number of adding processes. Default is CPU count.')
@click.argument('files', nargs=-1, required=True,
                type=click.Path(exists=True, dir_okay=False))
def main(username, password, watched, view_date, deleted, edit, jobs, encrypt,
         files):
    """AniDB client for adding files to mylist."""
    client = anidb.Client()
    try:
        if encrypt:
            client.encrypt(encrypt, username)
        response = client.auth(username, password)
        if response.code == 201:
            click.secho('New version available', bold=True)
    except exceptions.SocketTimeout:
        click.secho('AniDB API server is unavailable', fg='red', err=True)
        raise click.Abort
    except exceptions.AnidbError as e:
        click.secho(str(e), fg='red', err=True)
        raise click.Abort

    if watched and not view_date:
        view_date = AnidbDate.now()

    if view_date:
        watched = True

    mp_pool = multiprocessing.Pool(jobs)

    file_params = mp_pool.imap(mylistadd_file_params, files)
    for file, file_ed2k, file_size in file_params:
        try:
            result = client.call('MYLISTADD', {
                'ed2k': file_ed2k,
                'size': file_size,
                'state': 3 if deleted else 1,  # 1 = internal storage (hdd)
                'viewed': watched,
                'viewdate': view_date,  # field will be ignored if viewed=0
                'edit': edit,
            })

            if result.code in {210, 310, 311}:
                status = click.style(' OK ', fg='green')
            else:
                status = click.style('FAIL', fg='red')

            click.echo('[{}] {}: {}'.format(status, result.message,
                                            click.format_filename(file)))
        except exceptions.AnidbError as e:
            click.secho(str(e), fg='red', err=True)
            break

    mp_pool.close()
    mp_pool.join()

    client.logout()


if __name__ == '__main__':
    main()
