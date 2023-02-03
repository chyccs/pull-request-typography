import keyword
import os
import re
from os import environ as env

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


def __decorate_number(title: str):
    return re.sub('(([`]*)([0-9]+[0-9\.\-%$,]*)([`]*))', '`\\3`', title)


def main():
    owner = env['owner']
    repo = env['repository']
    pull_request_num = int(env['pull_request_number'])
    token = env['access_token']
    src_path = env['src_path']

    pull_request = fetch_pull_request(
        access_token=token,
        owner=owner,
        repository=repo,
        number=pull_request_num,
    )

    if not __can_process(pull_request.title):
        return

    stopwords = env.get("stopwords", default=[])

    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=3,
        dedupLim=0.9,
        stopwords=stopwords,
    )

    keywords = []
    for root, _, f_names in os.walk(src_path):
        for f in f_names:
            file_path = os.path.join(root, f)
            if file_path.startswith('./.venv'):
                continue
            try:
                with open(file_path, "r") as file:
                    strings = file.readlines()
                extracted = kw_extractor.extract_keywords('\n'.join(strings))
                keywords.extend(extracted)
            except UnicodeDecodeError:
                pass

    stopwords.extend(['cls.', 'self.'])
    stopwords.extend(keyword.kwlist)
    stopwords.extend(keyword.softkwlist)

    if env.get("verbose"):
        extracted = sorted(extracted, key=lambda x: x[1], reverse=True)
        for kw, v in keywords:
            print("extracted: ", kw, "/ score", v)

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

    decorated_title = __decorate_number(decorated_title)
    decorated_body = th.highlight(pull_request.body, keywords)

    pull_request.edit(
        title=decorated_title,
        body=decorated_body,
    )


if __name__ == "__main__":
    main()
