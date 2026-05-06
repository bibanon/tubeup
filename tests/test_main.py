import docopt

import tubeup.__main__ as cli


def test_proxy_short_option_sets_proxy():
    args = docopt.docopt(
        cli.__doc__,
        argv=['-x', 'socks5://localhost:9050', 'https://example.com/watch?v=abc123'])

    assert args['--proxy'] == 'socks5://localhost:9050'


def test_password_short_option_sets_password():
    args = docopt.docopt(
        cli.__doc__,
        argv=['-p', 'secret', 'https://example.com/watch?v=abc123'])

    assert args['--password'] == 'secret'
    assert args['--proxy'] is None
