#!/usr/bin/python3

import weltschmerz.anime as anime
import os
import logging
import shutil
import re
import exiv2
import configparser
import argparse
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
        type=str,
        default=config.get("tag-screenshot", "database"),
    )
    parser.add_argument(
        "--log-file",
        dest="log_file",
        help="logfile to use",
        type=str,
        default=config.get("tag-screenshot", "logfile"),
    )
    parser.add_argument(
        "-S",
        "--screenshot-file",
        help="screenshot file to tag",
        default=None,
        type=str,
        dest="screenshot_file",
    )
    parser.add_argument(
        "-F",
        "--file-path",
        help="file to query for",
        type=str,
        default=None,
        dest="file_path",
    )
    parser.add_argument(
        "-s",
        "--file-size",
        help="filesize to query for",
        default=None,
        type=int,
        dest="file_size",
    )
    parser.add_argument("-d", "--duration", help="file duration", default=None)
    parser.add_argument(
        "-D", "--duration-raw", help="file duration (raw)", default=None
    )
    parser.add_argument("-t", "--timepos", help="timepos of screenshot", default=None)
    parser.add_argument(
        "-T",
        "--timepos-raw",
        help="timepos (raw) of screenshot",
        default=None,
        dest="timepos_raw",
    )
    parser.add_argument(
        "-B",
        "--target-basedir",
        help="timepos (raw) of screenshot",
        default=config.get("tag-screenshot", "basedir"),
        dest="target_basedir",
    )
    parser.add_argument(
        "--screenshot-type", help="screenshot type", type=int, default=1
    )

    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log_file,
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    return args


def tag_screenshot(
    screenshot: str,
    filename: str,
    filesize: int,
    duration: str,
    duration_raw: str,
    timepos: str,
    timepos_raw: str,
    screenshot_type: int,
    hash_crc: str,
    hash_md5: str,
    hash_sha1: str,
    hash_ed2k: str,
):
    logging.info(f"tagging {config.screenshot_file}...")
    exiv2.XmpProperties.registerNs("http://ns.eroforce.one/anime/1.0/", "anime")
    screenshot_image = exiv2.ImageFactory.open(screenshot)
    screenshot_image.readMetadata()
    metadata = screenshot_image.xmpData()
    metadata["Xmp.anime.AnimeFileName"] = filename
    metadata["Xmp.anime.AnimeFileSize"] = filesize
    metadata["Xmp.anime.AnimeFileDuration"] = duration
    metadata["Xmp.anime.AnimeFileDurationRaw"] = duration_raw
    metadata["Xmp.anime.AnimeFileTime"] = timepos
    metadata["Xmp.anime.AnimeFileTimeRaw"] = timepos_raw
    metadata["Xmp.anime.AnimeFileCrc32"] = hash_crc
    metadata["Xmp.anime.AnimeFileMd5"] = hash_md5
    metadata["Xmp.anime.AnimeFileSha1"] = hash_sha1
    metadata["Xmp.anime.AnimeFileEd2k"] = hash_ed2k
    metadata["Xmp.anime.ScreenshotType"] = screenshot_type
    screenshot_image.setXmpData(metadata)
    screenshot_image.writeMetadata()
    logging.info(f"tagged {config.screenshot_file}")


def tag_screenshot_min(
    screenshot: str,
    filename: str,
    filesize: int,
    duration: str,
    duration_raw: str,
    timepos: str,
    timepos_raw: str,
    screenshot_type: int,
):
    logging.info(f"tagging (min) {config.screenshot_file}...")
    exiv2.XmpProperties.registerNs("http://ns.eroforce.one/anime/1.0/", "anime")
    screenshot_image = exiv2.ImageFactory.open(screenshot)
    screenshot_image.readMetadata()
    metadata = screenshot_image.xmpData()
    metadata["Xmp.anime.AnimeFileName"] = filename
    metadata["Xmp.anime.AnimeFileSize"] = filesize
    metadata["Xmp.anime.AnimeFileDuration"] = duration
    metadata["Xmp.anime.AnimeFileDurationRaw"] = duration_raw
    metadata["Xmp.anime.AnimeFileTime"] = timepos
    metadata["Xmp.anime.AnimeFileTimeRaw"] = timepos_raw
    metadata["Xmp.anime.ScreenshotType"] = screenshot_type
    screenshot_image.setXmpData(metadata)
    screenshot_image.writeMetadata()
    logging.info(f"tagged (min) {config.screenshot_file}")


