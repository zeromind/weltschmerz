#!/usr/bin/python3

# import anime titles from an AniDB title dump
# create filesystem hierarchy from AniDB title dump
# see https://wiki.anidb.net/API#Anime_Titles
# usage: animetitle.py <titledump> <target_folder>

import xml.etree.ElementTree as ET
import sys
import os.path
import os
import re
import html

FN_BLACKLIST = ['\'', '\\', ':', '"', '*', '?']
AID_PAD_WIDTH = 6
AID_CHUNK_SIZE = 2


def parse_file(filename):
    anime_list = {}
    tree = ET.parse(filename)
    root = tree.getroot()
    for anime in root:
        if anime.attrib['aid'] not in anime_list:
            anime_list[anime.attrib['aid']] = []
        for atitle in anime:
            anime_list[anime.attrib['aid']].append((atitle.attrib['type'], atitle.attrib['{http://www.w3.org/XML/1998/namespace}lang'], html.unescape(atitle.text)))
    return anime_list


if __name__ == "__main__":
    import sys

    source_file = sys.argv[1]
    target_path = sys.argv[2]
    data = parse_file(source_file)
    for aid in data:
        aid_path = aid.zfill(AID_PAD_WIDTH)
        aid_path = '/'.join( [ aid_path[i:i+AID_CHUNK_SIZE] for i in range(0, AID_PAD_WIDTH, AID_CHUNK_SIZE) ] )
        main_title_lang = ''
        print(aid_path)
        if os.path.exists(os.path.join(target_path, 'by-id', aid_path)):
            for title in data[aid]:
                if title[0] in ('main'):
                    main_title_lang = title[1]
                    title_sane = re.sub('\.$', '。', title[2].translate(str.maketrans('/', '⁄', ''.join(FN_BLACKLIST))))
                    if not os.path.exists(os.path.join(target_path, 'by-name', title[0], title_sane)):
                        os.symlink(os.path.join('../..', 'by-id', aid_path), os.path.join(target_path, 'by-name', title[0], title_sane))
            for title in data[aid]:
                if title[0] == 'official' and main_title_lang == ''.join(('x-', title[1], 't')):
                    title_sane = re.sub('\.$', '。', title[2].translate(str.maketrans('/', '⁄', ''.join(FN_BLACKLIST))))
                    if not os.path.exists(os.path.join(target_path, 'by-name', title[0], title_sane)):
                        os.symlink(os.path.join('../..', 'by-id', aid_path), os.path.join(target_path, 'by-name', title[0], title_sane))
                if title[0] == 'official' and title[1] == 'en':
                    title_sane = re.sub('\.$', '。', title[2].translate(str.maketrans('/', '⁄', ''.join(FN_BLACKLIST))))
                    if not os.path.exists(os.path.join(target_path, 'by-name', 'english', title_sane)):
                        os.symlink(os.path.join('../..', 'by-id', aid_path), os.path.join(target_path, 'by-name', 'english', title_sane))
