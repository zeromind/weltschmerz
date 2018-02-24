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
num_worker_threads = int(config.get('client', 'threads', fallback=4))
logging.basicConfig(filename=logfile, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


# TODO: add absolute path
def get_files(list, hashed_files):
    files = []
    known_files = []
    logging.info('Scanning for files...')
    for path in list:
        logging.info(''.join(('Scanning for files: ', path)))
        for dirpath, dirnames, filenames in os.walk(path):
            for ext in extensions:
                for filename in fnmatch.filter(filenames, ''.join(('*.', ext))):
                    if re.search('\udcd7|\udcb7', filename):
                        logging.warning(''.join(('skipped a file in ', os.path.abspath(dirpath))))
                    else:
                        real_path = os.path.abspath(dirpath)
                        if (real_path, filename) in hashed_files:
                            known_files.append((real_path, filename))
                            continue
                        elif (real_path, filename) in files:
                            continue
                        else:
                            files.append((real_path, filename))
                            qin[path].put((real_path, filename))

    logging.info('{} files to hash found, skipping {} which had been hashed already'.format(len(set(files)), len(set(known_files))))
    return files


def db_connect(name):
    logging.info(''.join(('Establishing database connection (', dbname, ')...')))
    # if os.path.isfile(name):
    #        dbc = db.connection()
    # else:
    #        dbc = db.connection()
    #        dbc.initialise_db()
    dbc = db.connection()
    dbc.initialise_db()
    return dbc


def db_disconnect(dbconnector):
    logging.info(''.join(('Closing database connection (', dbname, ')...')))
    dbconnector.shutdown()


def parser(folder):
    print(folder)
    while True:
        (directory, filename) = qin[folder].get()
        start = time.time()
        fhash = filehash.FileHash(directory, filename)
        end = time.time()
        data = (fhash.filename, fhash.directory, fhash.filesize, fhash.crc32, fhash.md5, fhash.sha1, fhash.ed2k)
        qout.put(data)
        logging.info(''.join(('hashed: ', os.path.join(directory, filename), ' %i MB @' % (fhash.filesize / 1048576.),
                              ' %f MB/s' % (fhash.filesize / 1048576. / (end - start)))))
        qin[folder].task_done()


def sql_worker():
    dbc = db_connect(dbname)
    while True:
        data = qout.get()
        dbc.add_file_hashed(data)
        qout.task_done()
    # db_disconnect(dbc)


if __name__ == "__main__":
    dbc = db_connect(dbname)
    hashed_files = dbc.hashed_files()
    db_disconnect(dbc)
    qin = {}
    for f in folders:
        qin[f] = queue.Queue()

    qout = queue.Queue()
    for f in folders:
        t = threading.Thread(target=parser, kwargs={'folder': f})
        t.daemon = True
        t.start()
    sqlt = threading.Thread(target=sql_worker)
    sqlt.daemon = True
    sqlt.start()
    fcount = get_files(folders, hashed_files)
    for f, q in qin.items():
        q.join()
    qout.join()
    logging.info('hashed: em all')
