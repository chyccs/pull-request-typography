import unittest

from manage import __can_process


class TestManage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        print('setUp')

    def tearDown(self):
        print('tearDown')

    def test_can_process(self):
        self.assertTrue(__can_process(' title'))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
