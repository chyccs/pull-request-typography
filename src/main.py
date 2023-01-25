import keyword
import os
import re
from os import environ

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


def __can_process(title: str):
    return title.lower().find('bump') < 0


def __can_relocate_words(title: str):
    return title.find(':') < 0


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
    
    if not __can_process(pull_request.title):
        return

    stopwords = environ.get("stopwords", default=[])

    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=3,
        dedupLim=0.9,
        stopwords=stopwords,
    )

    keywords = []
    texts = {}
    for root, _, f_names in os.walk(src_path):
        for f in f_names:
            file_path = os.path.join(root, f)
            try:
                file = open(file_path, "r")
                strings = file.readlines()
                texts[file_path] = '\n'.join(strings)
                extracted = kw_extractor.extract_keywords('\n'.join(strings))
                extracted = sorted(extracted, key=lambda x: x[1], reverse=True)
                keywords.extend(extracted)
            except UnicodeDecodeError as decode_err:
                pass

    stopwords.extend(['cls.', 'self.'])
    stopwords.extend(keyword.kwlist)
    stopwords.extend(keyword.softkwlist)

    # for kw, v in keywords:
    #     print("extracted: ", kw, "/ score", v)

    th = TextHighlighter(
        max_ngram_size=3,
        highlight_pre="`",
        highlight_post="`",
    )

    if __can_relocate_words(pull_request.title):
        p = re.search('(.*)[(](.*)[)](.*)', pull_request.title)
        plain_title = th.highlight(f'{p.group(1)}{p.group(3)}', keywords)
        tag = p.group(2).lower().strip()
        decorated_title = f'{tag}: {plain_title.lower().strip()}'
    else:
        decorated_title = th.highlight(pull_request.title, keywords)

    decorated_body = th.highlight(pull_request.body, keywords)

    pull_request.edit(
        title=decorated_title,
        body=decorated_body,
    )


if __name__ == "__main__":
    main()
