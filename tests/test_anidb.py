import unittest
import unittest.mock

from yumemi.anidb import *


class SocketTestCase(unittest.TestCase):
    @unittest.mock.patch('yumemi.anidb.socket.socket')
    def test_init(self, *args):
        s = Socket(('localhost', 1234), 4321)
        s._socket.bind.assert_called_once_with(('0.0.0.0', 4321))
        s._socket.settimeout.assert_called_once_with(4)

    @unittest.mock.patch('yumemi.anidb.socket.socket')
    def test_send_recv(self, *args):
        s = Socket(('localhost', 1234), 4321)
        s._socket.recv.return_value = b'Hello World'
        data = s.send_recv(b'Hello World')
        s._socket.sendto.assert_called_with(b'Hello World', ('localhost', 1234))
        self.assertEqual(data, b'Hello World')


class ClientSocketTestCase(unittest.TestCase):
    @unittest.mock.patch('yumemi.anidb.socket.socket')
    def test_init(self, *args):
        c = Client()
        self.assertEqual(c._socket.server, Client.SERVER)
        c._socket._socket.bind.assert_called_once_with(('0.0.0.0', Client.LOCALPORT))
        c._socket._socket.settimeout.assert_called_once_with(4)

    @unittest.mock.patch('yumemi.anidb.socket.socket')
    def test_init_none(self, *args):
        c = Client(None, None, None)
        self.assertEqual(c._socket.server, Client.SERVER)
        c._socket._socket.bind.assert_called_once_with(('0.0.0.0', Client.LOCALPORT))
        c._socket._socket.settimeout.assert_called_once_with(4)

    @unittest.mock.patch('yumemi.anidb.socket.socket')
    def test_send_recv(self, *args):
        c = Client()
        c._socket._socket.recv.return_value = b'200 OK'
        resp = c.call('PING')
        c._socket._socket.sendto.assert_called_with(b'PING', Client.SERVER)

    @unittest.mock.patch('yumemi.anidb.socket.socket')
    def test_send_recv_none(self, *args):
        c = Client(None, None, None)
        c._socket._socket.recv.return_value = b'200 OK'
        resp = c.call('PING')
        c._socket._socket.sendto.assert_called_with(b'PING', Client.SERVER)


class ClientCallTestCase(unittest.TestCase):
    @unittest.mock.patch('yumemi.anidb.Socket')
    def test_empty_data(self, *args):
        c = Client()
        c._socket.send_recv.return_value = b'200 OK'
        resp = c.call('PING', {'key': 'value'})
        c._socket.send_recv.assert_called_with(b'PING key=value')
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.message, 'OK')
        self.assertFalse(resp.data)

    @unittest.mock.patch('yumemi.anidb.Socket')
    def test_single_data(self, *args):
        c = Client()
        c._socket.send_recv.return_value = b'200 OK\nA|B|C'
        resp = c.call('PING', {'key': 'value'})
        c._socket.send_recv.assert_called_with(b'PING key=value')
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.message, 'OK')
        self.assertListEqual(resp.data, [['A', 'B', 'C']])

    @unittest.mock.patch('yumemi.anidb.Socket')
    def test_multi_data(self, *args):
        c = Client()
        c._socket.send_recv.return_value = b'200 OK\nA|B|C\nX|Y|Z'
        resp = c.call('PING', {'key': 'value'})
        c._socket.send_recv.assert_called_with(b'PING key=value')
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.message, 'OK')
        self.assertListEqual(resp.data, [['A', 'B', 'C'],
                                         ['X', 'Y', 'Z']])

    @unittest.mock.patch('yumemi.anidb.Socket')
    def test_escape(self, *args):
        c = Client()
        c._socket.send_recv.return_value = b'200 OK'
        resp = c.call('PING', {'key': 'line\n&'})
        c._socket.send_recv.assert_called_with(b'PING key=line<br />&amp;')

    @unittest.mock.patch('yumemi.anidb.Socket')
    def test_unescape(self, *args):
        c = Client()
        c._socket.send_recv.return_value = b'200 OK\nmulti<br />line|pi/pe|`apo`'
        resp = c.call('PING')
        self.assertListEqual(resp.data, [['multi\nline', 'pi|pe', "'apo'"]])


class ClientTestCase(unittest.TestCase):
    @unittest.mock.patch('yumemi.anidb.Socket')
    @unittest.mock.patch.object(Client, 'call')
    def test_ping(self, *args):
        c = Client()

        c.call.return_value = Response(300, 'PONG')
        pong = c.ping()
        c.call.assert_called_with('PING')
        self.assertTrue(pong)

        c.call.return_value = Response(500, 'SOME ERROR')
        pong = c.ping()
        c.call.assert_called_with('PING')
        self.assertFalse(pong)

    @unittest.mock.patch('yumemi.anidb.Socket')
    @unittest.mock.patch.object(Client, 'call')
    def test_auth_logout(self, *args):
        c = Client()

        c.call.return_value = Response(200, 'sess LOGIN ACCEPTED')

        resp = c.auth('user', 'pass')

        # First item is list of positional arguments
        call_command, call_params = c.call.call_args[0]

        self.assertEqual(call_command, 'AUTH')

        for param in ('user', 'pass', 'protover', 'client', 'clientver'):
            self.assertIn(param, call_params)

        self.assertEqual(call_params['user'], 'user')
        self.assertEqual(call_params['pass'], 'pass')

        self.assertTrue(c.is_logged_in())
        self.assertEqual(c._session, 'sess')

        c.call.return_value = Response(203, 'LOGGED OUT')

        resp = c.logout()

        # First item is list of positional arguments
        call_command = c.call.call_args[0][0]

        self.assertEqual(call_command, 'LOGOUT')
        self.assertFalse(c.is_logged_in())
        self.assertIsNone(c._session)

    @unittest.mock.patch('yumemi.anidb.Socket')
    @unittest.mock.patch.object(Client, 'call')
    def test_encoding(self, *args):
        c = Client()

        c.call.return_value = Response(200, 'sess LOGIN ACCEPTED')
        c.auth('user', 'pass')

        c.call.return_value = Response(219, 'ENCODING CHANGED')
        c.encoding('UTF-8')

        self.assertEqual(c._codec.encoding, 'UTF-8')

        c.call.return_value = Response(203, 'LOGGED OUT')
        c.logout()

        # Encoding should be reset to default after logout
        self.assertEqual(c._codec.encoding, Client.ENCODING)
