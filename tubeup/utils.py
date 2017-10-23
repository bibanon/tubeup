import os


EMPTY_ANNOTATION_FILE = ('<?xml version="1.0" encoding="UTF-8" ?>'
                         '<document><annotations></annotations></document>')


def check_is_file_empty(filepath):
    """
    Check whether file is empty or not.

    :param filepath:  Path of a file that will be checked.
    :return:          True if the file empty.
    """
    return os.path.exists(filepath) and os.stat(filepath).st_size == 0


class LogErrorToStdout(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
