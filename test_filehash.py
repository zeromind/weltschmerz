#!/usr/bin/python3

import unittest
import filehash


class TestFilehash(unittest.TestCase):

    def test_ed2k_empty(self):
        ed2k_empty = filehash.Ed2k()
        ed2k_empty.update(b'')
        self.assertEqual(ed2k_empty.hexdigest(), '31d6cfe0d16ae931b73c59d7e0c089c0')

    def test_ed2k_chunk_of_zeroes(self):
        ed2k_chunk_of_zeroes = filehash.Ed2k()
        ed2k_chunk_of_zeroes.update(b'\00' * 9728000)
        self.assertEqual(ed2k_chunk_of_zeroes.hexdigest(), 'fc21d9af828f92a8df64beac3357425d')

    def test_ed2k_double_chunk_of_zeroes(self):
        ed2k_double_chunk_of_zeroes = filehash.Ed2k()
        ed2k_double_chunk_of_zeroes.update(b'\00' * 9728000 * 2)
        self.assertEqual(ed2k_double_chunk_of_zeroes.hexdigest(), '114b21c63a74b6ca922291a11177dd5c')

    def test_crc32_empty(self):
        crc32_empty = filehash.Crc32()
        crc32_empty.update(b'')
        self.assertEqual(crc32_empty.hexdigest(), '00000000')

    def test_crc32_chunk_of_zeroes(self):
        crc32_chunk_of_zeroes = filehash.Crc32()
        crc32_chunk_of_zeroes.update(b'\00' * 9728000)
        self.assertEqual(crc32_chunk_of_zeroes.hexdigest(), '3abc06ba')


if __name__ == '__main__':
    unittest.main()
