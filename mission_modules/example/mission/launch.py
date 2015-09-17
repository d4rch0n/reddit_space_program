#!/usr/bin/env python
''' reddit_space_program test module

Reference:
http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html
'''

import sys
import time
import krpc
from reddit_space_program.tweet import connect as twitter_connect, tweet
from reddit_space_program.screenshot import connect as imgur_connect, screenshot, upload

twit_conn = None
try:
    twit_conn = twitter_connect()
except Exception:
    sys.stderr.write('Cant connect to twitter.\n')

img_conn = None
try:
    img_conn = imgur_connect()
except Exception:
    sys.stderr.write('Cant connect to imgur.\n')


def connect2vessel():
    conn = krpc.connect(name='RedditSpaceProgramExample')
    return conn.space_center.active_vessel

def turn(vessel, ang_offset):
    vessel.auto_pilot.target_pitch_and_heading(90 - ang_offset, 90)

def launch():
    vessel = connect2vessel()
    if img_conn:
        img_path1 = screenshot()
        link1 = upload(img_conn, img_path1)
        print('Uploaded image to {}'.format(link1))       
    if twit_conn and img_conn:
        tweet(twit_conn, 'Vessel {vessel.name} is preparing for launch!\n{link}'.format(vessel=vessel, link=link1))
        print('Tweeted!')

    vessel.control.throttle = 1
    vessel.control.sas = True

    # Launch!
    vessel.control.activate_next_stage()
    vessel.auto_pilot.engage()
    turn(vessel, 0)
    time.sleep(30)
    turn(vessel, 5)
    vessel.control.activate_next_stage()
    vessel.control.activate_next_stage()
    if img_conn:
        img_path2 = screenshot()
        link2 = upload(img_conn, img_path2)
        print('Uploaded image to {}'.format(link2))
    if twit_conn and img_conn:
        tweet(twit_conn, 'Vessel {vessel.name} is staging!\n{link}'.format(vessel=vessel, link=link2))
        print('Tweeted!')

    # if the code exits, it'll just flip over at this point (no autopilot)
    turn(vessel, 20)
    while True:
        time.sleep(10)
