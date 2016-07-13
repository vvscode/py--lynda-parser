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


def login(username, password):
    session = requests.Session()

    first_request = session.get('https://www.lynda.com/signin')

    if 200 != first_request.status_code:
        return login(username, password)

    token = re.search(r'name="-_-"\s+value="(.*)"', first_request.text)
    token = token.group(1)

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'www.lynda.com',
        'Referer': 'https://www.lynda.com/signin/password',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
        'X-Requested-With': 'XMLHttpRequest',
        '-_-': token
    }

    payload = {
        'email': username,
        '-_-': token,
        'password': password,
        'remember': 'on'
    }

    second_request = session.post('https://www.lynda.com/ajax/signin/user', data=payload, headers=headers)

    response = second_request.json()

    if 'RedirectUrl' in response and 'HasErrors' in response:
        if not response['HasErrors']:
            session.get('https://www.lynda.com' + response['RedirectUrl'])
            print('Starting...')
            return session
        else:
            print(response['ErrorMessage'])
            sys.exit(1)
    else:
        print(response)
        sys.exit(1)
