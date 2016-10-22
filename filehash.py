#!/usr/bin/python3

import hashlib
import os.path
import zlib


class FileHash:
    def __init__(self, filename):
        self.filename = filename
        self.filesize = os.path.getsize(filename)
        (self.crc32, self.md5, self.sha1, self.ed2k) = self.hash_file()

    def hash_file(self):
        '''Creates multiple hashes for a file in one go.

            Returns file name, size, crc32, md5, sha1, ed2k.
            Uses the red variant of ed2k. Info: http://wiki.anidb.net/w/Ed2k-hash
        '''
        block_size = 9728000
        crc32 = 0
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        ed2k = hashlib.new('md4')
        with open(self.filename, 'rb') as f:
            while True:
                data = f.read(block_size)
                crc32 = zlib.crc32(data, crc32)
                md5.update(data)
                sha1.update(data)
                if not data:
                    break
                if not (self.filesize < block_size):
                    md4data = hashlib.new('md4')
                    md4data.update(data)
                    ed2k.update(md4data.digest())
                else:
                    ed2k.update(data)
        return ("%08x" % (crc32 & 0xffffffff)).lower(), md5.hexdigest(), sha1.hexdigest(), ed2k.hexdigest()


if __name__ == '__main__':
    import sys

    try:
        file_info = FileHash(sys.argv[1])
        print((file_info.filename, file_info.filesize, file_info.crc32, file_info.md5, file_info.sha1, file_info.ed2k))
    except IndexError:
        print('must specify a filename')
    except IOError as err:
        print('error:', err)
