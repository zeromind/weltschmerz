#!/usr/bin/python3

import anime
import configparser
import argparse


def get_config(config_file: str = 'weltschmerz.cfg'):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description='Print ed2k links for specified folder(s).')
    parser.add_argument('--database', help='database to use',
                        default=config.get('client', 'database'))
    parser.add_argument('--folders', nargs='*', help='folders to process', default='/')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    for folder in config.folders:
        known_files = dbs.session.query(anime.LocalFile).filter(anime.LocalFile.directory.like(f'{folder.rstrip("/")}%')).all()
        for known_file in known_files:
            print(known_file.ed2k_link)
