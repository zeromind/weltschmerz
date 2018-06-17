#!/usr/bin/python3

import hashlib
import os.path
import zlib
import time
from threading import Thread, Semaphore

# Use the chunk size for calculating ed2k as block size
BLOCKSIZE = 9728000


class T(Thread):
    def __init__(self, h, o):
        self.h = h
        self.o = o
        self.ready = Semaphore(0)
        self.idle = Semaphore(0)
        Thread.__init__(self)

    def run(self):
        while True:
            self.idle.release()
            self.ready.acquire()
            if not len(self.o[0]):
                return
            self.h.update(self.o[0])


class Crc32:
    def __init__(self):
        self.v = 0

    def update(self, x):
        self.v = zlib.crc32(x, self.v)

    def hexdigest(self):
        return '%08x' % (self.v & 0xffffffff)


class Ed2k:
    def __init__(self, file_size):
        self.v = hashlib.new('md4')
        self.file_size = file_size

    def update(self, x):
        if not (self.file_size < BLOCKSIZE):
            md4data = hashlib.new('md4')
            md4data.update(x)
            self.v.update(md4data.digest())
        else:
            self.v.update(x)

    def hexdigest(self):
        return self.v.hexdigest()


class FileHash:
    def __init__(self, directory, filename):
        self.directory = directory
        self.filename = filename
        self.filesize = os.path.getsize(os.path.join(directory, filename))
        start = time.time()
        (self.crc32, self.md5, self.sha1, self.ed2k) = self.hash_file()
        end = time.time()
        self.hash_duration = end - start

    def hash_file(self):
        """Creates multiple hashes for a file in one go.

            Returns file name, size, crc32, md5, sha1, ed2k.
            Uses the red variant of ed2k. Info: http://wiki.anidb.net/w/Ed2k-hash
        """
        hashes = {'ed2k': Ed2k(self.filesize), 'sha1': hashlib.sha1(), 'md5': hashlib.md5(), 'crc32': Crc32()}
        data = [b'']
        threads = [T(h, data) for n, h in hashes.items()]
        [t.start() for t in threads]
        with open(os.path.join(self.directory, self.filename), 'rb') as f:
            while True:
                data.append(f.read(BLOCKSIZE))
                [t.idle.acquire() for t in threads]
                del data[0]
                [t.ready.release() for t in threads]
                if not len(data[0]):
                    break
        [t.join() for t in threads]
        return ([hashes[h].hexdigest() for h in ['crc32', 'md5', 'sha1', 'ed2k']])

    def ed2k_link(self):
        return 'ed2k://|file|{file}|{size}|{ed2k}|/'.format(file=self.filename, size=self.filesize, ed2k=self.ed2k)


if __name__ == '__main__':
    import sys

    for filename in sys.argv[1:]:
        try:
            file_info = FileHash(*os.path.split(filename))
            print(file_info.ed2k_link())
        except IndexError:
            print('must specify a filename')
        except IOError as err:
            print('error:', err)
