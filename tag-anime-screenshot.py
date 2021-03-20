#!/usr/bin/python3

import anime
import os
import logging
import shutil
import re
import pyexiv2
import configparser
import argparse


def get_config(config_file='weltschmerz.cfg'):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description='Tag screenshot file with source file metadata.')
    parser.add_argument('--database', help='database to use',
                        default=config.get('tag-screenshot', 'database'))
    parser.add_argument('--log-file', dest='log_file', help='logfile to use',
                        default='tag-anime-screenshot.log')
    parser.add_argument('-S', '--screenshot-file', help='screenshot file to tag',
                        default=None, dest='screenshot_file')
    parser.add_argument('-F', '--file-path', help='file to query for',
                        default=None, dest='file_path')
    parser.add_argument('-s', '--file-size', help='filesize to query for',
                        default=None, dest='file_size')
    parser.add_argument('-d', '--duration', help='file to query for',
                        default=None)
    parser.add_argument('-t', '--timepos', help='timepos of screenshot',
                        default=None)
    parser.add_argument('-T', '--timepos-raw', help='timepos (raw) of screenshot',
                        default=None, dest='timepos_raw')
    parser.add_argument('-B', '--target-basedir', help='timepos (raw) of screenshot',
                        dest='target_basedir')

    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file,
                        format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    return args

def tag_screenshot(screenshot, filename, filesize, duration, timepos, hash_crc, hash_md5, hash_sha1, hash_ed2k):
    logging.info(f'tagging {config.screenshot_file}...')
    pyexiv2.xmp.register_namespace('http://ns.eroforce.one/anime/1.0/', 'anime')
    metadata = pyexiv2.ImageMetadata(screenshot)
    metadata.read()
    metadata['Xmp.anime.AnimeFileName'] = filename
    metadata['Xmp.anime.AnimeFileSize'] = filesize
    metadata['Xmp.anime.AnimeFileDuration'] = duration
    metadata['Xmp.anime.AnimeFileTime'] = timepos
    metadata['Xmp.anime.AnimeFileCrc32'] = hash_crc
    metadata['Xmp.anime.AnimeFileMd5'] = hash_md5
    metadata['Xmp.anime.AnimeFileSha1'] = hash_sha1
    metadata['Xmp.anime.AnimeFileEd2k'] = hash_ed2k
    metadata.write()
    logging.info(f'tagged {config.screenshot_file}')


if __name__ == '__main__':
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    real_path = os.path.realpath(os.path.abspath(config.file_path))
    logging.info(f'processing {config.screenshot_file}')

    (directory, filename) = os.path.split(real_path)
    known_file = dbs.session.query(anime.LocalFile).filter(anime.LocalFile.directory == directory.rstrip('/'), anime.LocalFile.filename==filename, anime.LocalFile.filesize==config.file_size).one()
    if known_file:
        logging.info(f'found file \'{filename}\', adding metadata for {config.timepos}...')
        tag_screenshot(
            screenshot=config.screenshot_file,
            filename=known_file.filename,
            filesize=config.file_size,
            duration=config.duration,
            timepos=config.timepos,
            hash_crc=known_file.hash_crc,
            hash_md5=known_file.hash_md5,
            hash_sha1=known_file.hash_sha1,
            hash_ed2k=known_file.hash_ed2k
            )
        target_folder = os.path.join(config.target_basedir, re.search('(by-id(/[0-9]{2}){3})', real_path).group(1))
        target_file = os.path.join(target_folder, os.path.basename(config.screenshot_file))
        if os.path.isfile(target_file):
            logging.warning(f'screenshot \'{target_file}\' already present, deleting \'{config.screenshot_file}\'...')
            os.unlink(config.screenshot_file)
        else:
            logging.info(f'found anime id, moving file to \'{target_folder}\'...')
            os.makedirs(os.path.abspath(target_folder), exist_ok=True)
            shutil.move(config.screenshot_file, target_file)
    else:
        logging.error(f'\'{filename}\' not found, aborting...')

