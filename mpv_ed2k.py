#!/usr/bin/python3

import os.path
import subprocess
import re
import weltschmerz.anime as anime
import configparser
import argparse


def get_config(config_file=os.path.expanduser("~/.config/weltschmerz/weltschmerz.cfg")):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description="Play file matching ed2k in the database."
    )
    parser.add_argument(
        "--database", help="database to use", default=config.get("client", "database")
    )
    parser.add_argument("ed2k", help="ed2k hash to query")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    # try:
    uri = config.ed2k
    ed2k_match = re.match(r"(mpv-ed2k://)?(?P<ed2k>[0-9A-Fa-f]{32})", uri)
    ed2k = ed2k_match.group("ed2k")
    local_file = (
        dbs.session.query(anime.LocalFile)
        .filter(anime.LocalFile.hash_ed2k == ed2k)
        .first()
    )
    if local_file:
        print(local_file.directory)
        print(local_file.filename)
        subprocess.call(["mpv", "--load-scripts=no", local_file.full_path])
