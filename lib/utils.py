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


def get_course(link, username, password, start, finish):
    session = login(username, password)

    course = session.get(link)

    soup = BeautifulSoup(course.content, 'html.parser')

    id_course = soup.find(id='course-page').get('data-course-id')
    title_course = slugify(soup.find('h1', class_='default-title').get_text())

    chapters = soup.select('ul.course-toc > li > ul')
    items = soup.find_all('a', class_='video-name')

    len_char_chapters = len(str(len(chapters)))
    len_char_items = len(str(len(items)))

    mkdir(title_course)
    os.chdir(title_course)

    for index, item in enumerate(items, (start - 1)):
        if index == finish:
            break

        chapter = item.find_parent('ul', class_='toc-items')

        item_name = slugify(add_zero(index, len_char_items) + '. ' + item.get_text())
        item_id = item.get('data-ga-value')
        item_chapter = slugify(add_zero(chapters.index(chapter), len_char_chapters) + '. ' + chapter.find_previous('div', class_='chapter-row').find('h4').get_text())

        i = index + 1
        get_item(id_course, item_chapter, item_id, item_name, add_zero(i, len_char_items) + '/' + str(len(items)),
                 session)


def get_item(course_id, directory, item_id, item_name, desc, request):
    prev_directory = os.getcwd()
    mkdir(directory)
    os.chdir(directory)

    item_link = 'http://www.lynda.com/ajax/course/' + course_id + '/' + item_id + '/play'
    sub_link = 'http://www.lynda.com/ajax/player/transcript?courseId=' + course_id + '&videoId=' + item_id

    response = request.get(item_link)
    item_info = (response.json())[1]['urls']

    if '720' in item_info:
        vid_link = item_info['720']
    elif '540' in item_info:
        vid_link = item_info['540']
    elif '360' in item_info:
        vid_link = item_info['360']
    else:
        print('Video is not in the required format')
        sys.exit(1)

    link_dl(vid_link, item_name + '.mp4', desc + ' (vid)')
    link_dl(sub_link, item_name + '.srt', desc + ' (sub)')

    os.chdir(prev_directory)
