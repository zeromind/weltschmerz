#!/usr/bin/python3

import anime
import os.path
import logging
import configparser
import argparse


def get_config(config_file='weltschmerz.cfg'):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description='Hash files and add info to database.')
    parser.add_argument('--database', help='database to use',
                        default=config.get('client', 'database'))
    parser.add_argument('--log-file', dest='log_file', help='logfile to use',
                        default=config.get('client', 'log'))
    parser.add_argument('--folder', help='folder to query',
                        default=None)

    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file,
                        format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    return args


if __name__ == "__main__":
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    if config.folder:
        known_files = dbs.session.query(anime.LocalFile).filter(anime.LocalFile.directory.like(f'{config.folder.rstrip("/")}%')).all()
    else:
        known_files = dbs.session.query(anime.LocalFile).all()

    print(len(known_files))
    for known_file in known_files:
        if not os.path.isfile(known_file.full_path()):
            print(f'###### removing {known_file.full_path()}')
            dbs.session.delete(known_file)
        else:
            print(f'###### found {known_file.full_path()}')
    dbs.session.commit()
