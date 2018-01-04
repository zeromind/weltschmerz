#usr/bin/python3

import os
import db
import pyselect
import sys
import pprint
import filehash

dbc = db.connection()
dupes = dbc.get_dupes()
print(len(dupes))
sys.exit(0)
pp = pprint.PrettyPrinter(width=240)
for hash_sha1, files in dupes.items():
    selection = None
    while not selection:
        print('')
        print('')
        print('')
        print('')
        print('')
        print('')
        print('#' * 128)
        print('')
        print('File to keep:')
        if len(set([os.path.split(file)[1] for file in files])) == 1:
            selection = files[0]
            print('File to keep:')
            print(selection)
        else:
            #pp.pprint(files)
            #break
            selection = pyselect.select(sorted(files))
    if not selection:
        continue
    if os.path.isfile(selection):
        if filehash.FileHash(selection).hash_file()[2] == hash_sha1:
            print('sha1 matches, removing dupes')
            files.remove(selection)
            for f in files:
                if os.path.isfile(f):
                    print('removing: {}'.format(f))
                    os.remove(f)
                dbc.del_dupe(hash_sha1, f)
                dbc.conn.commit()
#    sys.exit(0)

