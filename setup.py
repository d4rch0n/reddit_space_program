import os
from setuptools import setup

# reddit_space_program
# Community driven realtime KSP missions!

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "reddit_space_program",
    version = "0.0.1",
    description = "Community driven realtime KSP missions!",
    author = "d4rch0n",
    author_email = "d4rch0n@gmail.com",
    license = "GPLv3+",
    keywords = "",
    url = "https://www.bitbucket.org/d4rch0n/reddit_space_program",
    packages=['reddit_space_program'],
    package_dir={'reddit_space_program': 'reddit_space_program'},
    long_description=read('README.rst'),
    classifiers=[
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    install_requires=[
        # protobuf 3.0.0 alpha breaks with a weird symbol_database error
        'protobuf==2.6.1',
        # Remote procedure call for kerbal space program
        'krpc',
    ],
    entry_points = {
        'console_scripts': [
            'rsp = reddit_space_program:main',
            'rsp-tweet = reddit_space_program.tweet:main',
        ],
    },
    #package_data = {
        #'reddit_space_program': ['catalog/*.edb'],
    #},
    #include_package_data = True,
)
