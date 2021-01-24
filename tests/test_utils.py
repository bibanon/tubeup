import unittest
import os
from tubeup.utils import sanitize_identifier, check_is_file_empty


class UtilsTest(unittest.TestCase):

    def test_preserve_valid_identifiers(self):
        valid = [
            'youtube--QBwhSklJks',
            'youtube-_--M04_mN-M',
            'youtube-Xy2jZABDB40'
        ]
        clean = [sanitize_identifier(x) for x in valid]
        self.assertListEqual(valid, clean)

    def test_sanitize_bad_identifiers(self):
        bad = [
            'twitch:vod-v181464551',
            'twitch:clips-1003820974',
            'twitter:card-1192732384065708032'
        ]
        expect = [
            'twitch-vod-v181464551',
            'twitch-clips-1003820974',
            'twitter-card-1192732384065708032'
        ]
        clean = [sanitize_identifier(x) for x in bad]
        self.assertListEqual(expect, clean)

    def test_check_is_file_empty_when_file_is_empty(self):
        # Create a file for the test
        with open('testemptyfile.txt', 'w'):
            pass

        self.assertTrue(check_is_file_empty('testemptyfile.txt'))
        os.remove('testemptyfile.txt')

    def test_check_is_file_empty_when_file_is_not_empty(self):
        with open('testfilenotempty.txt', 'w') as not_empty_file:
            not_empty_file.write('just a text')

        self.assertFalse(check_is_file_empty('testfilenotempty.txt'))
        os.remove('testfilenotempty.txt')

    def test_check_is_file_empty_when_file_doesnt_exist(self):
        with self.assertRaisesRegex(
                FileNotFoundError,
                r"^Path 'file_that_doesnt_exist.txt' doesn't exist$"):
            check_is_file_empty('file_that_doesnt_exist.txt')
