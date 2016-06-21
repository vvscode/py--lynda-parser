# coding=utf-8
"""" Helper function """
import os
import errno


def mkdir(directory):
    """ Create directory if not exists """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise exc
