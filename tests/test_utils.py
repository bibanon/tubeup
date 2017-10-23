import unittest
import os
from tubeup.utils import check_is_file_empty


class UtilsTest(unittest.TestCase):

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
