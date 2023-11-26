#!/usr/bin/python3

import os.path
import shutil
import pathlib
import anime
import configparser
import argparse

# import yumemi
import sys
import anime
import masks

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

    args = parser.parse_args()
    return args


class AniDBClient:
    def __init__(
        self,
        local_database: str,
        local_database_verbose: bool = False,
        fmask=masks.FMASK,
        famask=masks.FAMASK,
    ):
        (self.fmask_string, self.fmask_fields) = masks.make_mask(fmask)
        (self.famask_string, self.famask_fields) = masks.make_mask(famask)
        self.dbs = anime.DatabaseSession(local_database, local_database_verbose)
        # self.client = yumemi.Client(CLIENT_NAME, CLIENT_VERSION)

    def lookup_file(self, file_size: int, hash_ed2k: str):
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
            local_db_file = anime.File(
                fid=file_data["fid"],
                filesize=file_size,
                aid=file_data["aid"],
                eid=file_data["eid"],
                gid=file_data["gid"],
                source=file_data["source"],
                extension=file_data["file type (extension)"],
                hash_ed2k=hash_ed2k,
            )
            self.dbs.session.merge(local_db_file)
        elif result.code == 320:  # file not found
            pass
        return result


if __name__ == "__main__":
    config = get_config()
    adbc = AniDBClient(config.database, False, FMASK, FAMASK)
    # known_files = (
    #     adbc.dbs.session.query(anime.LocalFile)
    #     .join(anime.File, anime.LocalFile.hash_ed2k == anime.File.hash_ed2k)
    #     .filter(anime.LocalFile.directory.like(f'{config.source_basedir.rstrip("/")}%'))
    #     .all()
    # )
    unknown_files = (
        adbc.dbs.session.query(anime.LocalFile)
        .filter(anime.LocalFile.directory.like(f'{config.source_basedir.rstrip("/")}%'))
        .filter((anime.LocalFile.fid == None) | (anime.LocalFile.aid == None))
        .all()
    )
    known_files = []
    for i, unknown_file in enumerate(unknown_files):
        known_file = (
            adbc.dbs.session.query(anime.File)
            .join(anime.LocalFile, anime.LocalFile.hash_ed2k == anime.File.hash_ed2k)
            .filter(anime.File.hash_ed2k == unknown_file.hash_ed2k)
            .all()
        )
        if len(known_file) == 1:
            # print(f'found file: {known_file[0].fid}')
            unknown_file.fid = known_file[0].fid
            unknown_file.aid = known_file[0].aid

            known_files.append(unknown_file)
        if len(known_files) % 100 == 0:
            # print(len(known_files))
            adbc.dbs.session.commit()

    print(f'{config.source_basedir.rstrip("/")} {len(known_files)}')
    if len(known_files) > 0:
        adbc.dbs.session.commit()
    # print(len(unknown_files))
    if len(unknown_files) == 0:
        sys.exit(0)
    # try:
    #     pass
    # except yumemi.AnidbError as e:
    #     print(e)
