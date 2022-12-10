#!/usr/bin/python3

import xmltodict
import sys
import anime
import configparser
import os
import argparse
import queue
import threading

THREADS = 2

def get_config(config_file: str = 'weltschmerz.cfg'):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))

    parser = argparse.ArgumentParser(
        description='Remove files that changed in size from database.')
    parser.add_argument('--database', help='database to use',
                        default=config.get('client', 'database'))
    parser.add_argument('--log-file', dest='log_file', help='logfile to use',
                        default=config.get('client', 'log'))
    parser.add_argument('--mylist-xml-files', nargs='+', help='mylist export: xml-plain-full anime files to process')

    args = parser.parse_args()
    return args


def xml_parser():
    while True:
        with open(q_in.get(), 'r') as f:
                anime_xml = f.read()
                anime_data = xmltodict.parse(anime_xml)
                q_out.put(anime_data)
                q_in.task_done()


def dict_to_mylist_anime_worker():
    while True:
        anime_data = q_out.get()
        anime_anime = anime.Anime(
            aid = anime_data['anime']['id'],
            year = anime_data['anime']['year'],
            )
        anime_mylist_anime = anime.MylistAnime(
                    aid = anime_data['anime']['id'],
                    ml_count_episodes = anime_data['anime']['mylist_entry']['count']['@eps'],
                    ml_count_specials = anime_data['anime']['mylist_entry']['count']['@specials'],
                    ml_count_total = anime_data['anime']['mylist_entry']['count']['@total'],
                    ml_watched_episodes = anime_data['anime']['mylist_entry']['watched']['@eps'],
                    ml_watched_specials = anime_data['anime']['mylist_entry']['watched']['@specials'],
                    ml_watched_total = anime_data['anime']['mylist_entry']['watched']['@total'],
                )
        print(anime_mylist_anime.aid)
        dbs.session.merge(anime_anime)
        dbs.session.merge(anime_mylist_anime)
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
    
    for i in range(1,THREADS):
        workers[i] = threading.Thread(target=xml_parser)
        workers[i].daemon = True
        workers[i].start()
    
    db_worker = threading.Thread(target=dict_to_mylist_anime_worker)
    db_worker.daemon = True
    db_worker.start()


    q_in.join()
    q_out.join()
