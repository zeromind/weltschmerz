#!/usr/bin/python3

import click
import weltschmerz.anidb as anidb
import weltschmerz.filehasher as filehasher
import weltschmerz.remove_deleted as remove_deleted
import weltschmerz.remove_changed as remove_changed
import weltschmerz.delete_duplicates as delete_duplicates
import weltschmerz.move_files as move_files
import configparser
import os
from typing import List, Tuple, Union

CONFIG_FILES = ["weltschmerz.cfg", "~/.config/weltschmerz/weltschmerz.cfg"]


config = configparser.ConfigParser()
for cf in CONFIG_FILES:
    _cf = os.path.expanduser(cf)
    if os.path.isfile(_cf):
        config.read_file(open(_cf))
        break


@click.group()
@click.option(
    "--database", help="database to use", default=config.get("client", "database")
)
@click.option("--log-file", help="log file to use")
@click.pass_context
def cli(ctx, database: str, log_file: str):
    ctx.ensure_object(dict)
    ctx.obj["DATABASE"] = database
    ctx.obj["LOG_FILE"] = log_file
    pass


##############################################
# files
##############################################
@cli.group("files", help="manage file data")
def files_group():
    pass


#######################
# files hash
#######################
@files_group.command(name="hash", help="hash files")
@click.option(
    "--folder",
    "folders",
    multiple=True,
    required=True,
    type=click.Path(exists=True, readable=True, resolve_path=True),
    help="folders to process",
)
@click.option(
    "--folder-exclude", "folders_exclude", multiple=True, help="folders to exclude"
)
@click.option(
    "--foldername-exclude",
    "foldernames_exclude",
    multiple=True,
    help="folder names to exclude",
)
@click.option(
    "--file-extension",
    "file_extensions",
    multiple=True,
    help="file extensions to process",
)
@click.pass_context
def files_hash(
    ctx,
    folders: List[str],
    folders_exclude: List[str],
    foldernames_exclude: List[str],
    file_extensions: List[str],
):
    filehasher.hash_files(
        database=ctx.obj["DATABASE"],
        folders=folders,
        folders_exclude=folders_exclude,
        foldernames_exclude=foldernames_exclude,
        file_extensions=file_extensions,
    )


#######################
# files remove-deleted
#######################
@files_group.command(name="remove-deleted", help="remove deleted files from database")
@click.argument(
    "folders",
    nargs=-1,
    required=False,
    type=click.Path(exists=False, resolve_path=True),
)
@click.option(
    "-n",
    "--noop",
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="dry-run",
)
@click.pass_context
def files_remove_deleted(ctx, folders: List[str], dry_run: bool = False):
    for folder in folders:
        click.echo(folder)
        remove_deleted.remove_deleted_files(
            database=ctx.obj["DATABASE"],
            folder=folder,
            dry_run=dry_run,
        )


#######################
# files remove-changed
#######################
@files_group.command(
    name="remove-changed",
    help="remove files that changed in size from database",
)
@click.argument(
    "folders",
    nargs=-1,
    required=False,
    type=click.Path(exists=False, resolve_path=True),
)
@click.option(
    "-n",
    "--noop",
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="dry-run",
)
@click.pass_context
def files_remove_changed(ctx, folders: List[str], dry_run: bool = False):
    for folder in folders:
        click.echo(folder)
        remove_changed.remove_changed_files(
            database=ctx.obj["DATABASE"],
            folder=folder,
            dry_run=dry_run,
        )


#######################
# files remove-dupes
#######################
@files_group.command(
    name="delete-duplicates",
    help="remove&delete duplicate files from database/disk",
)
@click.option(
    "--preferred-directory-pattern",
    "preferred_directory_pattern",
    required=False,
)
@click.option(
    "-n",
    "--noop",
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="dry-run",
)
@click.pass_context
def files_delete_duplicates(ctx, preferred_directory_pattern: str, dry_run: bool = False):
    delete_duplicates.remove_duplicate_files(
        database=ctx.obj["DATABASE"],
        preferred_directory_pattern=preferred_directory_pattern,
        dry_run=dry_run,
    )


