#!/usr/bin/env python
''' reddit_space_program test module

Reference:
http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html
'''

import sys
import time
import krpc
from reddit_space_program.tweet import connect as twitter_connect, tweet
try:
    twit_conn = twitter_connect()
except Exception:
    sys.stderr.write('Cant connect to twitter.\n')
    twit_conn = None

def connect2vessel():
    conn = krpc.connect(name='RedditSpaceProgramExample')
    return conn.space_center.active_vessel

def turn(vessel, ang_offset):
    vessel.auto_pilot.target_pitch_and_heading(90 - ang_offset, 90)

def launch():
    vessel = connect2vessel()
    #if twit_conn:
    #   tweet(twit_conn, 'Vessel {vessel.name} is preparing for launch!'.format(vessel=vessel))

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

    # if the code exits, it'll just flip over at this point (no autopilot)
    turn(vessel, 20)
    while True:
        time.sleep(10)
