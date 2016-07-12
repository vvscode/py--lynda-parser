# coding=utf-8
"""" Helper function """
import os
import errno
import sys


def mkdir(directory):
    """ Create directory if not exists """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise exc


def set_progress(progress, description):
    if progress < 0:
        progress = 0

    if progress >= 1:
        progress = 1

    bar_length = 30
    block_length = int(round(bar_length * progress))
    text = "\r{0} [{1}] {2}%".format(description, ("#" * block_length) + (" " * (bar_length - block_length)), add_zero(int(progress * 100), 3))

    sys.stdout.write(text)
    sys.stdout.flush()


def add_zero(number, length):
    # todo: find correct .format way
    return '0' * (length - len(str(number))) + str(number)


def link_dl(link, filename, desc):
    response = requests.get(link, stream=True)

    with open(filename, 'wb') as file:
        file_size = int(response.headers['Content-Length'])
        file_size_dl = 0
        chunk_size = 8192
        for chunk in response.iter_content(chunk_size):
            file_size_dl += len(chunk)
            file.write(chunk)
            progress = float(file_size_dl) / file_size
            set_progress(progress, desc)

        file.close()
