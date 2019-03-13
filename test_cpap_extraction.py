import unittest
import mock
from mock import patch
import cpap_extraction

class TestHelloWorld(unittest.TestCase):
    def setup(self):
        pass

    def test_return(self):
        self.assertEqual(cpap_extraction.hello_world(), 0)


class TestCopy(unittest.TestCase):
    def setup(self):
        mock_source = patch('cpap_extraction.source').start()
        mock_destination = patch('cpap_extraction.destination').start()
        self.addCleanup(patch.stopall)

    @patch('os.path.isfile')
    def test_copy_file_no_source(self):
        pass
    '''
    def test_copy_file(self, mocked_os, mocked_file):
        mocked_file.return_value = True
        #cpap_extraction.copy_file(mocked_file, '.')
        self.assertTrue(mocked_os.path.isfile('mocked_file_extracted'))
    '''



if __name__ == '__main__':
    unittest.main()
