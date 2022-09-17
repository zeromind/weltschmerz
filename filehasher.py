#!/usr/bin/python3

import anime
import filehash
import os
import re
import configparser
import argparse
import logging
from typing import List, Tuple


def get_config(config_file='weltschmerz.cfg'):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description='Hash files and add info to database.')
    parser.add_argument('--database', help='database to use',
                        default=config.get('client', 'database'))
    parser.add_argument('--log-file', dest='log_file', help='logfile to use',
                        default=config.get('client', 'log'))
    parser.add_argument('--folders', nargs='*', help='folders to process',
                        default=re.split('\s+', config.get('client', 'folders', fallback='')))
    parser.add_argument('--folders-exclude', dest='folders_exclude', nargs='*', help='folders to exclude',
                        default=re.split('\s+', config.get('client', 'folders_exclude')))
    parser.add_argument('--foldernames-exclude', dest='foldernames_exclude', nargs='*', help='foldernames to exclude',
                        default=re.split('\s+', config.get('client', 'foldernames_exclude')))
    parser.add_argument('--extensions', nargs='*', help='folders to process',
                        default=re.split('\s+', config.get('client', 'fileextensions')))

    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file,
                        format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    return args


class FileHasher():
    def __init__(self, db='sqlite:///:memory:', echo=False):
        self.dbs = anime.DatabaseSession(db, echo)
        self.files = []

    def get_files(self, folders, folders_exclude, foldernames_exclude, exts):
        files = []
        for path in folders:
            logging.info(''.join(('Scanning for files: ', path)))
            for dirpath, dirnames, filenames in os.walk(path, topdown=True):
                dirnames[:] = [d for d in dirnames if not (os.path.join(dirpath, d).startswith(tuple(folders_exclude)) or d in foldernames_exclude or not d.encode('utf-8', errors='replace'))]
                filenames[:] = [f for f in filenames if f.casefold().endswith(tuple(exts)) and f.encode('utf-8', errors='replace')]
                print('{}: {}'.format(dirpath.encode('utf-8', errors='replace').decode('utf-8'), len(set(filenames))))
                for filename in filenames:
                    real_path = os.path.realpath(os.path.abspath(dirpath))
                    try:
                        os.path.join(real_path, filename).encode('utf-8')
                    except UnicodeEncodeError as e:
                        logging.warning(f'Skipping a file: {e}')
                        continue
                    if self.dbs.session.query(anime.LocalFile).filter_by(filename=filename, directory=real_path).first():
                        print(f'skipping {os.path.join(real_path, filename)}')
                        continue
                    elif (real_path, filename) in files:
                        continue
                    elif os.path.islink(os.path.join(real_path, filename)):
                        continue
                    else:
                        print(f'found {os.path.join(real_path, filename)}')
                        files.append((real_path, filename))

        return files


if __name__ == "__main__":
    config = get_config()
    hasher = FileHasher(config.database, False)
    files: List[Tuple[str, str]] = hasher.get_files(config.folders, config.folders_exclude, config.foldernames_exclude, config.extensions)
    print(len(files))
    for directory, filename in files:
        fhash = filehash.FileHash(directory, filename)
        lf = anime.LocalFile(filename=fhash.filename, directory=fhash.directory, filesize=fhash.filesize,
                             hash_crc=fhash.crc32, hash_md5=fhash.md5, hash_sha1=fhash.sha1, hash_ed2k=fhash.ed2k)
        print(f'{lf.filename}: {lf.hash_crc}')
        hasher.dbs.session.merge(lf)
        hasher.dbs.session.commit()
