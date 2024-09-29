#!/usr/bin/python3

import weltschmerz.anime as anime
import configparser
import argparse
import os.path


def get_config(config_file="weltschmerz.cfg"):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description="Return unknown files from the database."
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
    parser.add_argument("--folder", help="folder to query", default=None)
    parser.add_argument(
        "--dry-run",
        "-n",
        help="dry run, do not rename",
        default=False,
        dest="dry_run",
        action="store_true",
    )
    parser.add_argument(
        "--target-crc32",
        "-C",
        help="add crc32 not target filename",
        default=False,
        dest="target_crc32",
        action="store_true",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    extension = "backup"
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    if config.folder:
        unknown_files = (
            dbs.session.query(anime.LocalFile)
            .filter(
                anime.LocalFile.filename.like(f"%.{extension}"),
                anime.LocalFile.directory.like(f'{config.folder.rstrip("/")}%'),
            )
            .order_by(anime.LocalFile.directory, anime.LocalFile.filename)
            .all()
        )
        # unknown_files = dbs.session.query(anime.LocalFile).filter(anime.LocalFile.filename.like(f'%.{extension}'), anime.LocalFile.directory == config.folder.rstrip('/')).order_by(anime.LocalFile.directory, anime.LocalFile.filename).all()
        [print(unknown_file.ed2k_link()) for unknown_file in unknown_files]
    else:
        unknown_files = (
            dbs.session.query(anime.LocalFile)
            .filter(anime.LocalFile.filename.like(f"%.{extension}"))
            .order_by(anime.LocalFile.directory, anime.LocalFile.filename)
            .all()
        )
    # sys.exit(0)
    for local_file in unknown_files:
        # TODO: replace with removesuffix()
        target_filename = local_file.filename[: -len(extension) - 1]
        if config.target_crc32:
            target_filename = (
                target_filename[: -len(target_filename.split(".")[-1]) - 1]
                + f'[{local_file.hash_crc}].{target_filename.split(".")[-1]}'
            )
        print(f"{local_file.filename} -> {target_filename}")
        target_path = os.path.join(local_file.directory, target_filename)
        if os.path.isfile(target_path):
            print(
                f"local file {local_file.filename} could *not* be renamed, target exists: {target_path}"
            )
        else:
            print(
                f"local file {local_file.filename} could be renamed to {target_filename}"
            )
            if not config.dry_run:
                try:
                    os.rename(
                        os.path.join(local_file.directory, local_file.filename),
                        target_path,
                    )
                    local_file.filename = target_filename
                    dbs.session.commit()
                except Exception:
                    print(f"something wrong with {local_file.filename}")
