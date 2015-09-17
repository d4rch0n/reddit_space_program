#!/usr/bin/env python

from imgurpython import ImgurClient
from reddit_space_program import config

def connect():
    return ImgurClient(**config.imgur)

def upload(conn, path):
    return conn.upload_from_path(path, anon=False)['link']

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    args = parser.parse_args()
    conn = connect()
    link = upload(conn, args.path)
    print(link)

if __name__ == '__main__':
    main()
