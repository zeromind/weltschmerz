#!/usr/bin/python3

import os.path
import shutil
import pathlib
import anime
import configparser
import argparse

import yumemi
import sys
import anime
import masks
import time
import datetime

CLIENT_NAME = "weltschmerz"
CLIENT_VERSION = 0
FMASK = (
    (
        [0, "", ""],  # byte 1
        [1, "int4", "aid"],
        [1, "int4", "eid"],
        [1, "int4", "gid"],
        [1, "int4", "mylist id"],
        [1, "list", "other episodes"],
        [0, "int2", "IsDeprecated"],
        [1, "int2", "state"],
    ),
    (
        [0, "int8", "size"],  # byte 2
        [0, "str", "ed2k"],
        [0, "str", "md5"],
        [0, "str", "sha1"],
        [0, "str", "crc32"],
        [0, "", ""],
        [0, "", "video color depth"],
        [0, "", ""],
    ),
    (
        [1, "str", "quality"],  # byte 3
        [1, "str", "source"],
        [0, "str", "audio codec list"],
        [0, "int4", "audio bitrate list"],
        [0, "str", "video codec"],
        [0, "int4", "video bitrate"],
        [0, "str", "video resolution"],
        [1, "str", "file type (extension)"],
    ),
    (
        [0, "str", "dub language"],  # byte 4
        [0, "str", "sub language"],
        [0, "int4", "length in seconds"],
        [0, "str", "description"],
        [0, "int4", "aired date"],
        [0, "", ""],
        [0, "", ""],
        [0, "str", "anidb file name"],
    ),
    (
        [1, "int4", "mylist state"],  # byte 5
        [1, "int4", "mylist filestate"],
        [1, "int4", "mylist viewed"],
        [1, "int4", "mylist viewdate"],
        [1, "str", "mylist storage"],
        [1, "str", "mylist source"],
        [1, "str", "mylist other"],
        [0, "", ""],
    ),
)
FAMASK = (
    (
        [1, "int4", "anime total episodes"],  # byte 1
        [1, "", "highest episode number"],
        [0, "", "year"],
        [0, "", "type"],
        [0, "", "related aid list"],
        [0, "", "related aid type"],
        [0, "", "category list"],
        [0, "", ""],
    ),
    (
        [0, "str", "romaji name"],  # byte 2
        [0, "str", "kanji name"],
        [0, "str", "english name"],
        [0, "str", "other name"],
        [0, "str", "short name list"],
        [0, "str", "synonym list"],
        [0, "", ""],
        [0, "", ""],
    ),
    (
        [1, "str", "epno"],  # byte 3
        [1, "str", "ep name"],
        [1, "str", "ep romaji name"],
        [1, "str", "ep kanji name"],
        [0, "int4", "episode rating"],
        [0, "int4", "episode vote count"],
        [0, "", ""],
        [0, "", ""],
    ),
    (
        [1, "str", "group name"],  # byte 4
        [1, "str", "group short name"],
        [0, "", ""],
        [0, "", ""],
        [0, "", ""],
        [0, "", ""],
        [0, "", ""],
        [0, "int4", "date aid record updated"],
    ),
)


def get_config(config_file: str = "weltschmerz.cfg"):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description="Move known local files to target directory."
    )
    parser.add_argument(
        "--database", help="database to use", default=config.get("client", "database")
    )
    parser.add_argument(
        "--source-basedir",
        help="source folder to process",
        default=None,
        dest="source_basedir",
    )
    parser.add_argument(
        "--target-basedir",
        help="target basedir to move files to",
        default=None,
        dest="target_basedir",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        help="dry-run, no moving files",
        default=False,
        dest="dry_run",
        action="store_true",
    )
    parser.add_argument(
        "--target-crc32",
        "-C",
        help="add crc32 to target filename",
        default=False,
        dest="target_crc32",
        action="store_true",
    )
    parser.add_argument(
        "--online",
        "-O",
        help="whether to ask anidb about file info",
        default=False,
        dest="online",
        action="store_true",
    )
    parser.add_argument(
        "--anidb-username",
        help="AniDB username",
        default=config.get("anidb", "username"),
    )
    parser.add_argument(
        "--anidb-password",
        help="AniDB password",
        default=config.get("anidb", "password"),
    )

    args = parser.parse_args()
    return args


