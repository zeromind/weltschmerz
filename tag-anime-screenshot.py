#!/usr/bin/python3

import db
import os
import sys
import logging
from subprocess import call
import shutil
import re

# s async screenshot-to-file "/anime/screenshots/unsorted/${filename}_${=time-pos}.jpg" video; run "/home/zeromind/src/ekorre/anidb/weltschmerz/tag-anime-screenshot.py" "/anime/screenshots/unsorted/${filename}_${=time-pos}.jpg" "${path}" "${=file-size}" "${duration}" "${time-pos}" "${=time-pos}"; write-watch-later-config; playlist-next

if __name__ == '__main__':
    logfile = '/skymning/weltschmerz/tag-anime-screenshot.log'
    dbc = db.Connection(db='/skymning/weltschmerz/weltschmerz.sqlite3')
    logging.basicConfig(filename=logfile, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    (screenshot_file, path, filesize, duration, timepos, timepos_raw) = sys.argv[1:]
    real_path = os.path.realpath(os.path.abspath(path))
    try:
        (hash_crc, hash_md5, hash_sha1, hash_ed2k) = dbc.get_file_hashed_by_path(*os.path.split(real_path), filesize)
        logging.info('found file \'{filename}\', adding metadata for {timepos}...'.format(
            filename=os.path.basename(path),
            timepos=timepos
        ))

        call([
            '/usr/bin/exiftool',
            '-xmp-anime:AnimeFileName={filename}'.format(filename=os.path.basename(path)),
            '-xmp-anime:AnimeFileSize={filesize}'.format(filesize=os.path.getsize(path)),
            '-xmp-anime:AnimeFileDuration={duration}'.format(duration=duration),
            '-xmp-anime:AnimeFileTime={timepos}'.format(timepos=timepos),
            '-xmp-anime:AnimeFileCrc32={crc32}'.format(crc32=hash_crc),
            '-xmp-anime:AnimeFileMd5={md5}'.format(md5=hash_md5),
            '-xmp-anime:AnimeFileSha1={sha1}'.format(sha1=hash_sha1),
            '-xmp-anime:AnimeFileEd2k={ed2k}'.format(ed2k=hash_ed2k),
            '-overwrite_original_in_place',
            screenshot_file,
        ])
        target_folder = os.path.join('/anime/screenshots/', re.search('(by-id(/[0-9]{2}){3})', real_path).group(1))
        target_file = os.path.join(target_folder, os.path.basename(screenshot_file))
        if os.path.isfile(target_file):
            logging.info('screenshot \'{target_file}\' already present, deleting \'{screenshot}\'...'.format(
                target_file=target_file,
                screenshot=screenshot_file)
            )
            os.unlink(screenshot_file)
        else:
            shutil.move(screenshot_file, target_folder)

    except Exception as e:
        logging.info('found anime id, moving file to \'{target_folder}\'...'.format(target_folder=target_folder))
        target_file = os.path.join(target_folder, os.path.basename(screenshot_file))
        logging.error('\'{filename}\' not found, aborting... {error}'.format(filename=os.path.basename(path), error=e))
        sys.exit(1)
