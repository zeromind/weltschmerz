#!/usr/bin/python3

import os
import db

dbc = db.Connection()
hashed_files = dbc.hashed_files()

for directory, filename in hashed_files:
    if not os.path.isfile(os.path.join(directory, filename)):
        print('###### deleting {}'.format(os.path.join(directory, filename)))
        dbc.del_file_by_name(directory, filename)
dbc.conn.commit()
