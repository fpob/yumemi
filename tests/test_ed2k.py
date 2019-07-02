import unittest
import tempfile

from yumemi.ed2k import file_ed2k, parse_ed2k_link


class FileEd2kTestCase(unittest.TestCase):
    DATA = [
        # data, ed2k_hash
        ('0' * 1024,
         'cc8987d3db399feec0a28a74cbc350d5'),
        ('0' * 9728000,   # chunk_size
         'd8a24bd5137c60e610e414189e8445dc'),
        ('0' * 19456000,  # chunk_size * 2
         'b148215d3d6dc00ab6952b43abde6976'),
        ('0' * 19457024,  # chunk_size * 2 + 1024
         '54c5c3580fcb33a55c4b913986b2708e'),
    ]

    def test_file_ed2k(self):
        for data, ed2k_hash in self.DATA:
            with self.subTest(ed2k_hash):
                with tempfile.NamedTemporaryFile(mode='w') as tmp:
                    tmp.write(data)
                    tmp.flush()

                    self.assertEqual(file_ed2k(tmp.name), ed2k_hash)


class ParseEd2kLinkTestCase(unittest.TestCase):
    def test_parse(self):
        parsed = parse_ed2k_link(
            'ed2k://|file|01 - Where You Belong - [HorribleSubs](cf74da2b).mkv'
            '|229550436|88c7b6e493e653b3e14fae43a8712327|/'
        )
        expected = (
            '01 - Where You Belong - [HorribleSubs](cf74da2b).mkv',
            229550436,
            '88c7b6e493e653b3e14fae43a8712327',
        )
        self.assertEqual(parsed, expected)

        # without leading slash
        parsed = parse_ed2k_link(
            'ed2k://|file|02 - I Can`t Stand Magic - [HorribleSubs](690e6be0).mkv'
            '|160644878|8c3801a73b81b9f24a57b686b465374b|'
        )
        expected = (
            '02 - I Can`t Stand Magic - [HorribleSubs](690e6be0).mkv',
            160644878,
            '8c3801a73b81b9f24a57b686b465374b',
        )
        self.assertEqual(parsed, expected)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            # there should be 'file' instead of '<ivalid>'
            parse_ed2k_link('ed2k://|<invalid>|foo|123|abc|/')
        with self.assertRaises(ValueError):
            # invalid hash
            parse_ed2k_link('ed2k://|file|foo|123|xyz|/')
        with self.assertRaises(ValueError):
            # size is not a number
            parse_ed2k_link('ed2k://|file|foo|xyz|abc|/')
