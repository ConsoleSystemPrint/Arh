import unittest
from Arh import shannon_fano_tree, build_shannon_fano_codes, encode, decode, compress_file, decompress_file
import tempfile
import os


class TestShannonFanoCompression(unittest.TestCase):

    def test_shannon_fano_tree(self):
        symbols = ['A', 'B', 'C', 'D']
        frequencies = [10, 15, 30, 45]
        root = shannon_fano_tree(symbols, frequencies)
        self.assertIsNotNone(root)
        self.assertEqual(len(root.children), 2)

    def test_build_shannon_fano_codes(self):
        symbols = ['A', 'B', 'C', 'D']
        frequencies = [10, 15, 30, 45]
        root = shannon_fano_tree(symbols, frequencies)
        codes = {}
        build_shannon_fano_codes(root, '', codes)
        self.assertEqual(len(codes), len(symbols))
        for symbol in symbols:
            self.assertIn(symbol, codes)
            self.assertIsInstance(codes[symbol], str)

    def test_encode(self):
        codes = {'A': '0', 'B': '10', 'C': '110', 'D': '111'}
        text = 'ABCD'
        encoded_text = encode(text, codes)
        self.assertEqual(encoded_text, '010110111')

    def test_decode(self):
        codes = {'A': '0', 'B': '10', 'C': '110', 'D': '111'}
        text = 'ABCD'
        encoded_text = '010110111'
        root = shannon_fano_tree(list(codes.keys()), [1] * len(codes))  # dummy frequencies
        build_shannon_fano_codes(root, '', {})
        decoded_text = decode(encoded_text, root)
        self.assertEqual(decoded_text, text)

    def test_file_compression_decompression(self):
        original_text = "This is a test text for Shannon-Fano compression."

        with tempfile.NamedTemporaryFile(delete=False) as input_file:
            input_file.write(original_text.encode('utf-8'))
            input_name = input_file.name

        with tempfile.NamedTemporaryFile(delete=False) as compressed_file:
            compressed_name = compressed_file.name

        with tempfile.NamedTemporaryFile(delete=False) as decompressed_file:
            decompressed_name = decompressed_file.name

        try:
            compress_file(input_name, compressed_name)
            decompress_file(compressed_name, decompressed_name)

            with open(decompressed_name, 'r') as f:
                decompressed_text = f.read()

            self.assertEqual(decompressed_text, original_text)

        finally:
            os.remove(input_name)
            os.remove(compressed_name)
            os.remove(decompressed_name)


if __name__ == '__main__':
    unittest.main()