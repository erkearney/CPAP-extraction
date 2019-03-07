import unittest
import mock
import cpap_extraction

class TestHelloWorld(unittest.TestCase):
    def setup(self):
        pass

    def test_return(self):
        self.assertEqual(cpap_extraction.hello_world(), 0)


class TestCopy(unittest.TestCase):
    @mock.patch('cpap_extraction.os.path.isfile')
    @mock.patch('cpap_extraction.os.path.isdir')
    def test_copy_file(self, mocked_os, mocked_file):
        mocked_file.return_value = True
        cpap_extraction.copy_file(mocked_file, '.')
        self.assertTrue(mocked_os.path.isfile('mocked_file_extracted'))



if __name__ == '__main__':
    unittest.main()
