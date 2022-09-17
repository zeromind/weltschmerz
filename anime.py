from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, BigInteger, String, Date, Boolean, ForeignKey, Index
from sqlalchemy.orm import sessionmaker
import os.path

Base = declarative_base()


class Anime(Base):
    __tablename__ = 'anime'
    aid = Column(Integer, unique=True, primary_key=True, default=None)
    year = Column(Integer)
    type = Column(String)
    eps = Column(Integer)
    hep = Column(Integer)
    seps = Column(Integer)
    airdate = Column(Date)
    enddate = Column(Date)
    url = Column(String)
    picname = Column(String)
    rating = Column(Integer)
    votecount = Column(Integer)
    tempvote = Column(Integer)
    tempvcount = Column(Integer)
    avgreview = Column(Integer)
    reviewcount = Column(Integer)
    hrestricted = Column(Boolean)
    count_sp = Column(Integer)
    count_other = Column(Integer)
    count_trailer = Column(Integer)
    count_parody = Column(Integer)
    last_update = Column(Date)


class AnimeTitle(Base):
    __tablename__ = 'anime_title'
    aid = Column(Integer, ForeignKey('anime.aid'))
    type = Column(Integer, nullable=False, primary_key=True)
    lang = Column(String, nullable=False, primary_key=True)
    title = Column(String, nullable=False, primary_key=True)


class Episode(Base):
    __tablename__ = 'episode'
    eid = Column(Integer, primary_key=True, default=None)
    aid = Column(Integer, ForeignKey('anime.aid'))
    ep = Column(Integer)
    airdate = Column(Date)
    length = Column(Integer)
    title_en = Column(String)
    title_jp = Column(String)
    title_jp_t = Column(String)
    last_update = Column(Date)


class File(Base):
    __tablename__ = 'file'
    fid = Column(Integer, primary_key=True, default=None)
    filesize = Column(BigInteger, nullable=False)
    original_filename = Column(String)
    aid = Column(Integer, ForeignKey('anime.aid'))
    eid = Column(Integer, ForeignKey('episode.eid'))
    gid = Column(Integer)
    source = Column(String)
    video_codec = Column(String)
    resolution = Column(String)
    extension = Column(String)
    lang_audio = Column(String)
    lang_subs = Column(String)
    hash_crc = Column(String)
    hash_md5 = Column(String)
    hash_sha1 = Column(String)
    hash_tth = Column(String)
    hash_ed2k = Column(String, nullable=False)
    last_update = Column(Date)
    __table_args__ = (
        Index('idx_file_hash_ed2k', 'hash_ed2k', 'filesize', unique=True),
    )


class LocalFile(Base):
    __tablename__ = 'local_file'
    filename = Column(String, nullable=False, primary_key=True)
    directory = Column(String, nullable=False, primary_key=True)
    filesize = Column(BigInteger, nullable=False)
    fid = Column(Integer, ForeignKey('file.fid'))
    aid = Column(Integer, ForeignKey('anime.aid'))
    hash_crc = Column(String)
    hash_md5 = Column(String)
    hash_sha1 = Column(String)
    hash_tth = Column(String)
    hash_ed2k = Column(String, nullable=False)
    __table_args__ = (
        Index('idx_local_file_path_size', 'directory',
              'filename', 'filesize', unique=True),
        Index('idx_local_file_hash_ed2k', 'hash_ed2k', 'filesize', unique=False),
    )
    @property
    def ed2k_link(self) -> str:
        return f'ed2k://|file|{self.filename}|{self.filesize}|{self.hash_ed2k}|/'
    @property
    def full_path(self) -> str:
        return os.path.join(self.directory, self.filename)


class MylistFile(Base):
    __tablename__ = 'mylist'
    ml_id = Column(BigInteger, nullable=False, primary_key=True, default=None)
    fid = Column(BigInteger, ForeignKey('file.fid'), nullable=False)
    ml_state = Column(Integer, nullable=False)
    ml_viewed = Column(Integer)
    ml_viewdate = Column(Date)
    ml_storage = Column(String)
    ml_source = Column(String)
    ml_other = Column(String)


class DatabaseSession():
    def __init__(self, db='sqlite:///:memory:', echo=False):
        engine = create_engine(db, echo=echo)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
