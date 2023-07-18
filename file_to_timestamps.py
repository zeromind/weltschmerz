#!/usr/bin/python3

import anime
import os
import logging
import subprocess
import configparser
import argparse
import sys
from sqlalchemy.exc import NoResultFound


def get_config(config_file=os.path.expanduser("~/.config/weltschmerz/weltschmerz.cfg")):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description="Tag screenshot file with source file metadata and add title card screenshot to database"
    )
    parser.add_argument(
        "--database",
        help="database to use",
        default=config.get("tag-screenshot", "database"),
    )
    parser.add_argument(
        "--log-file",
        dest="log_file",
        help="logfile to use",
        default=config.get("tag-screenshot", "logfile"),
    )
    parser.add_argument(
        "-F", "--file-path", help="file to query for", default=None, dest="file_path"
    )
    parser.add_argument(
        "-T",
        "--title-type",
        help="title type to query for",
        default=1,
        dest="title_type",
    )
    parser.add_argument(
        "-L",
        "--title-limit",
        help="limit titles per episode",
        default=1,
        dest="title_limit",
    )
    parser.add_argument(
        "-m",
        "--minimum-filesize",
        help="skip files smaller than given size",
        default=128 * 1024,
        dest="minimum_filesize",
    )

    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log_file,
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    return args


def do_mpv_start(file_name: str, timestamps: list[str]):
    for timestamp in timestamps:
        subprocess.call(
            [
                "mpv",
                "--load-scripts=no",
                f"--start={timestamp}",
                "--aid=0",
                "--sid=0",
                "--script-opts=osc-visibility=always",
                "--cache=no",
                "--hwdec=auto-copy",
                "--autoload-files=no",
                file_name,
            ]
        )


if __name__ == "__main__":
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    real_path = os.path.realpath(os.path.abspath(config.file_path))
    (directory, filename) = os.path.split(real_path)

    if os.path.getsize(real_path) < config.minimum_filesize:
        logging.info(f"file size of '{filename}' below threshold, skipping...")
        sys.exit(0)

    try:
        logging.info(f"Looking up {real_path}")
        known_localfile = (
            dbs.session.query(anime.LocalFile)
            .filter(
                anime.LocalFile.directory == directory.rstrip("/"),
                anime.LocalFile.filename == filename,
            )
            .one()
        )
        known_screenshots_local_file = (
            dbs.session.query(anime.TitleScreenShot)
            .distinct(anime.TitleScreenShot.time_position)
            .filter(
                anime.TitleScreenShot.title_type.in_([1, 3]),
            )
            .filter_by(
                source_file_hash_ed2k=known_localfile.hash_ed2k,
                source_file_size=known_localfile.filesize,
            )
        ).all()
        if len(known_screenshots_local_file) >= config.title_limit:
            logging.info(
                f"found file '{filename}' in DB, enough title screenshots, skipping..."
            )
            sys.exit(0)

        known_file = (
            dbs.session.query(anime.File)
            .filter_by(
                hash_ed2k=known_localfile.hash_ed2k, filesize=known_localfile.filesize
            )
            .one()
        )
        logging.info(
            f"found file '{filename}' in DB, querying possible timestamps for episode {known_file.eid}..."
        )
        known_screenshots = (
            dbs.session.query(anime.TitleScreenShot)
            .distinct(anime.TitleScreenShot.time_position)
            .filter(
                anime.TitleScreenShot.title_type.in_([1, 3]),
            )
            .join(anime.File)
            .filter_by(eid=known_file.eid)
        )
        if known_screenshots:
            timestamps = [tss.time_position for tss in known_screenshots]
            print(filename)
            print(f"original timestamps: {timestamps}")
            if len(known_screenshots_local_file) >= 1:
                timestamps_local_file = [
                    tss.time_position for tss in known_screenshots_local_file
                ]
                print(f"local_file timestamps: {timestamps_local_file}")
                timestamps = [t for t in timestamps if t not in timestamps_local_file]
            print(f"resulting timestamps: {timestamps}")
            if len(timestamps) >= 1:
                do_mpv_start(real_path, sorted(timestamps))

    except NoResultFound as e:
        logging.warning(f"'{filename}' not found in DB, only tagged minimal info...")
