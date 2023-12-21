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
).all()

# adbc.go_online()
files_to_be_added = []
for i, file_not_in_mylist in enumerate(files_not_in_mylist, start=1):
    # mylist_file = (
    #     adbc.dbs.session.query(anime.MylistFile)
    #     .filter(anime.MylistFile.fid == file_not_in_mylist.fid)
    #     .first()
    # )
    # if not mylist_file:
    print(f'need to add file to mylist {file_not_in_mylist.fid} {file_not_in_mylist.filename}')
    print(f"checking files: {i} / {len(files_not_in_mylist)}")
    #files_to_be_added.append(file_not_in_mylist)
    adbc.add_file_to_mylist(file_id=file_not_in_mylist.fid, state=adbc.mylist_state)

# for i, files_to_be_added in enumerate(files_to_be_added, start=1):
#     print(f"adding files: {i} / {len(files_not_in_mylist)}")
#     print(
#         f"need to add file to mylist {files_to_be_added.fid} {files_to_be_added.filename}"
#     )
#     # adbc.add_file_to_mylist(file_id=file_not_in_mylist.fid, state=adbc.mylist_state)
