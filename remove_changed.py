#!/usr/bin/python3

import os
import db

dbc = db.Connection()
hashed_files = dbc.hashed_files_size()

for directory, filename, filesize in hashed_files:
    if os.path.isfile(os.path.join(directory, filename)):
        if filesize != os.path.getsize(os.path.join(directory, filename)):
            print('###### filesize mismatch, deleting {}'.format(os.path.join(directory, filename)))
            dbc.del_file_by_name(os.path.join(directory, filename))
dbc.conn.commit()
