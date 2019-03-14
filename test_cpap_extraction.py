import unittest
from mock import Mock
from mock import patch
import cpap_extraction
import os

class TestHelloWorld(unittest.TestCase):
    def setup(self):
        pass

    def test_return(self):
        self.assertEqual(cpap_extraction.hello_world(), 0)

class TestCopyFile(unittest.TestCase):
    def setup(self):
        pass

    @patch('cpap_extraction.write_file')
    @patch('cpap_extraction.read_file', return_value='xx')
    def testCopy(self, mocked_source, mocked_output):
        # TODO: This doesn't seem to actually work, I'll try and get some help
        cpap_extraction.copy_file(mocked_source, mocked_output)
        assert os.path.exists(mocked_source + '_extracted.JSON')

class testReadFile(unittest.TestCase):
    def setup(self):
        pass

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isfile', return_value=False)
    def testReadFileDoesNotExist(self, mocked_os, mocked_file):
        cpap_extraction.read_file('Any file')
        self.assertRaises(FileNotFoundError)

if __name__ == '__main__':
    unittest.main()
