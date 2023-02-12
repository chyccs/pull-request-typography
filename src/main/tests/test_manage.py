import unittest

from manage import (
    _decorate_bump,
    _highlight,
    _parse_title,
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

    def test_tokenize(self):
        self.assertEqual(_tokenize('return title'), 'title')
        self.assertEqual(_tokenize('TITLE'), 'title')
        self.assertEqual(_tokenize('make_canvas'), 'make canvas')
        self.assertEqual(_tokenize('makeCanvas'), 'make canvas')

    def test_decorate_bump(self):
        self.assertEqual(_decorate_bump(
            title='build(deps-dev): bump mypy from 0.991 to 1.0.0',
            ref_name='dependabot/pip/mypy-1.0.0',
        ), 'build(deps-dev): bump `mypy` from `0.991` to `1.0.0`')

    def test_highlight(self):
        keywords = [
            'update pull requests',
            'update_pull_requests',
            'update pull request',
            'update_pull_request',
            'fetch_pull_requests',
            'fetch pull requests',
            'fetch github repos',
            'fetch_github_repos',
            'fetch pull request',
            'fetch_pull_request',
            'fetch_github_repo',
            'fetch github repo',
            'stopwords',
            'stopword',
        ]
        self.assertEqual(_highlight(
            text='feat: add testcases named test manage',
            keywords=keywords,
        ), 'feat: add testcases named test manage')

    def test_parse_title(self):
        self.assertEqual(_parse_title(title='feat: add testcases named test manage'),
                         ('feat', 'add testcases named test manage'))
        self.assertEqual(_parse_title(title='(feat)add testcases named test manage'),
                         ('feat', 'add testcases named test manage'))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
