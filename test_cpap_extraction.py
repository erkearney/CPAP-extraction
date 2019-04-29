import unittest         # For testing
from mock import Mock   # For mocking input and output files
from mock import patch  # For patching out file I/O
import os               # For file I/O
import cpap_extraction  # The module to be tested
import io               # For reading strings as files
'''
This module contains unittests for the cpap_extraction module
'''


class testOpenFile(unittest.TestCase):
    '''
    Tests the open_file method, which reads in a binary file, and returns it
    as a file object.

    Methods
    -------
        testReadFileExists
            Tests whether open_file correctly opens a file that exists
        testReadFileDoesNotExist
            Tests whether open_file correctly raises the FileNotFoundError
            exception if the specified file does not exist
    '''

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isfile', return_value=True)
    def testOpenFileExists(self, mocked_os, mocked_file):
        cpap_extraction.open_file('Any file')
        mocked_file.assert_called_once_with('Any file', 'rb')

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isfile', return_value=False)
    def testOpenFileDoesNotExist(self, mocked_os, mocked_file):
        # Use a context manager to test raising exceptions:
        # https://docs.python.org/3.6/library/unittest.html
        with self.assertRaises(FileNotFoundError):
            cpap_extraction.open_file('Any file')


class testReadPacket(unittest.TestCase):
    '''
    Tests the read_packet method, which takes two arguments, data_file and
    delimeter. data_file is a file, created by the read_file method, that
    contains multiple packets, each separated by delimeter. This method
    returns the first complete packet it finds within data file, or it returns
    nothing if no packet is found. read_packet leaves the seak point of
    data_file at the beginning of the next packet.

    These tests use Python's io class:
    https://docs.python.org/3/library/io.html

    Methods
    -------
        testNormal
            Tests whether read_file performs as expected in a base case
        testEmpty
            Tests that read_file properly returns an empty BytesArray if
            data_file is empty
        testDataFileEndsNoDelimeter
            Tests whether read_file properly returns a packet that did not end
            with a delimeter. In this scenario, a warning should be raised
        testEmptyDelimeter
            Tests whether read_file properly returns the entire packet,
            unmodified if delimeter = b''
        testInvalidDelimeter
            Tests whether read_file properly raises a ValueError if delimeter
            is not of type bytes
    '''

    def testNormal(self):
        data_file = io.BytesIO(b'\x34\x32\xff\xff\xff\xff\x42')
        delimeter = b'\xff\xff\xff\xff'
        packet = cpap_extraction.read_packet(data_file, delimeter)

        self.assertEqual(packet, b'\x34\x32')

    def testEmpty(self):
        data_file = io.BytesIO(b'')
        delimeter = b'\xff\xff\xff\xff'
        packet = cpap_extraction.read_packet(data_file, delimeter)

        self.assertEqual(packet, b'')

    def testDataFileEndsNoDelimeter(self):
        data_file = io.BytesIO(b'\x34\x32')
        delimeter = b'\xff\xff\xff\xff'
        packet = cpap_extraction.read_packet(data_file, delimeter)

        self.assertEqual(packet, b'\x34\x32')

    def testEmptyDelimeter(self):
        data_file = io.BytesIO(b'\x34\x32\xff\xff\xff\xff\x42')
        delimeter = b''

        with self.assertWarns(Warning):
            packet = cpap_extraction.read_packet(data_file, delimeter)
            self.assertEqual(packet, b'\x34\x32\xff\xff\xff\xff\x42')

    def testInvalidDelimeter(self):
        data_file = io.BytesIO(b'\x34\x32\xff\xff\xff\xff\x42')
        delimeter = 'test'

        with self.assertRaises(TypeError):
            packet = cpap_extraction.read_packet(data_file, delimeter)


