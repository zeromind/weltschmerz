#!/usr/bin/python3

import os
import db

dbc = db.Connection()
hashed_files = dbc.hashed_files_size()

for filename, filesize in hashed_files:
    if os.path.isfile(filename):
        if filesize != os.path.getsize(filename):
            print('###### filesize mismatch, deleting {}'.format(filename))
            dbc.del_file_by_name(filename)
dbc.conn.commit()
