reddit_space_program
====================

Community driven realtime KSP missions!

Installation
------------

From the project root directory:

    $ python setup.py install

To create a ship module, create a directory and initialize a project inside
with a `README.txt`, a `config.yml`, a `mission/` directory with your mission module, a `crafts/` directory with your testing crafts, each having a`name.craft` file and a `name_config.yml`.

The config will be loaded as a vessel config for the code.

Example mission module layout:

    myProject/
        README.txt
        config.yml
        mission/
            __init__.py # has main() func
            foo.py
            bar.py
        crafts/
            test.craft
            test_config.yml
            myship.craft
            myship_config.yml

The ships config.yml can have any variables you want, but define these at the root:

    name: foo
    description: foo is a craft!
    author_name: d4rch0n
    author_email: d4rch0n@gmail.com
    <whatever else>

The root config.yml should also have the same, but tailored for the mission.

See mission_modules/example for the example layout and example code.

Usage
-----

Simply run it:

    $ rsp-launch $path_to_mission_module $name_of_craft

Use --help/-h to view info on the arguments:

    $ rsp-launch --help

Release Notes
-------------

0.0.1: Project created
