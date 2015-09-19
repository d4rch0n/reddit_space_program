''' example
'''
__project__ = 'munar_lander'

from reddit_space_program.tweet import connect as twitter_connect
from reddit_space_program.screenshot import connect as imgur_connect

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

from .launch import launch

def main(*args):
    print('Launching the orbiter')
    launch(*args)
