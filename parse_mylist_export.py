#!/usr/bin/python3

import xmltodict
import sys
import weltschmerz.anime as anime
import configparser
import argparse
import queue
import threading
import datetime

THREADS = 2


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
    parser.add_argument(
        "--mylist-xml-files",
        nargs="+",
        help="mylist export: xml-plain-full anime files to process",
    )

    args = parser.parse_args()
    return args


def xml_parser():
    while True:
        with open(q_in.get(), "r") as f:
            anime_xml = f.read()
            anime_data = xmltodict.parse(
                anime_xml,
                force_list=("episode", "file", "eprelation", "filerelation"),
            )
            q_out.put(anime_data)
            q_in.task_done()


def try_parse_date(date_str: str, format_str: str):
    try:
        return datetime.datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def not_empty(var):
    if var != "-" or "":
        return var
    else:
        return None


def dict_to_mylist_anime_worker():
    while True:
        anime_data = q_out.get()
        aired = try_parse_date(anime_data["anime"]["startdate"]["long"], "%d.%m.%Y")
        ended = try_parse_date(anime_data["anime"]["enddate"]["long"], "%d.%m.%Y")
        anime_anime = anime.Anime(
            aid=anime_data["anime"]["id"],
            year=anime_data["anime"]["year"],
            type=anime_data["anime"]["type"]["@id"],
            eps=anime_data["anime"]["count"]["@eps"],
            seps=anime_data["anime"]["count"]["@specials"],
            airdate=aired,
            enddate=ended,
            rating=not_empty(anime_data["anime"]["rating"]),
            votecount=not_empty(anime_data["anime"]["votes"]),
            tempvote=not_empty(anime_data["anime"]["tmprating"]),
            tempvcount=not_empty(anime_data["anime"]["tmpvotes"]),
            avgreview=not_empty(anime_data["anime"]["reviewrating"]),
            reviewcount=not_empty(anime_data["anime"]["reviews"]),
        )
        dbs.session.merge(anime_anime)
        # load anime from db to get related episodes etc.
        anime_anime = (
            dbs.session.query(anime.Anime)
            .filter(anime.Anime.aid == anime_data["anime"]["id"])
            .one()
        )
        anime_mylist_anime = anime.MylistAnime(
            aid=anime_data["anime"]["id"],
            ml_count_episodes=anime_data["anime"]["mylist_entry"]["count"]["@eps"],
            ml_count_specials=anime_data["anime"]["mylist_entry"]["count"]["@specials"],
            ml_count_total=anime_data["anime"]["mylist_entry"]["count"]["@total"],
            ml_watched_episodes=anime_data["anime"]["mylist_entry"]["watched"]["@eps"],
            ml_watched_specials=anime_data["anime"]["mylist_entry"]["watched"][
                "@specials"
            ],
            ml_watched_total=anime_data["anime"]["mylist_entry"]["watched"]["@total"],
        )

        print(
            f"anime: {anime_mylist_anime.aid} - eps: {anime_mylist_anime.ml_count_episodes} - watched: {anime_mylist_anime.ml_watched_episodes}"
        )
        dbs.session.merge(anime_mylist_anime)
        # mylist export contains wishlisted anime,
        # so anime may have no episodes/files in mylist
        # resulting xml contains empty episodes element
        if not anime_data["anime"]["episodes"]:
            q_out.task_done()
            continue
        for episode in anime_data["anime"]["episodes"]["episode"]:
            try:
                aired = datetime.datetime.strptime(
                    episode["aired"]["#text"], "%d.%m.%Y %H:%M"
                )
            except ValueError:
                aired = None
            try:
                episode_update = datetime.datetime.strptime(
                    episode["update"]["#text"], "%d.%m.%Y %H:%M"
                )
            except ValueError:
                episode_update = None

            anime_episode = anime.Episode(
                eid=episode["@id"],
                aid=anime_data["anime"]["id"],
                ep=episode["@number"],
                airdate=aired,
                length=episode["length"],
                title_en=episode["name"],
                last_update=episode_update,
            )
            if "name_kanji" in episode.keys():
                anime_episode.title_jp = episode["name_kanji"]
            if "name_romaji" in episode.keys():
                anime_episode.title_jp_t = episode["name_romaji"]
            dbs.session.merge(anime_episode)
            if dbs.session.dirty:
                dbs.session.commit()
            for file in episode["files"]["file"]:
                # generic files are 0 bytes
                # skip them for now
                if int(file["size_plain"]) == 0:
                    continue
                # files containing multiple episodes have episode relations, can't track those atm
                # skip them for now, when the current episode is from an ep relation
                if (
                    file["eprelations"]
                    and "eprelation" in file["eprelations"].keys()
                    and len(file["eprelations"]["eprelation"]) >= 1
                ):
                    if episode["@id"] in [
                        eprel["@eid"] for eprel in file["eprelations"]["eprelation"]
                    ]:
                        continue
                try:
                    file_update = datetime.datetime.strptime(
                        episode["update"]["#text"], "%d.%m.%Y %H:%M"
                    )
                except ValueError:
                    file_update = None
                anime_file = anime.File(
                    fid=file["@id"],
                    filesize=file["size_plain"],
                    aid=anime_data["anime"]["id"],
                    eid=episode["@id"],
                    gid=file["group"]["@id"],
                    source=file["source"],
                    extension=file["filetype"],
                    hash_crc=file["hash_crc"] or None,
                    hash_md5=file["hash_md5"] or None,
                    hash_sha1=file["hash_sha1"] or None,
                    hash_tth=file["hash_tth"] or None,
                    hash_ed2k=file["hash_ed2k"]["key"],
                    last_update=file_update,
                )
                dbs.session.merge(anime_file)
                if dbs.session.dirty:
                    dbs.session.commit()
                try:
                    view_date = datetime.datetime.strptime(
                        file["viewdate"]["long"], "%d.%m.%Y %H:%M"
                    )
                except ValueError:
                    view_date = None
                anime_mylist_file = anime.MylistFile(
                    fid=file["@id"],
                    ml_state=file["mystate"]["@id"],
                    ml_viewed=file["state"]["iswatched"],
                    ml_viewdate=view_date,
                    ml_storage=file["storage"],
                    ml_source=file["source"],
                )
                dbs.session.merge(anime_mylist_file)
                if dbs.session.dirty:
                    dbs.session.commit()
                file_screenshots = (
                    dbs.session.query(anime.TitleScreenShot)
                    .filter(anime.TitleScreenShot.fid == anime_file.fid)
                    .all()
                )
                for file_screenshot in file_screenshots:
                    if (
                        file_screenshot.aid != anime_file.aid
                        or file_screenshot.eid != anime_file.eid
                    ):
                        file_screenshot.aid = anime_file.aid
                        file_screenshot.eid = anime_file.eid
                        dbs.session.merge(file_screenshot)
                        if dbs.session.dirty:
                            dbs.session.commit()

        print(
            f"anime: {anime_mylist_anime.aid} - eps: {anime_mylist_anime.ml_count_episodes} - watched: {anime_mylist_anime.ml_watched_episodes} done"
        )
        if dbs.session.dirty:
            dbs.session.commit()
        q_out.task_done()


if __name__ == "__main__":
    config = get_config()
    dbs = anime.DatabaseSession(config.database, False)
    mylist_anime = []
    workers = {}
    q_in = queue.Queue()
    q_out = queue.Queue()

    for mylist_xml_file in config.mylist_xml_files:
        q_in.put(mylist_xml_file)

    for i in range(1, THREADS):
        workers[i] = threading.Thread(target=xml_parser)
        workers[i].daemon = True
        workers[i].start()

    db_worker = threading.Thread(target=dict_to_mylist_anime_worker)
    db_worker.daemon = True
    db_worker.start()

    q_in.join()
    q_out.join()
