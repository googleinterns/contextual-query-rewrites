import unittest
import translate_utils
import os
import shutil


class TestRawData(unittest.TestCase):
    def test_translate_text(self):
        file = open("dummy_file.txt", 'w')
        file.write(" Ram \n")
        file.close()

        translate_utils.translate_data("dummy_file.txt", "dummy_output.txt")

        data = open("dummy_output.txt", 'r').readlines()
        print(data)
        expected = ['राम\n']
        self.assertEqual(data, expected)

    def test_translate_text_batch(self):
        file = open("dummy_file.txt", 'w')
        file.write(" Ram \n")
        file.close()

        translate_utils.translate_data("dummy_file.txt",
                                       "dummy_output.txt",
                                       threshold=0)

        data = open("dummy_output.txt", 'r').readlines()
        print(data)
        expected = ['राम\n']
        self.assertEqual(data, expected)

    def test_translate_text_dir(self):
        shutil.rmtree('./test_dummy_dir')
        os.mkdir('./test_dummy_dir')
        file = open("./test_dummy_dir/dummy_file.txt", 'w')
        file.write(" Ram \n")
        file.close()

        translate_utils.translate_data("./test_dummy_dir",
                                       "dummy_output.txt",
                                       threshold=0)

        data = open("dummy_output.txt", 'r').readlines()
        print(data)
        expected = ['राम\n']
        self.assertEqual(data, expected)


if __name__ == '__main__':
    unittest.main()