class AniDBClient:
    def __init__(
        self,
        local_database: str,
        local_database_verbose: bool = False,
        fmask=masks.FMASK,
        famask=masks.FAMASK,
        online: bool = False,
        anidb_username: str = None,
        anidb_password: str = None,
    ):
        (self.fmask_string, self.fmask_fields) = masks.make_mask(fmask)
        (self.famask_string, self.famask_fields) = masks.make_mask(famask)
        self.dbs = anime.DatabaseSession(local_database, local_database_verbose)
        self.online = online
        self.client = None
        self.anidb_username = anidb_username
        self.anidb_password = anidb_password

    def go_online(self):
        if not self.client:
            if self.anidb_username and self.anidb_password and self.online:
                self.client = yumemi.Client(CLIENT_NAME, CLIENT_VERSION)
                self.client.auth(self.anidb_username, self.anidb_password)
            else:
                raise ValueError

    def lookup_file(self, file_size: int, hash_ed2k: str) -> dict:
        file_data = {}
        ##############
        # try cache
        ##############
        cached_response = (
            self.dbs.session.query(anime.AnidbFileResponse)
            .filter(anime.AnidbFileResponse.hash_ed2k == hash_ed2k)
            .filter(anime.AnidbFileResponse.filesize == file_size)
            .first()
        )
        if cached_response:
            file_data = cached_response.data
            # print(f"DEBUG: cached file data found {file_data}")
        if self.online and not cached_response:
            ##############
            # ask AniDB
            ##############
            try:
                self.go_online()
                result = self.client.command(
                    "FILE",
                    {
                        "size": file_size,
                        "ed2k": hash_ed2k,
                        "fmask": self.fmask_string,
                        "amask": self.famask_string,
                    },
                )
                if result.code == 220:  # file found
                    requested_fields = self.fmask_fields + self.famask_fields
                    # "fid is always returned as the first value, regardless of what masks are provided."
                    file_data = dict(zip(["fid"] + requested_fields, result.data[0]))
            except Exception as e:
                print(
                    f"WARN: AniDB lookup failed for {hash_ed2k} / {file_size}: {type(e)}"
                )
            # persist new cached response
            anidb_file_response = anime.AnidbFileResponse(
                hash_ed2k=hash_ed2k,
                filesize=file_size,
                fmask=self.fmask_string,
                famask=self.famask_string,
                data=file_data,
                updated_at=datetime.datetime.utcnow(),
            )
            self.dbs.session.merge(anidb_file_response)
        if len(file_data.keys()) > 0:
            # print(f"DEBUG: file data found {file_data}")

            # update local DB from data
            local_db_anime = anime.Anime(
                aid=file_data["aid"], last_update=datetime.datetime.utcnow()
            )
            self.dbs.session.merge(local_db_anime)
            local_db_episode = anime.Episode(
                eid=file_data["eid"],
                aid=file_data["aid"],
                ep=file_data["epno"],
                title_en=file_data["ep name"],
                title_jp=file_data["ep kanji name"],
                title_jp_t=file_data["ep romaji name"],
                last_update=datetime.datetime.utcnow(),
            )
            self.dbs.session.merge(local_db_episode)
            local_db_file = anime.File(
                fid=file_data["fid"],
                filesize=file_size,
                aid=file_data["aid"],
                eid=file_data["eid"],
                gid=file_data["gid"],
                source=file_data["source"],
                extension=file_data["file type (extension)"],
                hash_ed2k=hash_ed2k,
                last_update=datetime.datetime.utcnow(),
            )
            self.dbs.session.merge(local_db_file)
            self.dbs.session.commit()
        return file_data


if __name__ == "__main__":
    config = get_config()
    adbc = AniDBClient(
        config.database,
        False,
        FMASK,
        FAMASK,
        config.online,
        config.anidb_username,
        config.anidb_password,
    )
    unknown_files = (
        adbc.dbs.session.query(anime.LocalFile)
        .filter(anime.LocalFile.directory.like(f'{config.source_basedir.rstrip("/")}%'))
        .filter((anime.LocalFile.fid == None) | (anime.LocalFile.aid == None))
        .all()
    )
    known_files = []
    files_to_look_up = []
    for i, unknown_file in enumerate(unknown_files):
        known_file = (
            adbc.dbs.session.query(anime.File)
            .join(anime.LocalFile, anime.LocalFile.hash_ed2k == anime.File.hash_ed2k)
            .filter(anime.File.hash_ed2k == unknown_file.hash_ed2k)
            .first()
        )
        if known_file:
            print(f"found file: {known_file.fid}")
            unknown_file.fid = known_file.fid
            unknown_file.aid = known_file.aid

            known_files.append(unknown_file)
        else:
            files_to_look_up.append(unknown_file)
        if len(known_files) % 100 == 0:
            adbc.dbs.session.commit()

    print(
        f'{config.source_basedir.rstrip("/")} - unknown files: {len(unknown_files)} - known: {len(known_files)} - to look up: {len(files_to_look_up)}'
    )
    if len(known_files) > 0:
        adbc.dbs.session.commit()

    # for i, file_to_look_up in enumerate(unknown_files):
    for i, file_to_look_up in enumerate(files_to_look_up):
        anidb_result = adbc.lookup_file(
            file_to_look_up.filesize, file_to_look_up.hash_ed2k
        )
        if adbc.online:
            time.sleep(3)
    adbc.dbs.session.commit()
    if adbc.online and adbc.client:
        adbc.client.logout()
