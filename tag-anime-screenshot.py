#!/usr/bin/python3

import db
import os
import sys
import logging
from subprocess import call

# s async screenshot-to-file "/anime/screenshots/unsorted/${filename}_${=time-pos}.jpg" video; run "/home/zeromind/src/ekorre/anidb/weltschmerz/tag-anime-screenshot.py" "/anime/screenshots/unsorted/${filename}_${=time-pos}.jpg" "${path}" "${=file-size}" "${duration}" "${time-pos}" "${=time-pos}"; write-watch-later-config; playlist-next

if __name__ == '__main__':
    logfile = '/skymning/weltschmerz/tag-anime-screenshot.log'
    dbc = db.Connection(db='/skymning/weltschmerz/weltschmerz.sqlite3')
    logging.basicConfig(filename=logfile, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    (screenshot_file, path, filesize, duration, timepos, timepos_raw) = sys.argv[1:]
    try:
        (hash_crc, hash_md5, hash_sha1, hash_ed2k) = dbc.get_file_hashed_by_path(*os.path.split(os.path.realpath(os.path.abspath(path))), filesize)
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
    except Exception as e:
        logging.error('file not found, aborting... {}'.format(e))
        sys.exit(1)
