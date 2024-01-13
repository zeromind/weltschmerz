#!/usr/bin/python3
import anidb
import anime


config = anidb.get_config()
adbc = anidb.AniDBClient(
    config.database,
    False,
    anidb.FMASK,
    anidb.FAMASK,
    config.online,
    config.anidb_username,
    config.anidb_password,
    config.anidb_udp_api_key,
    config.mylist_state,
    config.debug,
)
adbc.online = True
adbc.debug = True
files_not_in_mylist = (
    adbc.dbs.session.query(anime.LocalFile)
    .outerjoin(anime.MylistFile, anime.LocalFile.fid == anime.MylistFile.fid)
    .filter(anime.LocalFile.fid != None)
    .filter(anime.MylistFile.fid == None)
    .order_by(anime.LocalFile.fid.desc())
).all()
for i, file_not_in_mylist in enumerate(files_not_in_mylist, start=1):
    print(f'need to add file to mylist {file_not_in_mylist.fid} {file_not_in_mylist.filename}')
    print(f"checking files: {i} / {len(files_not_in_mylist)}")
    adbc.add_file_to_mylist(file_id=file_not_in_mylist.fid, state=adbc.mylist_state)
