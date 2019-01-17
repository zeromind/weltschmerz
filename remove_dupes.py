#!/usr/bin/python3

import os
import db
import pyselect
import sys
import filehash
import difflib
import datetime

dbc = db.Connection()
dupes = dbc.get_dupes()
total_dupes = len(dupes)

for i, (hash_sha1, files) in enumerate(dupes.items(), start=1):
    filenames = sorted([os.path.join(dupe[0], dupe[1]) for dupe in files])
    selection = None
    while not selection:
        print("\n" * 8 + '#' * 128 + "\n")
        print('[ {current:05} / {total:05} ]'.format(current=i, total=total_dupes))
        print('Files to keep:')
        file_names = list(set([filename[1] for filename in files]))
        if len(file_names) == 1:
            selection = filenames[0]
            print('File to keep:')
            print(selection)
        else:
            sys.stdout.writelines(difflib.context_diff(file_names[0], file_names[1], fromfile='a', tofile='b'))
            print()
            # break
            selection = pyselect.select(filenames)
    if not selection:
        continue
    if os.path.isfile(selection):
        if filehash.FileHash(os.path.split(selection)[0], os.path.split(selection)[1]).hash_file()[2] == hash_sha1:
            print('sha1 matches: setting atime/mtime to oldest and removing dupes')
            filenames.remove(selection)
            for f in filenames:
                if os.path.isfile(f):
                    mtime = os.path.getmtime(f)
                    if os.path.getmtime(selection) > mtime:
                        print('setting atime/mtime to {mtime}'.format(mtime=datetime.datetime.fromtimestamp(mtime).isoformat()))
                        os.utime(selection, (mtime, mtime))
                    print('deleting: {}'.format(f))
                    os.remove(f)
                    dbc.del_dupe(hash_sha1, os.path.split(f)[0], os.path.split(f)[1])
                dbc.conn.commit()
        else:
            filenames.remove(selection)
            print('removing file with sha1 mismatch from db: {}'.format(selection))
            dbc.del_dupe(hash_sha1, os.path.split(selection)[0], os.path.split(selection)[1])
            dbc.conn.commit()