#######################
# files sort
#######################
@files_group.command(name="sort", help="sort files")
@click.option(
    "--source-folder",
    "source_folders",
    multiple=True,
    required=True,
    type=click.Path(exists=True, readable=True, resolve_path=True),
    help="source folders",
)
@click.option(
    "--target-folder",
    "target_folder",
    type=click.Path(
        exists=True,
        readable=True,
        writable=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    required=True,
    help="target folder",
)
@click.option(
    "-n",
    "--noop",
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="dry-run",
)
@click.option(
    "-C",
    "--target-crc32",
    "target_crc32",
    is_flag=True,
    default=False,
    help="whether to append CRC32 to filename",
)
@click.pass_context
def files_sort(
    ctx,
    source_folders: List[str],
    target_folder: str,
    target_crc32: bool = False,
    dry_run: bool = False,
):
    for source_folder in source_folders:
        click.echo(source_folder)
        move_files.sort_files(
            database=ctx.obj["DATABASE"],
            source_folder=source_folder,
            target_folder=target_folder,
            target_crc32=target_crc32,
            dry_run=dry_run,
        )


##############################################
# anidb
##############################################
@cli.group("anidb", help="manage AniDB data")
@click.option(
    "--username",
    help="AniDB user name",
    default=config.get("anidb", "username", fallback=None),
)
@click.option(
    "--password",
    help="AniDB user password",
    default=config.get("anidb", "password", fallback=None),
)
@click.option(
    "--udp-api-key",
    help="AniDB user UDP API key",
    default=config.get("anidb", "udp_api_key", fallback=None),
)
@click.pass_context
def anidb_group(ctx, username: str, password: str, udp_api_key: str):
    ctx.ensure_object(dict)
    ctx.obj["ANIDB_USER_NAME"] = username
    ctx.obj["ANIDB_USER_PASSWORD"] = password
    ctx.obj["ANIDB_USER_UDP_API_KEY"] = udp_api_key
    pass


#######################
# anidb lookup-files
#######################
@anidb_group.command(name="lookup-files", help="lookup files")
@click.option(
    "--folder",
    "folders",
    multiple=True,
    required=False,
    type=click.Path(exists=False, resolve_path=True),
    help="folders to process",
    default=["/"],
)
@click.option(
    "--db-verbose",
    "db_verbose",
    is_flag=True,
    default=False,
    help="verbose mode for database",
)
@click.option(
    "-d",
    "--debug",
    "debug",
    is_flag=True,
    default=False,
    help="debug output",
)
@click.option(
    "-M",
    "--add-to-mylist",
    "add_to_mylist",
    is_flag=True,
    default=False,
    help="add known files to AniDB mylist",
)
@click.option(
    "-m",
    "--mylist-state",
    "mylist_state",
    type=click.IntRange(0, 4),
    default=4,
    help="mylist state",
)
@click.option(
    "--online/--offline",
    "online",
    default=False,
    help="whether to ask AniDB for file info (database cache only otherwise)",
)
@click.pass_context
def anidb_lookup_files(
    ctx,
    db_verbose: bool = False,
    online: bool = False,
    add_to_mylist: bool = False,
    mylist_state: int = 4,
    debug: bool = False,
    folders: Union[List[str], None] = None,
):
    if online:
        if not (
            ctx.obj["ANIDB_USER_NAME"]
            and ctx.obj["ANIDB_USER_PASSWORD"]
            and ctx.obj["ANIDB_USER_UDP_API_KEY"]
        ):
            click.echo("no AniDB credentials configured")
            return 1
        anidb.lookup_files(
            database=ctx.obj["DATABASE"],
            database_verbose=db_verbose,
            folders=folders,
            online=online,
            add_to_mylist=add_to_mylist,
            mylist_state=mylist_state,
            anidb_username=ctx.obj["ANIDB_USER_NAME"],
            anidb_password=ctx.obj["ANIDB_USER_PASSWORD"],
            anidb_udp_api_key=ctx.obj["ANIDB_USER_UDP_API_KEY"],
            debug=debug,
        )
    else:
        anidb.lookup_files(
            database=ctx.obj["DATABASE"],
            database_verbose=db_verbose,
            folders=folders,
            online=online,
            debug=debug,
        )


#######################
# main
#######################
if __name__ == "__main__":
    cli(obj={})
