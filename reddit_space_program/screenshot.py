#!/usr/bin/env python

import os
import time
import re
from subprocess import call, Popen, PIPE, CalledProcessError
import shlex
from uuid import uuid1

from imgurpython import ImgurClient

from reddit_space_program import config, TEST_PHASE

screenshot_dir = config.screenshot_dir or os.path.expanduser('~/kerbal_screenshots')
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

RE_WINDOW = re.compile(r'xwininfo: Window id: (\S+) "Kerbal Space Program"')

WINDOW = None

def connect():
    if TEST_PHASE:
        return True
    return ImgurClient(**config.imgur)

def get_kspwin():
    global WINDOW
    if WINDOW is not None:
        return WINDOW
    out, err = Popen(shlex.split(
        'xwininfo -name "Kerbal Space Program"'), 
        stdout=PIPE, stderr=PIPE).communicate()
    if err:
        return None
    if not out:
        return None
    lines = out.splitlines()
    if len(lines) < 2:
        raise RuntimeError('Unexpected output from xwininfo (less than 2 lines): {}'.format(out))
    window_line = lines[1]
    match = RE_WINDOW.match(window_line)
    if not match:
        raise RuntimeError('Unexpected output from xwininfo (doesn\'t match regex): {}'.format(out))
    WINDOW = match.group(1)
    return WINDOW
        
def screenshot():
    window = get_kspwin()
    path = os.path.join(screenshot_dir, str(uuid1()) + '.jpg')
    call(shlex.split('import -window {} {}'.format(window, path)))
    return path

def record(output=None, cap_time=5):
    window = get_kspwin()
    if output is None:
        output = str(uuid1())
    prog1 = Popen(shlex.split(
        'recordmydesktop -o {} --windowid {} --no-sound'.format(
            output, window
        )), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    time.sleep(cap_time)
    os.kill(prog1.pid, 2)
    while True:
        try:
            os.kill(prog1.pid, 0)
        except OSError:
            break
        else:
            prog1.communicate('\n')
            time.sleep(0.1)
    inp_fname = output + '.ogv'
    out_path = os.path.join(screenshot_dir, output + '.mp4')
    prog2 = Popen(shlex.split(
        'avconv -i {} {}'.format(
            inp_fname,
            out_path,
        )), stdout=PIPE, stderr=PIPE)
    while not os.path.exists(out_path):
        time.sleep(0.1)
    os.remove(inp_fname)
    return out_path

def upload(conn, path):
    if TEST_PHASE:
        return path
    return conn.upload_from_path(path, anon=False)['link']

def main():
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    if get_kspwin() is None:
        raise RuntimeError('Please launch Kerbal Space Program')
    conn = connect()
    path = screenshot()
    link = upload(conn, path)
    print('Dumped to {}'.format(path))
    print('Link: {}'.format(link))

if __name__ == '__main__':
    main()
