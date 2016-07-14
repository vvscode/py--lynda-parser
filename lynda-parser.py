# coding=utf-8
# compatibility modules
# from __future__ import unicode_literals
# from __future__ import print_function
from builtins import input

# standard modules
# import os
# import re
import sys
import getpass
import argparse


from lib import utils


def main():
    parser = argparse.ArgumentParser(description='Free Downloader (Lynda.com)', prog='lyndacom-dl')

    parser.add_argument('link', help='link', default=None, action='store')
    parser.add_argument('-u', '--username', help='email', default=None, action='store')
    parser.add_argument('-p', '--password', help='password', default=None, action='store')
    parser.add_argument('-s', '--start', help='Start at <int> (default=1)', default=1, action='store')
    parser.add_argument('-f', '--finish', help='Finish at <int>', default=None, action='store')
    parser.add_argument('-v', '--version', help='version', action='version', version='%(prog)s 1.0')

    args = vars(parser.parse_args())

    if not args['username']:
        args['username'] = input("Email: ")

    if not args['password']:
        args['password'] = getpass.getpass(prompt='Password: ')

    utils.get_course(args['link'], args['username'], args['password'], args['start'], args['finish'])

    print('Success!')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
