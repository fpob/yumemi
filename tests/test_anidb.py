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


class CodecTestCase(unittest.TestCase):
    DATA = [
        (b'200 12345 LOGIN ACCEPTED\n',
         '200 12345 LOGIN ACCEPTED\n'),
        (b'230 ANIME\n1|4087,7493,7501,7503,7514,7516,21911,21958,40209,49519,28,4081,4079,4080,4082,4083,4084,4085,4086,4088,7512,21943,21944,21945,21946,21947,21948,21949,21954\n',
         '230 ANIME\n1|4087,7493,7501,7503,7514,7516,21911,21958,40209,49519,28,4081,4079,4080,4082,4083,4084,4085,4086,4088,7512,21943,21944,21945,21946,21947,21948,21949,21954\n'),
        # Compressed data
        (b'\x00\x00x\x9c%\x941\xa2$7\x08D\xf3=\xc5\x1e`\x82AH\x02\x85\x0e\x1c8\xb0O\xe4\xc3\xef{\xfc\x80\xean($(\xa9Y\xf9\xfd\xfd\xd7\x7f\xff\xfc\xfb\xf7\xaf\xd3\xfb\xffx\xf7\x13\xaf\xb0\xfe\xac\xef\x17\x0b,\xb1\x8b\x15\xf6>+\xf0\x07\xfeX\xd8\xc6\x0eF<\x88\x07y\x8b\xef\xc53\xf9N\xf8\x9b\xe7\x81\x7f\xe0^\x9e\x97\xf8\xc5w\xe1\\\xe2\xec\xb7\xd8/\xd9g\x97V\x9f\xdd_,\xb0\x85\xe1\xeb\x8d\x1d\xecb\xef\xb3\x1f\xbe\xc7\xf7{\x9f\x8b\x15u\xd6\xd2\x16\x96\xd8\xc6\x0ev\xb1\xc2\x1a\x83\x97_\x0c^\xc2Kx\t/\xe1%<j\xadM|\xe3\xdb|Sw\x1d\xbe\x0f<j\xaf\x03\xef\xe0?\xfaY\xef\xc0\xbf\xc4\xe9\xa9.\xeb]x\x17\x1e\xfd\xd5\x85G\x8fE\x8fE\x8fU\xf0\n^\xc1+8\x05\xa7\xe0\xd0k\x15\x9c\x82C\xcfE\xcfE\xcfE\xcfE\xcfE\xcfE\xcf\xd5\xf0\x1a\x1e\xbd\xd7\x83\xf7\xe0=x\x0f\x0e:\x14\xe7V\xe8X\xe8X\xe8\xd1\x9c]\xa3I\x7f\x17\x96\xd8\xc6\x0ev\xb1\xc2\x1a\x83\xc7Y6g\xd9\x9ce\x07<\xce\xb39\xcf\xe6<\x9b\xf3l\xce\xb3\x17\x1ctmtmt\xed\xc3\xfb\xf1\t\x0f=\x1a=\x1a=\x9a\xfe\x9a\xfe\xba5\xb8\xd4\xdf\xd4\xd4\xd4\xd4\xd4\xf4\xa8\xe9Q\xd3\xa3\x9e\x87N\x0f\x9d\x1e:\xc5\x97M\x81y+\xa1\x85\x07\xb03\x10\xc2\x12R\x90\xcc\xd1\x02f,3\x96\x19\xcb\x8c4#\xcdH3\xd2\x8c4#\xcdH3RrJ\xde\x92\xb7\xe4-yK\xde\x92\xb7\xe4k\xf4\xce\x9bi\xd7\x8c\xd6\xc7\x99Dp1\x80\x10\x96\x90\xc2\x16&z\x85\x12\xd8-\xb8!\xe1\x15\x07X%\x11!\xbc\xed\xc0\x16\x8eP\x02\x94\xe4H\x00)\x1c\n /\xa4\xc4D]@]R]RIRIRIRIRIRIRIR5R5R\rR\r2\xa5l\xdf\xf6\xbcI\xde\x92m+m!m!m!m!\x8fQ%I\x9b\xc9\xebz\xd7}U(U(\xaf\xe4+Y\xad\xb2$\x97\xe4\x92\\VZf\x94\x19eFI.\xc9\n\x9b-\xb9\xe5\xb5<u\xce\x96\xf7\xf4=}O\xdf\x1b\x9f\xbb\xa9i\xaa\xe9\xe6r\x01!,!\x85-\x1c\xe1\ndl\xd5\xdd\xaa\xbbUw[\xe9\xe6\xc7\x8a\xfd\x0c\xb8\x87s\x050\xc3=\xf6\x9b(\xbc\xe3\x1e\xc7\xa38^\xa9\x93\xf3v\x85\x12\xe0]\xfe\xd3pX\x84\xd3"\x1c\x17\xe1\xbc\x08\x87E8-\xc2q\x11\xce\x0bf\xeb\x0cX&\xe2&\x00\xcc\xdb\x12R\xd8\x9f\xbb\xd6\xc0\x11\xaePB\x0b\x0c\xbe\xc5m\x07BXB\n\xfe\xc1\x8f\xf9\xd0\xb3\xb6\xb8\x06sp\x0f\x9e\xc1+\xae\xe1\xcc\xff\xfd\x9d?\xdc?L\x1c\xce\xfa\xe1\xd4\xe0\xcc\x026\x06s\xa29\xd1\x9c\xe8\x1d\xcf\x1d\xcf\xd5\x13\xe3\x8f\xbb\x07\xcf\xe0\x8f\xc7u\xc2I\x01N\xb4&Z\xe6F\x0f\xa7\xe5\xac\xa9yM\xb5k\xaa]\xf1\xe3\xb7\x86\xf53\x97\xa6\xfe5\xf5\xaf\xa9s\xd5\xf8k\xfc\xb3\xcb\xaaYg\xf6Z5+\x8c>\xeb\xcdTs~-/8xcp\xfcS\xad\x17\xfa\xdd\xa4*\x10>\x93\xeb\xfb\x833\xc5\xbe{\xf0\x0c\xde\xc1\'r\xb4b\xfc\xfa\x03PE',
         '230 ANIME\n584|196,197,198,200,201,203,206,207,209,210,211,212,214,215,216,217,218,225,228,237,239,247,251,254,261,265,267,268,269,297,298,303,473,477,480,481,482,483,484,485,486,489,493,495,499,699,701,721,722,723,724,725,726,727,728,729,730,731,732,733,734,735,736,739,740,744,746,747,750,753,754,755,756,757,758,759,760,761,762,763,764,765,766,767,768,769,770,771,772,774,775,776,777,778,779,780,781,782,783,784,785,786,787,788,789,790,791,792,794,795,796,797,798,799,800,801,802,803,804,805,806,807,808,809,810,811,812,813,814,815,816,817,818,820,822,823,824,852,854,855,856,857,858,871,872,882,883,884,897,898,899,900,901,903,964,965,966,1014,1016,1017,1018,1019,1020,1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,1036,1038,1039,1040,1041,1042,1043,1044,1045,1060,1065,1066,1069,1080,1085,1150,1151,1152,1153,1154,1155,1156,1157,1158,1161,1298,1299,1301,1303,1304,1305,1307,1308,1310,1311,1312,1313,1315,1318,1319,1320,1321,1323,1324,1325,1326,1327,1328,1329,1331,1332,1335,1336,1337,1346,1347,1348,1349,1350,1355,1356,1357,1358,1359,1360,1361,1362,1364,1365,1366,1367,1368,1369,1370,1371,1372,1373,1374,1375,1376,1378,1379,1380,1381,1383,1384,1385,1386,1393,1394,1395,1396,1397,1398,1399,1400,1401,1402,1403,1404,1405,1406,1407,1410,1411,1412,1469,1488,1490,1494,1495,1496,1497,1498,1499,1500,1515,1534,1535,1536,1537,1538,1687,1754,1755,1756,1757,1759,1760,1761,1762,2010,2011,2460,2461,2462,2463,2464,6224,6225,6226,6227,6228,6229,6230,6231,6232,6233,6234,81991,82011,82012,82013,82014,82015,82016,82021,82022,82023,82024,82025,82026,82027,82028,82029,82035,82036,82037,82065,82066,82067,82137,82164,82165,82167,82168,82172,82174,82175,82176,82187,82188,82213,82215,82216,82218,82219,82220,82221,82222,82227,82270,82271,82272,82273,82274,82278,82291,82292,82357,82359,82361,82362,82367,82368,96387,96392,96402,96403,96404,96405,96406,96409,96410,96411\n'),
        (b'\x00\x00x\x9c\x1d\x95;v\x1c1\x0c\x04s\x9dB\x07\xd8`\xf0\x07B\x07\x0e\x1c\xd8\'\xf2\xe1\xd55\x01\xea\xed\x0e\xba\xa1a\x93Ky<\xdf\xbf\xfe\xfd\xf9\xfb\xfb\xab\xef\x7f\x9e\x7f\xf2R\xd5\xaaQ\xed\xa7\x9eGe*W\x85*U\xa5j\xd5\xa8\xeeS&\x8dIc\xd2\x984\xa6\xbe\xa9o\xea\x9bf\x984.\x8dK\xe3\xd2\xb84\xae9.\x9dK\xe7\xf3\xe9\x0cU\xaaJ\xd5*\x9e\xad\xea>]\xa6r\x954\xa5~\xa9_\xea\x97\xfa\xa5~\xab\xdf\xea\x8f\xfc\xa3\xde>*=[=[\xbeK\xbb\xd2\xae\xb4\xa7\x9e\xd6\xd9\xa7YZk\x9f\xe6i\xbd\xad\xf5\xb6\xd6;Z\xaf\xb1@\xbbJ\xf0~j0`\xc1\t\xfd\x00\x03\x0eB\x18\x1c\x83cp\x0c\x8e\xc118\x16\x87^\xcb\x1f\xad](\xd0`\xc0\x82\x13\xe2\x01\xe8\xc2\x01\xe2@\x1c\x88\x03q \x0e\xc4\x898\x11\x17\xcf\xf4jn\x88\r\x9d\xa13t\x86\xce\xd0\xad^H\xd0\xb3\xd5\x0b\t<SPB\x80\x04\x05\x1a\x0c\xc0\xb18\x0e\xc7\xe18\x1c\x87\xe3\xe8\x9e\xba\xa7c"$(\xd0@\xdd\xd3\xf9\x10\x1c\x04@bt\xfd\x85\xfe\xc6\xf1\xa6\xc7\x9b\x1e/y\x898\x11\'\xe2d\x9eNE<:N\xc2\t:L\x82\x83\x00\t\n\xa0\xd3\xd0 \xd3 \xd3 \xd3 \xd3 S\x01G\xe0\x08\x1c\x81#p\x04\x8e\xc0\x918\x12G\xe2H\x1c\xc5\xd7\xe2k\xbd_\x19P\x0c(\x06\x14\x03\x8a\x01\xc5\x80f@\xe3h\x1c\x8d\xa3q4\x8e\xc6\xd18\x1aG\xe3\x18\x1c\x83cp\x0c\x8e\xc118\x06\xc7\xe0\x18\x1c\x83cq,\x8e\xc5\xb18\x16\xc7\xe2X\x1c\x8bcqh\x07\xc3\x14\xbb0`\x01\xcf\xf4\xd3\x14\x0c8\x08\x90\xa0\x00\x0e\xe24\xe24\xe24\x924\x924\x924\x92\xe4\xd4\t\x88I\x92\xa3\x17\x1c\xbd\xe0\xe8\x05GO\xc0A\x92\x968\x12\x07\xbbj\x89#q\x90\xae\x91\xae\x91\xae\x91\xae\x91\xae\x91\xae\xd5+a(\xe9\x1a\xe9\x1a\xe9\x1a\xe9\x1a\xe9\x1a\xe9\x1a\xe9\x1a\xe9:\xf3\x9cy\xce<g\x9e3\xcf\xeb\xed.\xd0<g\x9e3\xcf\x99\xe7\xccs\xe69\xf3\x9cy\xfe\xcec\xb7\x9c=r\xb6\xc7\xd9\x1e\'g\'b\'b\x9dy\x80\xe4\x18u\xe8\x0e\xdd1\xea\x10\x1f\xa3\x0e\x87~8\x11\xbas\x049\x8at\x8b\xc3ZD\\D\\D\\D\\D\\D\\D\\D\\\x04[L.\x86\x16C\x8b\xa1\xcd\xd0fh\xeb\xea\x16\x02$(\xd0`\xc0\x02\x1c\x86\xc3p\xe8\xb7\x1a\xcb\x89X\x7f?\x05HP@\xde\x8d\x17\xb2-\x1b\xbal\xe8\xb2\xa1\xcb\x86.\x1b\xbal\xe8&\x92z\x00\xf3\x08\x87\x1b$\xb8A\x82\x1bD\xc0\xcb\x12\x96p\x96up\xab\x04\xb7J\x1c\xeb\xe0j\x11\x1c\x04HP\xa0\xc1\x00\xfd\xa3)\xed\xa0\x90\xa0@\x03\x1a\xfam\t\x0e\x02\xd0\x98\xb7\xa1\xffM\xa5\x9fPq\xff\x15\xf7_q{+\xc8\x02\xef\xa7\x01\x0b$>-A0\xe0 \x00\xb6\xc3q8\x0e\xc7\xed\xd7\x0f9l',
         '230 ANIME\n69|492,494,496,497,498,500,501,502,503,504,505,506,507,509,510,511,512,513,515,516,517,518,519,520,521,522,523,524,525,526,527,643,644,645,646,647,648,649,651,652,653,655,656,657,658,659,661,662,674,676,680,681,682,686,687,688,689,690,692,693,694,695,696,697,698,700,1505,1954,1955,1956,1957,1958,1959,1960,1961,1962,1963,1974,1975,1976,1977,1978,1979,1980,1981,2024,2025,2026,2027,2028,2029,2030,2031,2032,2034,2035,2036,2037,2038,2039,2040,2041,2058,2059,2135,2137,2138,2139,2140,2141,2878,2879,2880,2881,2882,2883,2884,2885,2886,2887,2888,2889,2890,2891,2892,2893,2898,2899,2901,2904,2905,2906,2908,2910,2912,2913,2914,2916,2926,2927,2938,2939,2941,2942,2943,2944,2945,2946,3018,3019,3021,3022,3023,3024,3025,3026,3027,3028,3029,3030,3031,3032,3033,3034,3035,3036,3037,3038,3039,3040,3041,3042,3043,3051,3052,3053,3054,3055,3056,3057,3058,3059,3060,3061,3062,3063,3064,3065,3066,3067,3068,3069,3070,3071,3072,3073,3074,3075,3076,3077,3078,3079,3080,3081,3082,3083,3084,3085,3086,3087,3088,3089,3116,3117,3118,3119,3120,3121,3122,3123,3124,3125,3126,3127,3128,3129,3131,3132,3133,3134,3135,3136,3137,3138,3139,3140,3141,3142,3143,3144,3145,3146,3147,3148,3152,3153,3154,3155,3156,3157,3158,3159,3160,3161,3162,3163,3164,3165,3166,3167,3252,3253,3254,3255,3256,3257,3258,3259,3260,3261,3262,3263,3264,3265,3266,3267,3268,3271,3273,3274,3286,3288,3289,3290,3291,3292,3293,3294,3295,3296,3297,3298,3299,3300,3301,3529,3530,3531,3532,3533,3534,3535,3536,3537,3538,3541,3595,3597,3598,3599,3600,3601,3602,3603,3604,3605,3606,3607,3608,3609,3610,3611,3612,3821,3822,3823,3824,3825,3826,3836,3839,3843,3844,3845,3846,3847,3848,3849,3850,3851,3890,3891,3892,3893,3894,3895,3896,3897,3898,3899,3900,3901,3902,3903,3904,3905,3906,3907,3908,5561,5564,5565,5566,5568,5570,5572,5573,5576,5578,5579,5581,5883,5884,5976,5985,5986,5987,5988,5989,5990,5991,5992,5993,5994,5995,5996,5997,5998\n'),
    ]

    def test_decode(self):
        c = Codec('ASCII')
        for i, o in self.DATA:
            with self.subTest(i=i, o=o):
                self.assertEqual(c.decode(i), o)


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
    def test_params_converting(self, *args):
        c = Client()
        c._socket.send_recv.return_value = b'200 OK\n'

        with self.subTest(type=bool):
            c.call('PING', {'key': True})
            c._socket.send_recv.assert_called_with(b'PING key=1')

        with self.subTest(type=None):
            c.call('PING', {'key': None})
            c._socket.send_recv.assert_called_with(b'PING key=')

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
