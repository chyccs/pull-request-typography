import unittest

from src.main import can_process


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        print('setUp')

    def tearDown(self):
        print('tearDown\n')

    def test_can_process(self):
        self.assertTrue(can_process('bump title'))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()