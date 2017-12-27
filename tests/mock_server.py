import logging
import socketserver
import urllib.parse
import random

logger = logging.getLogger(__name__)


class UDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        logger.debug('client: %s', self.client_address)

        data = self.request[0].decode('utf-8')

        cmd, urlargs = data.split(maxsplit=1) if data.count(' ') else (data, '')
        cmd = cmd.strip().lower()
        args = {k.strip(): v.strip() for k, v in urllib.parse.parse_qsl(urlargs)}

        response = None

        if cmd not in {'ping', 'encoding', 'auth', 'version', 'encrypt'}:
            # All other commands requires session.
            if not args['s']:
                response = '506 INVALID SESSION\n'
            if not args['s'] == 'sessid':
                response = '502 ACCESS DENIED\n'

        if not response:
            if hasattr(self, 'cmd_' + cmd):
                response = getattr(self, 'cmd_' + cmd)(args)
            else:
                response = '598 UNKNOWN COMMAND\n'

        logger.info('data: %s', (cmd.upper(), args))
        logger.info('response: %s', response)

        try:
            if response:
                self.request[1].sendto(response.encode('utf-8'),
                                       self.client_address)
        except Exception as e:
            logger.info(e)

    def cmd_ping(self, args):
        return '300 PONG\n'

    def cmd_auth(self, args):
        if args['user'] == args['pass']:
            return '200 sessid LOGIN ACCEPTED\nlocalhost'
        else:
            return '500 LOGIN FAILED\n'

    def cmd_logout(self, args):
        return '203 LOGGED OUT\n'

    def cmd_mylistadd(self, args):
        if not ((args.get('fid')) or (args.get('size') and args.get('ed2k'))
                or (args.get('lid') and str(args.get('edit')) == '1')):
            return '505 ILLEGAL INPUT OR ACCESS DENIED\n'
        return '210 MYLIST ENTRY ADDED\n%d' % random.randint(1, 10**9)

    def cmd_vote(self, args):
        return '260 VOTED\nAnime|{}|{}|{}'.format(args['value'], args['type'], args['id'])


def main(port=9000):
    try:
        server = socketserver.UDPServer(('127.0.0.1', port), UDPHandler, False)
        server.allow_reuse_address = True
        server.server_bind()
        server.server_activate()
        logger.info('server: start @ port %d', port)
        server.serve_forever()

    except KeyboardInterrupt:
        logger.info('server: bye')

    except Exception as e:
        logger.critical(e)


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
        level=logging.DEBUG)
    main()
