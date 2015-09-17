#!/usr/bin/env python
import os
import sys
import json
import twitter

from reddit_space_program import config

def connect():
    return twitter.Api(**config.twitter)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('tweet')
    args = parser.parse_args()
    conn = connect()
    conn.PostUpdate(args.tweet)

if __name__ == '__main__':
    main()
