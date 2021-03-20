#!/usr/bin/python3

import anime
import logging
import configparser
import argparse

def get_config(config_file='weltschmerz.cfg'):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description='Return unknown files from the database.')
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
      unknown_files = dbs.session.query(anime.LocalFile).outerjoin(anime.File, anime.LocalFile.hash_ed2k==anime.File.hash_ed2k).filter(anime.File.hash_ed2k == None, anime.LocalFile.directory == config.folder.rstrip('/')).order_by(anime.LocalFile.directory, anime.LocalFile.filename).all()
      [ print(unknown_file.ed2k_link()) for unknown_file in unknown_files]
    else:
      unknown_files = dbs.session.query(anime.LocalFile).outerjoin(anime.File, anime.LocalFile.hash_ed2k==anime.File.hash_ed2k).filter(anime.File.hash_ed2k == None).order_by(anime.LocalFile.directory, anime.LocalFile.filename).all()
      folders = {}
      for local_file in unknown_files:
        if local_file.hash_crc in local_file.filename.casefold():
          if local_file.directory not in folders.keys():
            folders[local_file.directory] = 0
          folders[local_file.directory] += 1

      folders = dict(sorted(folders.items(), key=lambda item: item[1], reverse=True))
      for folder, filecount in folders.items():
        if filecount >= 100:
          print(f'{folder}: {filecount}')
        else:
          break
