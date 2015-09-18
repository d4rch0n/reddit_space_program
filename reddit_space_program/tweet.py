#!/usr/bin/env python
import os
import sys
import json
import twitter

from reddit_space_program import config, TEST_PHASE

def connect():
    if TEST_PHASE:
        return True
    return twitter.Api(**config.twitter)

def tweet(conn, msg):
    if len(msg) > 140:
        raise RuntimeError('Message is too long ({})'.format(len(msg)))
    if TEST_PHASE:
        print('Tweet: {}'.format(msg))
    else:
        conn.PostUpdate(msg)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('tweet')
    args = parser.parse_args()
    conn = connect()
    tweet(conn, args.tweet)

if __name__ == '__main__':
    main()
