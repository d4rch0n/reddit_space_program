#!/usr/bin/env python
''' reddit_space_program Orbiter Mk2

Reference:
http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html
https://www.reddit.com/r/KerbalAcademy/comments/3lmc75/most_efficient_launch_profile_to_reach_orbit
'''

import os
import sys
import time
import krpc
from reddit_space_program.tweet import connect as twitter_connect, tweet
from reddit_space_program.screenshot import connect as imgur_connect, screenshot, upload
from tinylog import Logger

log = Logger(info='orbiter_debug.log', console='stdout')
#log = Logger(debug='orbiter_debug.log', console='stdout')

twit_conn = twitter_connect()
img_conn = imgur_connect()

conn, rframe, vessel, stream = None, None, None, None
stage = 0

def init_globals(craft_cfg):
    global conn, rframe, vessel, stream
    conn = krpc.connect(name='RSP-OrbiterMk2')
    vessel = conn.space_center.active_vessel
    stages = [
            vessel.resources_in_decouple_stage(stage=x, cumulative=False)
            for x in range(0, craft_cfg.num_stages)
        ]
    rframe = vessel.orbit.body.reference_frame
    stream = {
        'time': conn.add_stream(getattr, conn.space_center, 'ut'),
        'alt': conn.add_stream(getattr, vessel.flight(rframe), 'surface_altitude'),
        'speed': conn.add_stream(getattr, vessel.flight(rframe), 'speed'),
        'vspeed': conn.add_stream(getattr, vessel.flight(rframe), 'vertical_speed'),
        'hspeed': conn.add_stream(getattr, vessel.flight(rframe), 'horizontal_speed'),
        'termv': conn.add_stream(getattr, vessel.flight(rframe), 'terminal_velocity'),
        'apo': conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude'),
        'apotime': conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis'),
        'peri': conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude'),
        'peritime': conn.add_stream(getattr, vessel.orbit, 'time_to_periapsis'),
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
    vessel.auto_pilot.engage()
    vessel.auto_pilot.sas = True
    #vessel.auto_pilot.reference_frame = rframe

def throttle(t=None):
    if t is None:
        return vessel.control.throttle
    vessel.control.throttle = min(max(t, 0.0), 1.0)

def shot_tweet(msg):
    if img_conn:
        img_path1 = screenshot()
        link1 = upload(img_conn, img_path1)
    if twit_conn and img_conn:
        tweet(twit_conn, msg + '\n' + link1)

def maintain(turn_f=None, throttle_f=None, **kwargs):
    limits = {}
    for kwarg, func in kwargs.items():
        if not kwarg.endswith('_min') and not kwarg.endswith('_max'):
            limits[kwarg] = [func]
    for kwarg in limits:
        limits[kwarg] += [(kwargs.get(kwarg + '_min'), kwargs.get(kwarg + '_max'))]
    while True:
        if turn_f is not None:
            turn_f()
        if throttle_f is not None:
            throttle_f()
        done = False
        for kwarg, vals in limits.items():
            func, lminmax = vals
            lmin, lmax = lminmax
            if lmin is not None and func() < lmin:
                log.info('{} reached minimum ({})'.format(kwarg, lmin))
                done = True
                break
            if lmax is not None and func() > lmax:
                log.info('{} reached maximum ({})'.format(kwarg, lmax))
                done = True
                break
        if done:
            break

def turn(ang_offset):
    vessel.auto_pilot.target_pitch_and_heading(90 - ang_offset, 90)

def spacebar():
    global stage
    stage += 1
    vessel.control.activate_next_stage()

def static_angle(val):
    def angle0():
        turn(val)
    return angle0

def launch(mission_cfg, craft_cfg):
    init_globals(craft_cfg)
    shot_tweet('{vessel.name} is preparing for launch!'.format(vessel=vessel))
    throttle(1)
    vessel.control.activate_next_stage()    
    # Burn until you hit 100 m/s
    maintain(turn_f=static_angle(0), vel=stream['vspeed'], vel_max=100)
    # start to tip
    init_alt = stream['alt']()
    alt_max = 50000
    diff = float(alt_max - init_alt)
    turn_max = 90
    def turn_f():
        # Get ratio of altitude from initial state to alt_max,
        # and slowly turn to 45 at that time
        ratio = (stream['alt']() - init_alt) / diff
        turn(turn_max * ratio)
    def throttle_f():
        # keep throttle below terminal velocity
        spd = stream['speed']()
        tvel = stream['termv']()
        if spd < tvel:
            throttle(throttle() * 1.005)
        else:
            throttle(throttle() * 0.999)
        if stream['liquid'][stage]() < 0.01:
            spacebar()
    maintain(turn_f=turn_f, throttle_f=throttle_f,
        alt=stream['alt'], alt_max=alt_max)
    # Now we're at `alt_max` and `turn_max` degrees AoA
    throttle(1)
    print('Burn until apo at 75000')
    def throttle_f():
        if stream['liquid'][stage]() < 0.01:
            spacebar()
    maintain(turn_f=static_angle(90), throttle_f=throttle_f,
        apo=stream['apo'], apo_max=75000)
    print('Circularize')
    def throttle_f():
        if stream['liquid'][stage]() < 0.01:
            spacebar()
        apotime = stream['apotime']()
        if apotime > 1:
            throttle(0)
        else:
            throttle(0.5)
    maintain(turn_f=static_angle(90), throttle_f=throttle_f,
        peri=stream['peri'], peri_max=75000)
    throttle(0)
    print('Orbiting!')
