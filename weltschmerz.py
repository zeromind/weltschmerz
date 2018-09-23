#!/usr/bin/python3

import configparser
import db
import fnmatch
import filehash
import logging
import os.path
import re
import threading
import queue
import argparse
import time

config = configparser.ConfigParser()
config.read_file(open('weltschmerz.cfg'))
dbname = config.get('client', 'database', fallback='weltschmerz.sqlite3')
logfile = config.get('client', 'log', fallback='weltschmerz.log')
folders_exclude = re.split(' ', config.get('client', 'folders_exclude'))
logging.basicConfig(filename=logfile, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--folders', nargs='*', help='folders to process',
                    default=re.split(' ', config.get('client', 'folders')))
parser.add_argument('--folders-exclude', nargs='*', help='folders to exclude',
                    default=re.split(' ', config.get('client', 'folders_exclude')))
parser.add_argument('--extensions', nargs='*', help='folders to process',
                    default=re.split(' ', config.get('client', 'fileextensions')))

args = parser.parse_args()


def get_files(folders, hashed_files, exts):
    files = []
    known_files = []
    for path in folders:
        logging.info(''.join(('Scanning for files: ', path)))
        for dirpath, dirnames, filenames in os.walk(path):
            try:
                dirpath.encode('utf-8')
            except UnicodeEncodeError as e:
                logging.warning('Skipping a folder in {folder}: {e}'.format(folder=os.path.dirname(dirpath), e=e))
                continue
            for ext in exts:
                for filename in fnmatch.filter(filenames, ''.join(('*.', ext))):
                    try:
                        filename.encode('utf-8')
                    except UnicodeEncodeError as e:
                        logging.warning('Skipping a file in {folder}: {e}'.format(folder=os.path.abspath(dirpath), e=e))
                        continue
                    real_path = os.path.realpath(os.path.abspath(dirpath))
                    for excluded_folder in folders_exclude:
                        if real_path.startswith(excluded_folder):
                            logging.debug('Skipping {}'.format(os.path.join(real_path, filename)))
                            break
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
        logging.info('Hashed: {file} {size}MB @ {speed}MB/s'.format(file=os.path.join(directory, filename),
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
    print(args.folders)
    dbc = db_connect(dbname)
    hashed_files = dbc.hashed_files()
    logging.info('Closing database connection ({db})...'.format(db=dbname))
    dbc.shutdown()
    qin = {}
    qout = queue.Queue()
    fi = {}
    for f in args.folders:
        qin[f] = queue.Queue()

        fi[f] = threading.Thread(target=get_files, kwargs={'folders': [f],
                                                           'hashed_files': hashed_files,
                                                           'exts': args.extensions})
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
    logging.info('Hashed: em all')
