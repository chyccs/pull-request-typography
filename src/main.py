import glob
import keyword
import os
import re
from os import (
    environ,
    path,
    walk,
)

import yake
from yake.highlight import TextHighlighter

from services import fetch_pull_request

TAG = [
    'build',
    'chore',
    'ci',
    'docs',
    'feat',
    'fix',
    'perf',
    'refactor',
    'revert',
    'style',
    'test',
]


def main():
    owner = os.environ['owner']
    repo = os.environ['repository']
    pull_request_num = int(os.environ['pull_request_number'])
    token = os.environ['access_token']
    src_path = os.environ['src_path']

    pull_request = fetch_pull_request(
        access_token=token,
        owner=owner,
        repository=repo,
        number=pull_request_num,
    )

    stopwords = environ.get("stopwords", default=[])

    texts = {}
    for root, _, f_names in os.walk(src_path):
        for f in f_names:
            file_path = os.path.join(root, f)
            try:
                file = open(file_path, "r")
                strings = file.readlines()
                texts[file_path] = '\n'.join(strings)
            except UnicodeDecodeError as decode_err:
                pass
                
    # for x in walk(src_path):
    #     for y in glob.glob(path.join(x[0], '*.*')):
    #         if not y.startswith('./.venv'):
    #             file = open(y, "r")
    #             strings = file.readlines()
    #             texts[y] = '\n'.join(strings)

    text = '\n\n\n'.join(texts.values())
    stopwords.extend(['cls.', 'self.'])
    stopwords.extend(keyword.kwlist)
    stopwords.extend(keyword.softkwlist)

    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=3,
        top=300,
        dedupLim=0.9,
        stopwords=stopwords,
    )
    keywords = kw_extractor.extract_keywords(text)
    keywords = sorted(keywords, key=lambda x: x[1], reverse=True)

    # for kw, v in keywords:
    #     print("yake: ", kw, "/ score", v)

    th = TextHighlighter(
        max_ngram_size=3,
        highlight_pre="`",
        highlight_post="`",
    )

    if pull_request.title.find(':') < 0:
        p = re.search('(.*)[(](.*)[)](.*)', pull_request.title)
        decorated_title = th.highlight(f'{p.group(1)}{p.group(3)}', keywords)
        tag = p.group(2).strip()
        decorated_title = f'{tag}: {decorated_title.lower().strip()}'
    else:
        decorated_title = th.highlight(pull_request.title, keywords)

    decorated_body = th.highlight(pull_request.body, keywords)

    pull_request.edit(
        title=decorated_title,
        body=decorated_body,
    )


if __name__ == "__main__":
    main()
