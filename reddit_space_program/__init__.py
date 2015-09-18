''' reddit_space_program

Community driven realtime KSP missions!
'''
from yamlcfg import YamlConfig
__version__ = '0.0.1'

import os

config = YamlConfig(name='reddit_space_program')
TEST_PHASE = os.getenv('TEST_PHASE')

def main():
    pass

if __name__ == '__main__':
    main()
