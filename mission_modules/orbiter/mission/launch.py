#!/usr/bin/env python
''' reddit_space_program Orbiter

Reference:
http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html
'''

import os
import sys
import time
import krpc
from reddit_space_program.tweet import connect as twitter_connect, tweet
from reddit_space_program.screenshot import connect as imgur_connect, screenshot, upload
from tinylog import Logger

log = Logger(debug='orbiter_debug.log', console='stdout')

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

def connect2vessel(craft_cfg):
    conn = krpc.connect(name='RSP-Orbiter')
    vessel = conn.space_center.active_vessel
    stages = [
            vessel.resources_in_decouple_stage(stage=x, cumulative=False)
            for x in range(0, craft_cfg.num_stages)
        ]
    data = {
        'ut': conn.add_stream(getattr, conn.space_center, 'ut'),
        'alt': conn.add_stream(getattr, vessel.flight(), 'mean_altitude'),
        'apo': conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude'),
        'peri': conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude'),
        'ecc': conn.add_stream(getattr, vessel.orbit, 'eccentricity'),
        'liquid': [
            conn.add_stream(stages[i].amount, 'LiquidFuel')
            for i in range(0, craft_cfg.num_stages)
        ][::-1],
        'solid': [
            conn.add_stream(stages[i].amount, 'SolidFuel')
            for i in range(0, craft_cfg.num_stages)
        ][::-1],
    }
    return vessel, data

def turn(vessel, ang_offset):
    vessel.auto_pilot.target_pitch_and_heading(90 - ang_offset, 90)

def shot_tweet(msg):
    if img_conn:
        img_path1 = screenshot()
        link1 = upload(img_conn, img_path1)
    if twit_conn and img_conn:
        tweet(twit_conn, msg + '\n' + link1)

def maintain(vessel, mv, **kwargs):
    limits = {}
    for kwarg, val in kwargs.items():
        if not kwarg.endswith('_limit'):
            limits[kwarg] = [val]
    for kwarg in limits:
        limits[kwarg] += [kwargs[kwarg]]
    while True:
        vel = vessel.flight(vessel.orbit.body.reference_frame).velocity
        vvel = vel[-1] * -1
        if vvel > mv:
            vessel.control.throttle *= 0.9
        if vvel < mv:
            vessel.control.throttle *= 1.1
        for kwarg, vals in limits.items():
            func, limit = vals
            log.debug('{}: {}'.format(kwarg, func()))
            if func() > limit:
                log.info('{} reached limit'.format(kwarg))
                break


def stage1(vessel, data):
    # Launch!
    # http://wiki.kerbalspaceprogram.com/wiki/Tutorial:_How_to_Get_into_Orbit
    vessel.control.activate_next_stage()
    vessel.auto_pilot.engage()
    turn(vessel, 0)
    time.sleep(1)
    shot_tweet('We have liftoff!')
    while True:
        vel = vessel.flight(vessel.orbit.body.reference_frame).velocity
        vvel = vel[-1] * -1
        log.debug('velocity: {}, {}, {}'.format(*vel))
        if vvel > 100.0:
            break
        time.sleep(0.1)
    turn(vessel, 5)
    time.sleep(1)
    shot_tweet('Beginning to turn to 10deg east at 100 m/s vertical velocity')
    maintain(vessel, 300, apo=data['apo'], apo_limit=80000, alt=data['alt'], alt_limit=25000)
    turn(vessel, 15)
    maintain(vessel, 500, apo=data['apo'], apo_limit=80000, alt=data['alt'], alt_limit=35000)
    maintain(vessel, 1000, fuel=data['liquid'][0], fuel_limit=0.1, apo=data['apo'], apo_limit=80000)
    if data['apo'] > 78000:
        shot_tweet('...burning to the horizon!')
        turn(vessel, 80)
        maintain(vessel, 1000, fuel=data['liquid'][0], fuel_limit=0.1)
    else:
        turn(vessel, 60)
        shot_tweet('out of fuel... will this work??')

def stage2(vessel, data):
    peri0 = data['peri']()
    apo0 = data['apo']()
    vessel.control.activate_next_stage()
    shot_tweet('Were on our final stage! Wish us luck!')
    maintain(vessel, 1000, fuel=data['liquid'][1], fuel_limit=0.1, apo=data['peri'], peri_limit=79000)

def launch(mission_cfg, craft_cfg):
    vessel, data = connect2vessel(craft_cfg)
    shot_tweet('{vessel.name} is preparing for launch!'.format(vessel=vessel))
    vessel.control.throttle = 1

    stage1(vessel, data)
    stage2(vessel, data)
    vessel.control.activate_next_stage()
    if data['apo']() > 70000 and data['peri']() > 70000:

        shot_tweet('Satellite deployed... Apo: {}, Peri: {}\nlooks like we\'re in orbit!'.format(data['apo'](), data['peri']()))
    else:
        shot_tweet('Satellite deployed... but according to apo and peri, it\'s not in orbit :(')
