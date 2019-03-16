import unittest         # For testing
from mock import Mock   # For mocking input and output files
from mock import patch  # For patching out file I/O
import os               # For file I/O
import cpap_extraction  # The module to be tested
'''
This module contains unittests for the cpap_extraction module
'''

class TestHelloWorld(unittest.TestCase):
    '''
    Tests the hello_world method, that method, as well as this test, should
    eventually be deleted.

    Methods
    -------
    test_return
        Tests that the return value of hello_world is 0, as it should be
    '''
    def test_return(self):
        self.assertEqual(cpap_extraction.hello_world(), 0)

class TestCopyFile(unittest.TestCase):
    '''
    Tests the copy_file method, which coverts a file written in binary to 
    plain-text, to a file called orig_file_extracted.JSON. The second
    argument of copy_file is the directory to write the plain-text file to.
    The copy_file method, as well as this test, should eventually be deleted.

    Methods
    -------
        testCopy
            Tests whether a file is correctly read in, and whether a file
            called orig_file_extracted.JSON is created in the correct
            directory
    '''
    @patch('cpap_extraction.write_file')
    @patch('cpap_extraction.read_file', return_value='xx')
    def testCopy(self, mocked_source, mocked_output):
        # TODO: This doesn't seem to actually work, I'll try and get some help
        cpap_extraction.copy_file(mocked_source, mocked_output)
        assert os.path.exists(mocked_source + '_extracted.JSON')

class testReadFile(unittest.TestCase):
    '''
    Tests the read_file method, which reads in a binary file, and returns it
    as a file object.

    Methods
    -------
        testReadFileExists
            Tests whether read_file correctly opens a file that exists
        testReadFileDoesNotExist
            Tests whether read_file correctly raises the FileNotFoundError
            exception if the specified file does not exist
    '''

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isfile', return_value=True)
    def testReadFileExists(self, mocked_os, mocked_file):
        cpap_extraction.read_file('Any file')
        mocked_file.assert_called_once_with('Any file', 'rb')

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isfile', return_value=False)
    def testReadFileDoesNotExist(self, mocked_os, mocked_file):
        # Use a context manager to test raising exceptions:
        # https://docs.python.org/3.6/library/unittest.html
        with self.assertRaises(FileNotFoundError): 
            cpap_extraction.read_file('Any file')

class testWriteFile(unittest.TestCase):
    '''
    Tests the write_file method, which takes a file object created by the
    read_file method, and writes it out to a file called 
    orig_file_extracted.JSON, in the specified directory on the users' drive.

    Methods
    -------
        testWriteFileDirExists
            Tests whether write_file correctly creates a file called
            orig_file_extracted.JSON in the specified directory
        testWriteFileDirDoesNotExist
            Test whether write_file correctly raises the FileNotFoundError
            exception if the specified directory to write the file into does
            not exist
    '''

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isdir', return_value=True)
    def testWriteFileDirExists(self, mocked_os, mocked_file):
        cpap_extraction.write_file('Any file', 'Any directory')
        mocked_file.assert_called_once_with('Any directory/_extracted.JSON', 'w')

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isdir', return_value=False)
    def testWriteFileDirDoesNotExist(self, mocked_os, mocked_file):
        with self.assertRaises(FileNotFoundError):
            cpap_extraction.write_file('Any file', 'Any directory')

if __name__ == '__main__':
    unittest.main()
