#!/usr/bin/python3

import sys
import db

dbc = db.Connection()

directories = sys.argv[1:]
for directory in directories:
    for link in dbc.get_ed2k_links(directory):
        print(link)