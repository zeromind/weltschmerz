#!/usr/bin/python3

import os
import db
import configparser
import re

config = configparser.ConfigParser()
config.read_file(open('weltschmerz.cfg'))
folders_exclude = re.split(' ', config.get('client', 'folders_exclude'))

dbc = db.Connection()
hashed_files = dbc.hashed_files()

for directory, filename in hashed_files:
    for excluded_folder in folders_exclude:
        if directory.startswith(excluded_folder):
            print('###### removing excluded {}'.format(os.path.join(directory, filename)))
            dbc.del_file_by_name(directory, filename)
            continue
    else:
        if not os.path.isfile(os.path.join(directory, filename)):
            print('###### removing {}'.format(os.path.join(directory, filename)))
            dbc.del_file_by_name(directory, filename)
dbc.conn.commit()
