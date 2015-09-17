#!/usr/bin/env python

import os
from subprocess import call
import shlex
from uuid import uuid1

from imgurpython import ImgurClient

from reddit_space_program import config

screenshot_dir = config.screenshot_dir or os.path.expanduser('~/kerbal_screenshots')
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

def connect():
    return ImgurClient(**config.imgur)

def screenshot(window):
    path = os.path.join(screenshot_dir, str(uuid1()) + '.jpg')
    call(shlex.split('import -window {} {}'.format(window, path)))
    return path

def upload(conn, path):
    return conn.upload_from_path(path, anon=False)['link']

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--window', '-w', default=config.window)
    args = parser.parse_args()
    conn = connect()
    path = screenshot(args.window)
    link = upload(conn, path)
    print('Dumped to {}'.format(path))
    print('Link: {}'.format(link))

if __name__ == '__main__':
    main()
