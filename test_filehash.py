#!/usr/bin/python3

import unittest
import filehash


class TestFilehash(unittest.TestCase):

    def test_ed2k_empty(self):
        empty_file_ed2k = filehash.Ed2k()
        empty_file_ed2k.update(b'')
        self.assertEqual(empty_file_ed2k.hexdigest(), '31d6cfe0d16ae931b73c59d7e0c089c0')

    def test_ed2k_file_of_zeroes_chunk_sized(self):
        ed2k_file_of_zeroes_chunk_sized = filehash.Ed2k()
        ed2k_file_of_zeroes_chunk_sized.update(b'\00' * 9728000)
        self.assertEqual(ed2k_file_of_zeroes_chunk_sized.hexdigest(), 'fc21d9af828f92a8df64beac3357425d')

    def test_ed2k_file_of_zeroes_double_chunk_sized(self):
        test_ed2k_file_of_zeroes_double_chunk_sized = filehash.Ed2k()
        test_ed2k_file_of_zeroes_double_chunk_sized.update(b'\00' * 9728000 * 2)
        self.assertEqual(test_ed2k_file_of_zeroes_double_chunk_sized.hexdigest(), '114b21c63a74b6ca922291a11177dd5c')

    def test_crc32_empty(self):
        empty_file_crc32 = filehash.Crc32()
        empty_file_crc32.update(b'')
        self.assertEqual(empty_file_crc32.hexdigest(), '00000000')

    def test_crc32_file_of_zeroes_chunk_sized(self):
        empty_file_crc32 = filehash.Crc32()
        empty_file_crc32.update(b'\00' * 9728000)
        self.assertEqual(empty_file_crc32.hexdigest(), '3abc06ba')


if __name__ == '__main__':
    unittest.main()
