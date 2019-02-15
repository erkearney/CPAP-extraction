import unittest
from CPAP_extraction import hello_world

class TestHelloWorld(unittest.TestCase):
    def setUp(self):
        pass

    def test_return(self):
        self.assertEqual(hello_world(), 0)


if __name__ == '__main__':
    unittest.main()
