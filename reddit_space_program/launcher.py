#!/usr/bin/env python
import sys
import os
import importlib
from yamlcfg import YamlConfig


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mission_dir')
    parser.add_argument('craft_name')
    args = parser.parse_args()
    mission_cfg = YamlConfig(
            path=os.path.join(args.mission_dir, 'config.yml'))
    craft_cfg = YamlConfig(
            path=os.path.join(
                args.mission_dir, 
                'crafts', 
                '{}_config.yml'.format(args.craft_name)))
    print('Launching mission {m.name}\n  by {m.author_name} <{m.author_email}>\n'
        .format(m=mission_cfg))
    print('Description: ' + mission_cfg.description + '\n')
    print('Using craft {c.name}\n  by {c.author_name} <{c.author_email}>\n'
        .format(c=craft_cfg))
    print('Description: ' + craft_cfg.description + '\n')
    sys.path = [args.mission_dir] + sys.path
    mission_mod = importlib.import_module('mission')
    mission_mod.main()

if __name__ == '__main__':
    main()
