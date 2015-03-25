#!/usr/bin/python3

import hashlib
import os.path
import zlib

def hash_file(filename):
    '''Creates multiple hashes for a file in one go.

        Returns file name, size, crc32, md5, sha1, ed2k.
        Uses the red variant of ed2k. Info: http://wiki.anidb.net/w/Ed2k-hash

    '''
    block_size = 9728000
    crc32 = 0
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    ed2k = hashlib.new('md4')
    filesize = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        while True:
            data = f.read(block_size)
            crc32 = zlib.crc32(data, crc32)
            md5.update(data)
            sha1.update(data)
            if not (filesize < block_size):
                md4data = hashlib.new('md4')
                md4data.update(data)
                ed2k.update(md4data.digest())
            else:
                ed2k.update(data)
            if not data:
                break
    return (filename, filesize, str.lower("%08x"%(crc32 & 0xffffffff)), md5.hexdigest(), sha1.hexdigest(), ed2k.hexdigest())

if __name__ == '__main__':
    import sys
    try:
        print(hash_file(sys.argv[1]))
    except IndexError:
        print('must specify a filename')
    except IOError as err:
        print('error:', err)
