#!/usr/bin/python3

import os.path
import shutil
import pathlib
import anime
import configparser
import argparse
import sys


AID_PAD_WIDTH = 6
AID_CHUNK_SIZE = 2



def get_config(config_file:str = 'weltschmerz.cfg'):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description='Move screenshots to target directory.')
    parser.add_argument('--database', help='database to use',
                        default=config.get('client', 'database'))
    parser.add_argument('--source-basedir', help='source folder to process',
                        default=None, dest='source_basedir')
    parser.add_argument('--target-basedir', help='target basedir to move files to',
                        default=None, dest='target_basedir')
    parser.add_argument('--dry-run', '-n', help='dry-run, no moving files',
                        default=False, dest='dry_run', action='store_true')

    args = parser.parse_args()
    return args



if __name__ == '__main__':
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    screenshots = dbs.session.query(anime.TitleScreenShot).filter(anime.TitleScreenShot.filename.like(f'{config.source_basedir.rstrip("/")}%')).all()
    print(len(screenshots))
    # sys.exit(0)
    for screenshot in screenshots:
      try:
        known_file = dbs.session.query(anime.File).filter(anime.File.hash_ed2k==screenshot.source_file_hash_ed2k).one()
        aid = known_file.aid
      except:
        aid = screenshot.aid
      if not aid:
        print(f'##### WARNING: "{screenshot.filename}" does not have an anime id')
        continue
      aid_padded = str(aid).zfill(AID_PAD_WIDTH)
      aid_path = os.path.join(*[aid_padded[i:i+AID_CHUNK_SIZE] for i in range(0, AID_PAD_WIDTH, AID_CHUNK_SIZE)])
      target_dir = os.path.join(config.target_basedir, 'by-id', aid_path)
      if os.path.dirname(screenshot.filename) not in [target_dir]:
        if os.path.isfile(screenshot.filename):
          print(f'file not sorted yet "{screenshot.filename}" is in "{os.path.dirname(screenshot.filename)}", should be "{target_dir}"')
          if not os.path.isfile(os.path.join(target_dir, os.path.basename(screenshot.filename))):
            pathlib.Path(target_dir).mkdir(parents=True, exist_ok=True)
            print(f'##### INFO: moving "{screenshot.filename}" to "{target_dir}"')
            if not config.dry_run:
              shutil.move(screenshot.filename, target_dir)
              screenshot.filename = os.path.join(target_dir, os.path.basename(screenshot.filename))
              dbs.session.merge(screenshot)
              dbs.session.commit()
            else:
              print('##### INFO: dry-run requested, not moving file')
              print(f'##### INFO: dry-run: source {screenshot.filename} target {target_dir}')
              print(f'##### INFO: dry-run: {os.path.join(target_dir, os.path.basename(screenshot.filename))}')

          else:
            print(f'##### WARNING: "{os.path.join(target_dir, os.path.dirname(screenshot.filename))}" already present')
