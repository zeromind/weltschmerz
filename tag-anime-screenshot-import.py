#!/usr/bin/python3

import anime
import os
import logging
import shutil
import re
import pyexiv2
import configparser
import argparse
import sys


def get_config(config_file=os.path.expanduser("~/.config/weltschmerz/weltschmerz.cfg")):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description="Tag screenshot file with source file metadata."
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
        "-S",
        "--screenshot-files",
        nargs="*",
        help="screenshot file to tag",
        default=None,
        dest="screenshot_files",
    )

    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log_file,
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    return args


def try_parse_xmp(md: pyexiv2.ImageMetadata, tag: str):
    try:
        return md[tag].value
    except KeyError:
        return None


def raw_timepos_from_filename(filename: str):
    try:
        matches = re.match(r"^.*_([0-9]+.[0-9]+)\.(jpeg|jpg|webp|png)$", filename)
        return matches.groups()[0]
    except:
        raise


def anime_filename_from_filename(filename: str):
    try:
        matches = re.match(r"^(.*)_([0-9]+.[0-9]+)\.(jpeg|jpg|webp|png)$", filename)
        return matches.groups()[0]
    except:
        raise


def parse_screenshot(screenshot: str) -> anime.TitleScreenShot:
    try:
        metadata = pyexiv2.ImageMetadata(screenshot)
        metadata.read()
        tss = anime.TitleScreenShot(
            filename=screenshot,
            source_file_name=try_parse_xmp(metadata, "Xmp.anime.AnimeFileName")
            or anime_filename_from_filename(screenshot),
            source_file_size=metadata["Xmp.anime.AnimeFileSize"].value,
            source_file_hash_ed2k=metadata["Xmp.anime.AnimeFileEd2k"].value,
            source_file_hash_crc=try_parse_xmp(metadata, "Xmp.anime.AnimeFileCrc32"),
            source_file_hash_md5=try_parse_xmp(metadata, "Xmp.anime.AnimeFileMd5"),
            source_file_hash_sha1=try_parse_xmp(metadata, "Xmp.anime.AnimeFileSha1"),
            source_file_duration=try_parse_xmp(metadata, "Xmp.anime.AnimeFileDuration"),
            source_file_duration_raw=try_parse_xmp(
                metadata, "Xmp.anime.AnimeFileDurationRaw"
            ),
            time_position=metadata["Xmp.anime.AnimeFileTime"].value,
            time_position_raw=try_parse_xmp(metadata, "Xmp.anime.AnimeFileTimeRaw")
            or raw_timepos_from_filename(screenshot),
            title_type=try_parse_xmp(metadata, "Xmp.anime.ScreenshotType"),
        )
        try:
            anidb_file = (
                dbs.session.query(anime.File)
                .filter(
                    anime.File.hash_ed2k == metadata["Xmp.anime.AnimeFileEd2k"].value
                )
                .one()
            )
            tss.aid = anidb_file.aid
            tss.eid = anidb_file.eid
            tss.fid = anidb_file.fid
        except:
            pass

        logging.info(f"parsed {screenshot}...")
        return tss
    except KeyError as e:
        raise e
    except AttributeError as e:
        raise e


if __name__ == "__main__":
    pyexiv2.xmp.register_namespace("http://ns.eroforce.one/anime/1.0/", "anime")
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    for screenshot_file in config.screenshot_files:
        try:
            logging.info(f"importing metadata from {screenshot_file}...")
            scr = parse_screenshot(screenshot_file)
            dbs.session.merge(scr)
            logging.info(f"imported metadata from {screenshot_file}")
        except KeyError as e:
            logging.error(f"failed importing metadata from {screenshot_file}")
            logging.error(e)
        except AttributeError as e:
            logging.error(f"failed importing metadata from {screenshot_file}")
            logging.error(e)
    dbs.session.commit()
