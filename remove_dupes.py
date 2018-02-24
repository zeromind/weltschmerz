#!/usr/bin/python3

import os
import db
import pyselect
import sys
import pprint
import filehash

dbc = db.connection()
dupes = dbc.get_dupes()
total_dupes = len(dupes)
pp = pprint.PrettyPrinter(width=240)

for i, (hash_sha1, files) in enumerate(dupes.items(), start=1):
    selection = None
    while not selection:
        print("\n" * 8 + '#' * 128 + "\n" + '[ {current:05} / {total:05} ]'.format(current=i,
                                                                                   total=total_dupes) + "\nFiles to keep:\n")
        if len(set([os.path.split(file)[1] for file in files])) == 1:
            selection = files[0]
            print('File to keep:')
            print(selection)
        else:
            # break
            selection = pyselect.select(sorted(files))
    if not selection:
        continue
    if os.path.isfile(selection):
        if filehash.FileHash(selection).hash_file()[2] == hash_sha1:
            print('sha1 matches, removing dupes')
            files.remove(selection)
            for f in files:
                if os.path.isfile(f):
                    print('deleting: {}'.format(f))
                    os.remove(f)
                dbc.del_dupe(hash_sha1, f)
                dbc.conn.commit()
        else:
            files.remove(selection)
            print('removing file with sha1 mismatch from db: {}'.format(selection))
            dbc.del_dupe(hash_sha1, selection)
            dbc.conn.commit()
