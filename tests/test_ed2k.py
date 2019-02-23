import unittest

from yumemi.ed2k import *


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
