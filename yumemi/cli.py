import multiprocessing
import os
import re
import time

import click

import yumemi
from . import anidb
from . import exceptions
from . import ed2k


class AnidbDate(click.ParamType):
    """
    AniDB Date parameter.

    Converts local time to server (UTC) time.
    """

    name = 'anidb_date'

    FROM_STR_DATE = (
        (re.compile(r'^(?P<dt>\d{4}-\d{2}-\d{2})$'),
         '%Y-%m-%d'),
        (re.compile(r'^(?P<dt>\d{4}-\d{2}-\d{2} \d{2}:\d{2})$'),
         '%Y-%m-%d %H:%M'),
        (re.compile(r'^(?P<dt>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$'),
         '%Y-%m-%d %H:%M:%S'),
        (re.compile(r'^(?P<rel>y) (?P<dt>\d{2}:\d{2})$'),
         '%H:%M'),
        (re.compile(r'^(?P<rel>-\d+)d? (?P<dt>\d{2}:\d{2})$'),
         '%H:%M'),
    )

    @classmethod
    def from_str(cls, date_time, _format=None):
        """Create timestamp from string."""
        if date_time == 'now':
            return int(time.time())
        elif _format:
            return int(time.mktime(time.strptime(date_time, _format)))
        for cre, fmt in cls.FROM_STR_DATE:
            match = cre.match(date_time)
            if match:
                groups = match.groupdict()
                if 'rel' not in groups:
                    return cls.from_str(groups['dt'], fmt)
                # Relative date.
                today_fmt = '%Y-%m-%d '
                today = time.strftime(today_fmt)
                timestamp = cls.from_str(today + groups['dt'], today_fmt + fmt)
                rel_days = -1 if groups['rel'] == 'y' else int(groups['rel'])
                return timestamp + rel_days * 24 * 60 * 60
        return None

    def convert(self, value, param, ctx):
        if not value:
            return 0
        date = self.from_str(value)
        if date is None:
            self.fail('Invalid value')
        return date


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


@click.command()
@click.version_option(version=yumemi.__version__)
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
              ' Formats: Y-m-d[ H:M[:S]] | y H:M (yesterday) | -#[d] H:M '
              '(before # days).')
@click.option('-d', '--deleted', is_flag=True, default=False,
              help='Set file state to deleted.')
@click.option('-e', '--edit', is_flag=True, default=False,
              help='Set edit flag to true.')
@click.option('-j', '--jobs', type=int, default=None, envvar='JOBS',
              help='Number of adding processes. Default is CPU count.')
@click.argument('files', nargs=-1, required=True,
                type=click.Path(exists=True, dir_okay=False))
def cli(username, password, watched, view_date, deleted, edit, jobs, encrypt,
        files):
    """AniDB client for adding files to mylist."""
    client = anidb.Client()
    try:
        if encrypt:
            client.encrypt(encrypt, username)
        response = client.auth(username, password)
        if response.code == 201:
            click.echo('New version available')
    except exceptions.AnidbError as e:
        click.echo('ERROR: {}'.format(str(e)), err=True)
        return

    if watched and not view_date:
        view_date = AnidbDate.from_str('now')

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
                'viewed': int(watched),
                'viewdate': view_date,  # field will be ignored if viewed=0
                'edit': int(edit),
            })

            if result.code in {210, 310, 311}:
                status = click.style(' OK ', fg='green')
            else:
                status = click.style('FAIL', fg='red')

            click.echo('[{}] {}: {}'.format(status, result.message,
                                            click.format_filename(file)))
        except exceptions.AnidbError as e:
            click.echo('ERROR: {}'.format(str(e)), err=True)
            break

    mp_pool.close()
    mp_pool.join()

    client.logout()


def main():
    # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
    cli(help_option_names=['-h', '--help'],
        auto_envvar_prefix='YUMEMI')


if __name__ == '__main__':
    main()
