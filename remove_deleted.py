#usr/bin/python3

import os
import db
import pyselect
import sys
import pprint
import filehash

dbc = db.connection()
hashed_files = dbc.hashed_files()
pp = pprint.PrettyPrinter(width=240)
for filename in hashed_files:
    pp.pprint(filename)
    if not os.path.isfile(filename):
        pp.pprint('###### deleting {}'.format(filename))
        dbc.del_file_by_name(filename)
#        dbc.conn.commit()
dbc.conn.commit()
    #sys.exit(0)
    
     
