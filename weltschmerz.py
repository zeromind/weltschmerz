#!/usr/bin/python3

import configparser
import db
import fnmatch
import filehash
import logging
import os.path
import re
import sys
import threading
import queue
import argparse
import time

config = configparser.ConfigParser()
config.read_file(open('weltschmerz.cfg'))
extensions = re.split(' ', config.get('client', 'fileextensions'))
dbname = config.get('client', 'database', fallback='weltschmerz.sqlite3')
logfile = config.get('client', 'log', fallback='weltschmerz.log')
folders = re.split(' ', config.get('client', 'folders'))
folders_exclude = re.split(' ', config.get('client', 'folders_exclude'))
num_worker_threads = int(config.get('client', 'threads', fallback=4))
logging.basicConfig(filename=logfile, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_files(folders, hashed_files):
    files = []
    known_files = []
    for path in folders:
        logging.info(''.join(('Scanning for files: ', path)))
        for dirpath, dirnames, filenames in os.walk(path):
            for ext in extensions:
                for filename in fnmatch.filter(filenames, ''.join(('*.', ext))):
                    if re.search('[\udcd7\udcb7]', filename):
                        logging.warning(''.join(('skipped a file in ', os.path.abspath(dirpath))))
                    else:
                        real_path = os.path.realpath(os.path.abspath(dirpath))
                        for excluded_folder in folders_exclude:
                            if real_path.startswith(excluded_folder):
                                print('skipping {}'.format(os.path.join(real_path, filename)))
                                break
                        else:
                            if (real_path, filename) in hashed_files:
                                known_files.append((real_path, filename))
                                continue
                            elif (real_path, filename) in files:
                                continue
                            else:
                                files.append((real_path, filename))
                                qin[path].put((real_path, filename))

    logging.info('{} files to hash for {}. skipping {} which had been hashed already'.format(len(set(files)),
                                                                                             ','.join(folders),
                                                                                             len(set(known_files))
                                                                                             )
                 )
    return files


def db_connect(name):
    logging.info('Establishing database connection ({db})...'.format(db=name))
    db_connection = db.Connection()
    db_connection.initialise_db()
    return db_connection


def parser(folder):
    while True:
        (directory, filename) = qin[folder].get()
        start = time.time()
        fhash = filehash.FileHash(directory, filename)
        end = time.time()
        data = (fhash.filename, fhash.directory, fhash.filesize, fhash.crc32, fhash.md5, fhash.sha1, fhash.ed2k)
        qout.put(data)
        logging.info('hashed: {file} {size}MB @ {speed}MB/s'.format(file=os.path.join(directory, filename),
                                                                    size=(fhash.filesize / 1048576.),
                                                                    speed=(fhash.filesize / 1048576. / (end - start))))
        qin[folder].task_done()


def sql_worker():
    dbc = db_connect(dbname)
    while True:
        data = qout.get()
        dbc.add_file_hashed(data)
        qout.task_done()


if __name__ == "__main__":
    dbc = db_connect(dbname)
    hashed_files = dbc.hashed_files()
    logging.info('Closing database connection ({db})...'.format(db=dbname))
    dbc.shutdown()
    qin = {}
    qout = queue.Queue()
    fi = {}
    for f in folders:
        qin[f] = queue.Queue()

        fi[f] = threading.Thread(target=get_files, kwargs={'folders': [f], 'hashed_files': hashed_files})
        fi[f].daemon = True
        fi[f].start()

        t = threading.Thread(target=parser, kwargs={'folder': f})
        t.daemon = True
        t.start()

    sqlt = threading.Thread(target=sql_worker)
    sqlt.daemon = True
    sqlt.start()

    for i, walk_thread in fi.items():
        walk_thread.join()
    for f, q in qin.items():
        q.join()
    qout.join()
    logging.info('hashed: em all')
