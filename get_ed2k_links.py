#!/usr/bin/python3

import sys
import db
import os

dbc = db.Connection()

directories = sys.argv[1:]
for directory in directories:
    for link in dbc.get_ed2k_links(os.path.realpath(os.path.abspath(directory))):
        print(link)
