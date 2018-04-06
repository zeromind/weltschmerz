#!/usr/bin/python3

import sqlite3


class Connection():
    def __init__(self):
        db = 'weltschmerz.sqlite3'
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def initialise_db(self):
        self.cur.executescript('''CREATE TABLE IF NOT EXISTS anime (
                            aid           INT4     PRIMARY KEY
                                                   NOT NULL
                                                   UNIQUE,
                            year          INT4,
                            type          VARCHAR  NOT NULL,
                            eps           INT4,
                            hep           INT4,
                            seps          INT4,
                            airdate       DATE,
                            enddate       DATE,
                            url           VARCHAR,
                            picname       VARCHAR,
                            rating        INT4,
                            votecount     INT4,
                            tempvote      INT4,
                            tempvcount    INT4,
                            avgreview     INT4,
                            reviewcount   INT4,
                            hrestricted   BOOLEAN,
                            count_sp      INT4,
                            count_other   INT4,
                            count_trailer INT4,
                            count_parody  INT4,
                            last_update   DATETIME
                );
                CREATE TABLE IF NOT EXISTS anime_title (
                            aid        INT NOT NULL,
                            type       INT NOT NULL,
                            lang       VARCHAR NOT NULL,
                            title      VARCHAR NOT NULL,
                            PRIMARY KEY (aid,type,lang),
                            FOREIGN KEY (aid) REFERENCES anime(aid)
                );
                CREATE TABLE IF NOT EXISTS episode (
                            eid        INT     PRIMARY KEY
                                               NOT NULL
                                               UNIQUE,
                            aid        INT     NOT NULL,
                            ep         INT     NOT NULL,
                            airdate    DATE,
                            length     INT,
                            title_en   VARCHAR NOT NULL,
                            title_jp   VARCHAR,
                            title_jp_t VARCHAR,
                            last_update DATETIME,
                            FOREIGN KEY (aid) REFERENCES anime(aid)
                );
                CREATE TABLE IF NOT EXISTS file (
                            fid         INT PRIMARY KEY
                                            UNIQUE
                                            NOT NULL,
                            filesize    INT NOT NULL,
                            original_filename    VARCHAR,
                            aid         INT,
                            eid         INT,
                            gid         INT,
                            source      VARCHAR,
                            video_codec VARCHAR,
                            resolution  VARCHAR,
                            extension   VARCHAR,
                            lang_audio  VARCHAR,
                            lang_subs   VARCHAR,
                            hash_crc    VARCHAR,
                            hash_md5    VARCHAR,
                            hash_sha1   VARCHAR,
                            hash_tth    VARCHAR,
                            hash_ed2k   VARCHAR NOT NULL,
                            last_update DATETIME,
                            FOREIGN KEY (aid) REFERENCES anime(aid),
                            FOREIGN KEY (eid) REFERENCES episode(eid)
                );
                CREATE TABLE IF NOT EXISTS local_file (
                            filename    VARCHAR NOT NULL,
                            directory   VARCHAR NOT NULL,
                            filesize    INT     NOT NULL,
                            fid         INT,
                            aid         INT,
                            hash_crc    VARCHAR,
                            hash_md5    VARCHAR,
                            hash_sha1   VARCHAR,
                            hash_tth    VARCHAR,
                            hash_ed2k   VARCHAR NOT NULL,
                            FOREIGN KEY (fid) REFERENCES file(fid),
                            FOREIGN KEY (aid) REFERENCES anime(aid)
                );
                CREATE TABLE IF NOT EXISTS mylist (
                            ml_id       INT      PRIMARY KEY
                                                 UNIQUE
                                                 NOT NULL,
                            fid         INT      UNIQUE
                                                 NOT NULL,
                            ml_state    INT      NOT NULL,
                            ml_viewed   INT,
                            ml_viewdate DATETIME,
                            ml_storage  VARCHAR,
                            ml_source   VARCHAR,
                            ml_other    VARCHAR,
                            FOREIGN KEY (fid) REFERENCES file(fid)
                );
                CREATE TABLE IF NOT EXISTS relation (
                            aid         INT4 NOT NULL,
                            aid_related INT4 NOT NULL,
                            type        INT4,
                            PRIMARY KEY (aid, aid_related),
                            FOREIGN KEY (aid) REFERENCES anime(aid),
                            FOREIGN KEY (aid_related) REFERENCES anime(aid)
                );''')

    def add_anime(self,
                  data):  # aid,year,type,eps,hep,seps,airdate,enddate,url,picname,rating,votecount,tempvote,tempvcount,avgreview,reviewcount,hrestricted,count_sp,count_other,count_trailer,count_parody,last_update
        self.cur.execute('INSERT OR REPLACE INTO anime VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)

    def add_anime_title(self,
                        data):  # aid,type,lang,title --  # type: 1=primary title (one per anime), 4=official title (one per language)
        self.cur.execute('INSERT OR REPLACE INTO anime VALUES (?,?,?,?)', data)

    def add_episode(self, data):  # (eid,aid,ep,airdate,length,title_en,title_jp,title_jp_t)
        self.cur.execute('INSERT OR REPLACE INTO episode VALUES (?,?,?,?,?,?,?,?)', data)

    def add_file(self,
                 data):  # (fid,filesize,original_filename,aid,eid,gid,source,video_codec,resolution,extension,lang_audio,lang_subs,hash_crc,hash_md5,hash_sha1,hash_tth,hash_ed2k)
        self.cur.execute('INSERT OR REPLACE INTO file VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)

    def add_file_hashed(self, data):
        self.cur.execute(
            'INSERT OR REPLACE INTO local_file (filename, directory, filesize, hash_crc, hash_md5, hash_sha1, hash_ed2k) VALUES (?,?,?,?,?,?,?)',
            data)
        self.conn.commit()

    def shutdown(self):
        self.conn.commit()
        self.conn.close()

    def hashed_files(self):
        self.cur.execute('SELECT directory, filename FROM local_file')
        files = [f for f in self.cur.fetchall()]
        return files

    def hashed_files_size(self):
        self.cur.execute('SELECT directory, filename, filesize FROM local_file')
        files = self.cur.fetchall()
        return files

    def get_dupes(self):
        self.cur.execute(
            'SELECT local_file.hash_sha1, local_file.filename, local_file.directory FROM local_file WHERE (local_file.filesize, local_file.hash_crc, local_file.hash_md5, local_file.hash_ed2k, local_file.hash_sha1) in (select f.filesize, f.hash_crc, f.hash_md5, f.hash_ed2k, f.hash_sha1 from local_file as f group by f.hash_crc, f.hash_md5, f.hash_ed2k, f.hash_sha1 having count(*) >= 2)')
        result = {}
        for file in self.cur.fetchall():
            if file[0] in result:
                result[file[0]].append([file[1:2]])
            else:
                result[file[0]] = [[file[1:2]]]
        return result

    def del_dupe(self, hash_sha1, filename, directory):
        self.cur.execute(
            'DELETE FROM local_file WHERE hash_sha1=:hash_sha1 AND filename=:filename AND directory=:directory',
            {'hash_sha1': hash_sha1, 'filename': filename, 'directory': directory})

    def del_file_by_name(self, filename, directory):
        self.cur.execute('DELETE FROM file WHERE filename=:filename AND directory=:directory', {'filename': filename, 'directory': directory})
