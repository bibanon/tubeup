import unittest
import os
import json
from tubeup.utils import sanitize_identifier, check_is_file_empty, strip_ip_from_meta

current_path = os.path.dirname(os.path.realpath(__file__))

def get_testfile_path(name):
    return os.path.join(current_path, 'test_tubeup_files', name)

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

    def test_strip_ip_from_meta(self):
        with open(get_testfile_path(
                'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A.'
                'info.json')
        ) as f:
            vid_meta = json.load(f)
            mod, new_meta = strip_ip_from_meta(vid_meta)
            self.assertTrue(mod)
            self.assertNotEqual(f.read(), json.dumps(new_meta))
            self.assertNotRegex(json.dumps(new_meta), r'36\.73\.93\.234')
