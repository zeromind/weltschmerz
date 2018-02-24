#!/usr/bin/python3

import os
import db

dbc = db.connection()
hashed_files = dbc.hashed_files()
for filename in hashed_files:
    if not os.path.isfile(filename):
        print('###### deleting {}'.format(filename))
        dbc.del_file_by_name(filename)
dbc.conn.commit()
