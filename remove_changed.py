#!/usr/bin/python3

import anime
import filehash
import configparser
import os
import argparse


def get_config(config_file: str = "weltschmerz.cfg"):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description="Remove files that changed in size from database."
    )
    parser.add_argument(
        "--database", help="database to use", default=config.get("client", "database")
    )
    parser.add_argument(
        "--log-file",
        dest="log_file",
        help="logfile to use",
        default=config.get("client", "log"),
    )
    parser.add_argument("--folder", help="folder to process", default="/")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    hashed_files = dbs.session.query(anime.LocalFile).filter(
        anime.LocalFile.directory.like(config.folder + "%")
    )
    for local_file in hashed_files:
        if os.path.isfile(local_file.full_path):
            if local_file.filesize != os.path.getsize(local_file.full_path):
                print(f"###### filesize mismatch, removing {local_file.full_path}")
                dbs.session.delete(local_file)
