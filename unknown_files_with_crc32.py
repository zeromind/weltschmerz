#!/usr/bin/python3

import anime
import configparser
import argparse
import re
from typing import Dict, List

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
    parser.add_argument('--single-crc32-match-only', help='print only files with matching crc32 in filename',
                        default=False, action='store_true')
    parser.add_argument('--print-path', help='print path of files with matching crc32 in filename (default is ed2k link)',
                        default=False, action='store_true')
                        

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    unknown_files: List[anime.LocalFile]
    if config.folder:
      unknown_files = dbs.session.query(anime.LocalFile).outerjoin(anime.File, anime.LocalFile.hash_ed2k==anime.File.hash_ed2k).filter(anime.File.hash_ed2k == None, anime.LocalFile.directory == config.folder.rstrip('/')).order_by(anime.LocalFile.directory, anime.LocalFile.filename).all()
      if config.single_crc32_match_only:
        unknown_files = [ unknown_file for unknown_file in unknown_files if unknown_file.hash_crc in unknown_file.filename.casefold() and not re.match(r'.*/by-id/\d\d/\d\d/\d\d', unknown_file.directory) ]
      if config.print_path:
        for unknown_file in unknown_files:
          print(unknown_file.filename)
      else:
        for unknown_file in unknown_files:
            print(unknown_file.ed2k_link)
    else:
      unknown_files = dbs.session.query(anime.LocalFile).outerjoin(anime.File, anime.LocalFile.hash_ed2k==anime.File.hash_ed2k).filter(anime.File.hash_ed2k == None).order_by(anime.LocalFile.directory, anime.LocalFile.filename).all()
      folders: Dict[str, int]= {}
      for local_file in unknown_files:
        if local_file.hash_crc in local_file.filename.casefold() and not re.match(r'.*/by-id/\d\d/\d\d/\d\d', local_file.directory):
          if local_file.directory not in folders.keys():
            folders[local_file.directory] = 0
          folders[local_file.directory] += 1

      folders = dict(sorted(folders.items(), key=lambda item: item[1], reverse=True))
      for folder, filecount in folders.items():
        if filecount >= 100:
          print(f'{folder}: {filecount}')
        else:
          break
