from yumemi.ed2k import *


def test_parse_ed2k_link():
    assert parse_ed2k_link(
        'ed2k://|file|01 - Where You Belong - [HorribleSubs](cf74da2b).mkv'
        '|229550436|88c7b6e493e653b3e14fae43a8712327|/'
    ) == (
        '01 - Where You Belong - [HorribleSubs](cf74da2b).mkv',
        229550436,
        '88c7b6e493e653b3e14fae43a8712327',
    )
    # without leading slash
    assert parse_ed2k_link(
        'ed2k://|file|02 - I Can`t Stand Magic - [HorribleSubs](690e6be0).mkv'
        '|160644878|8c3801a73b81b9f24a57b686b465374b|'
    ) == (
        '02 - I Can`t Stand Magic - [HorribleSubs](690e6be0).mkv',
        160644878,
        '8c3801a73b81b9f24a57b686b465374b',
    )
