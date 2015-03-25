#!/usr/local/bin/python3.4

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

config = configparser.ConfigParser()
config.read_file(open('weltschmerz.cfg'))
extensions = re.split(' ', config.get('client', 'fileextensions'))
dbname = config.get('client', 'database', fallback = 'weltschmerz.sqlite3')
logfile = config.get('client', 'log', fallback='weltschmerz.log')
folders = re.split(' ', config.get('client', 'folders'))
num_worker_threads = int(config.get('client', 'threads', fallback=4))
logging.basicConfig(filename=logfile, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
#TODO: add absolute path
def get_files(list):
        files = []
        logging.info('Scanning for files...')
        for path in list:
                logging.info(''.join(('Scanning for files: ', path)))
                for dirpath, dirnames, filenames in os.walk(path):
                        for ext in extensions:
                                for filename in fnmatch.filter(filenames, ''.join(('*.', ext))):
                                        if re.search('\udcd7|\udcb7', filename):
                                                logging.warning(''.join(('skipped a file in ', os.path.abspath(dirpath))))
                                        else:
                                                files.append(os.path.join(os.path.abspath(dirpath), filename))
        logging.info(''.join((str(len(files)), ' files found')))
        return files

def db_connect(name):
        logging.info(''.join(('Establishing database connection (', dbname, ')...')))
        #if os.path.isfile(name):
        #        dbc = db.connection()
        #else:
        #        dbc = db.connection()
        #        dbc.initialise_db()
        dbc = db.connection()
        dbc.initialise_db()
        return dbc

def db_disconnect(dbconnector):
        logging.info(''.join(('Closing database connection (', dbname, ')...')))
        dbconnector.shutdown()

def parse(folders):
        dbc = db_connect(dbname)
        files = list(set(get_files(folders)).difference(set(dbc.hashed_files())))
        db_disconnect(dbc)
        listlength = len(files)
        logging.info(''.join((str(listlength), ' files to hash')))
        for file in files:
                qin.put(file)
        return listlength

def parser():
    while True:
        filename = qin.get()
        data = filehash.hash_file(filename)
        qout.put(data)
        logging.info(''.join(('hashed: ', filename)))
        qin.task_done()

def sql_worker():
    dbc = db_connect(dbname)
    while True:
        data = qout.get()
        dbc.add_file_hashed(data)
        qout.task_done()
    db_disconnect(dbc)

if __name__ == "__main__":
        qin = queue.Queue()
        qout = queue.Queue()
        fcount = parse(folders)
        if fcount > 0:
            for i in range(num_worker_threads):
                t = threading.Thread(target=parser)
                t.daemon = True
                t.start()
            sqlt = threading.Thread(target=sql_worker)
            sqlt.daemon = True
            sqlt.start()
            qin.join()
            qout.join()
        else:
            logging.info('Nothing to do: exiting...')