if __name__ == "__main__":
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    real_path = os.path.realpath(os.path.abspath(config.file_path))
    logging.info(f"processing {config.screenshot_file}")

    (directory, filename) = os.path.split(real_path)
    try:
        known_file = (
            dbs.session.query(anime.LocalFile)
            .filter(
                anime.LocalFile.directory == directory.rstrip("/"),
                anime.LocalFile.filename == filename,
                anime.LocalFile.filesize == config.file_size,
            )
            .one()
        )
        logging.info(
            f"found file '{filename}' in DB, adding metadata for {config.timepos} ..."
        )
        tag_screenshot(
            screenshot=config.screenshot_file,
            filename=known_file.filename,
            filesize=config.file_size,
            duration=config.duration,
            duration_raw=config.duration_raw,
            timepos=config.timepos,
            timepos_raw=config.timepos_raw,
            screenshot_type=config.screenshot_type,
            hash_crc=known_file.hash_crc,
            hash_md5=known_file.hash_md5,
            hash_sha1=known_file.hash_sha1,
            hash_ed2k=known_file.hash_ed2k,
        )
        tss = anime.TitleScreenShot(
            filename=config.screenshot_file,
            source_file_name=known_file.filename,
            source_file_size=config.file_size,
            source_file_hash_ed2k=known_file.hash_ed2k,
            source_file_hash_crc=known_file.hash_crc,
            source_file_hash_md5=known_file.hash_md5,
            source_file_hash_sha1=known_file.hash_sha1,
            source_file_duration=config.duration,
            source_file_duration_raw=config.duration_raw,
            time_position=config.timepos,
            time_position_raw=config.timepos_raw,
            title_type=config.screenshot_type,
        )
        if re.search("(by-id(/[0-9]{2}){3})", real_path):
            target_folder = os.path.join(
                config.target_basedir,
                re.search("(by-id(/[0-9]{2}){3})", real_path).group(1),
            )
            target_file = os.path.join(
                target_folder, os.path.basename(config.screenshot_file)
            )
            if os.path.isfile(target_file):
                logging.warning(
                    f"screenshot '{target_file}' already present, deleting '{config.screenshot_file}' ..."
                )
                os.unlink(config.screenshot_file)
            else:
                logging.info(f"found anime id, moving file to '{target_folder}'...")
                os.makedirs(os.path.abspath(target_folder), exist_ok=True)
                shutil.move(config.screenshot_file, target_file)
            tss.filename = target_file
        logging.info(
            f"adding title screenshot to DB for '{tss.filename}' at {config.timepos} ..."
        )
        try:
            anidb_file = (
                dbs.session.query(anime.File)
                .filter(anime.File.hash_ed2k == known_file.hash_ed2k)
                .one()
            )
            tss.aid = anidb_file.aid
            tss.eid = anidb_file.eid
            tss.fid = anidb_file.fid
        except:
            pass
        dbs.session.merge(tss)
        dbs.session.commit()
    except NoResultFound as e:
        tag_screenshot_min(
            screenshot=config.screenshot_file,
            filename=filename,
            filesize=config.file_size,
            duration=config.duration,
            duration_raw=config.duration_raw,
            timepos=config.timepos,
            timepos_raw=config.timepos_raw,
            screenshot_type=config.screenshot_type,
        )
        logging.warning(f"'{filename}' not found in DB, only tagged minimal info ...")
