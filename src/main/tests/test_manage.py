import unittest

from manage import (
    _can_process,
    _tokenize,
)


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
        self.assertTrue(_can_process(' title'))

    def test_tokenize(self):
        self.assertEqual(_tokenize('return title'), 'title')
        self.assertEqual(_tokenize('TITLE'), 'title')
        self.assertEqual(_tokenize('make_canvas'), 'make canvas')
        self.assertEqual(_tokenize('makeCanvas'), 'make canvas')

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
