import keyword
import os
import re
from os import environ as env
from typing import List

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
    return re.sub(r'(([`]*)([0-9]+[0-9\.\-%$,]*)([`]*))', r'`\3`', title)


def __decorate_filename(title: str, files: List[str]):
    files_available = '|'.join(files)
    return re.sub(rf'([`]*)({files_available})([`]*)', r'`\2`', title)


def __parse_title(title: str):
    if __can_relocate_words(title):
        p = re.search(r'(.*)[(\[](.*)[)\]](.*)', title)
        plain_title = f'{p.group(1)}{p.group(3)}'
        tag = p.group(2).lower().strip()
        return tag, plain_title

    p = re.search(r'(.*)[\:][ ]*(.*)', title)
    return p.group(1).lower().strip(), p.group(2).lower().strip()


def __highlight(text: str, keywords: List[str]):
    rep = dict((re.escape(k), f'`{k}`') for k in keywords) 
    patt = "|".join([re.escape(k) for k in sorted(rep, key=len, reverse=True)])
    print(patt)
    pattern = re.compile("|".join([re.escape(k) for k in sorted(rep, key=len, reverse=True)]), flags=re.DOTALL)
    return pattern.sub(lambda x: rep[x.group(0)], text)


def main():
    owner = env['owner']
    repo = env['repository']
    pull_request_num = int(env['pull_request_number'])
    token = env['access_token']
    src_path = env['src_path']
    symbols = env["symbols"]
    keywords = symbols.split('\n')
    
    pull_request = fetch_pull_request(
        access_token=token,
        owner=owner,
        repository=repo,
        number=pull_request_num,
    )

    if not __can_process(pull_request.title):
        return

    stopwords = env.get("stopwords", default=[])
    stopwords.extend(['cls.', 'self.'])
    stopwords.extend(keyword.kwlist)
    stopwords.extend(keyword.softkwlist)
    
    keywords = []
    files = []
    for root, _, f_names in os.walk(src_path):
        for f in f_names:
            file_path = os.path.join(root, f)
            if file_path.startswith('./.venv'):
                continue
            files.append(f)

    tag, plain_title = __parse_title(pull_request.title)

    plain_title = __decorate_number(plain_title)
    plain_title = __decorate_filename(plain_title, files)

    decorated_title = f'{tag}: {__highlight(plain_title, keywords)}'
    decorated_body = __highlight(pull_request.body, keywords)
    
    print(decorated_title)
    print(decorated_body)
    
    pull_request.edit(
        title=decorated_title,
        body=decorated_body,
    )


if __name__ == "__main__":
    main()