class testConvertUnixTime(unittest.TestCase):
    '''
    Tests the convert_unix_time method, which takes an int, unixtime, as an
    argument, and returns the unix time converted into year-month-day,
    hour:minute:second format. This converted format is returned as a string.

    Methods
    -------
        testNormal
            Tests a base case, 842323380000, which should evaluate to
            1996-09-10 02:43:00
        testZero
            Tests that if unixtime = 0, a warning is raised, and the returned
            string is 1970-01-01 00:00:00
        testNegative
            Tests that if unixtime < 0, a warning is raised, and the returned
            string is 1970-01-01 00:00:00
        testLargeValue
            Tests that is unixtime > 2147483647000, a warning is raised
        testNonInteger
            The CPAP machines store time in UNIX time, but in milliseconds.
            Therefore, convert_unix_time divides the passed in unixtime
            argument by 1000. Therefore, we'll want to make sure
            convert_unix_time correctly handles non-integer values, it should
            simply discard any decimal values.
        testBadArgument
            Tests that convert_unix_time correctly catches a TypeError, and
            returns 'ERROR: {unixtime} is invalid' instead.
    '''

    def testNormal(self):
        unixtime = 842323380000
        converted_time = cpap_extraction.convert_unix_time(unixtime)
        self.assertEqual(converted_time, '1996-09-10 02:43:00')

    def testZero(self):
        unixtime = 0
        with self.assertWarns(Warning):
            converted_time = cpap_extraction.convert_unix_time(unixtime)
            self.assertEqual(converted_time, '1970-01-01 00:00:00')

    def testNegative(self):
        unixtime = -1
        with self.assertWarns(Warning):
            converted_time = cpap_extraction.convert_unix_time(unixtime)
            self.assertEqual(converted_time, '1970-01-01 00:00:00')

    def testLargeValue(self):
        unixtime = 2147483647000
        with self.assertWarns(Warning):
            converted_time = cpap_extraction.convert_unix_time(unixtime)
            self.assertEqual(converted_time, '2038-01-19 03:14:07')

    def testNonInteger(self):
        # convert_unix_time should just drop extra milliseconds
        unixtime = 842323380451
        converted_time = cpap_extraction.convert_unix_time(unixtime)
        self.assertEqual(converted_time, '1996-09-10 02:43:00')

    def testBadArgument(self):
        # convert_unix_time should catch the TypeError, when it does, it's
        # supposed to return whathever the original unixtime was
        unixtime = 'test'
        converted_time = cpap_extraction.convert_unix_time(unixtime)
        self.assertEqual(converted_time, 'ERROR: test is invalid')


class testWriteFile(unittest.TestCase):
    '''
    Tests the write_file method, which takes a file object created by the
    open_file method, and writes it out to a file called
    orig_file_extracted.JSON, in the specified directory on the users' drive.

    Methods
    -------
        testWriteFileDirExists
            Tests whether write_file correctly creates a file called
            orig_file_extracted.JSON in the specified directory
        testWriteFileDirDoesNotExist
            Tests whether write_file correctly raises the FileNotFoundError
            exception if the specified directory to write the file into does
            not exist
        testWriteEmptyFile
            Tests whether write_file correctly raises a warning if the input
            File is empty
    '''

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isdir', return_value=True)
    def testWriteFileDirExists(self, mocked_os, mocked_file):
        cpap_extraction.write_file('Any file', 'Any directory')
        mocked_file.assert_called_once_with('Any directory/_extracted.JSON',
                                            'a')

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isdir', return_value=False)
    def testWriteFileDirDoesNotExist(self, mocked_os, mocked_file):
        with self.assertRaises(FileNotFoundError):
            cpap_extraction.write_file('Any file', 'Any directory')

    @patch('cpap_extraction.open')
    @patch('cpap_extraction.os.path.isdir', return_value=True)
    def testWriteEmptyFile(self, mocked_os, mocked_file):
        with self.assertWarns(Warning):
            cpap_extraction.write_file('', 'Any directory')


if __name__ == '__main__':
    unittest.main()
