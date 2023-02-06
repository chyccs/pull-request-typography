import inspect
import keyword
import os
import re
from os import environ as env
from typing import (
    List,
    Set,
)

from inflection import (
    humanize,
    pluralize,
    singularize,
    underscore,
)

from main import fetch_pull_request
from main.constants import STOPWORDS

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


def _logging(level: str, title: str, message: str):
    frame: inspect.FrameInfo = inspect.stack()[2]
    print(f'::{level} file={frame.filename}, line={frame.lineno}, title={title}::{message}')


def _can_process(title: str):
    return title.lower().find('bump') < 0


def __can_relocate_words(title: str):
    return title.find(':') < 0


def _decorate_number(title: str):
    return re.sub(r'(([`]*)([0-9]+[0-9\.\-%$,]*)([`]*))', r'`\3`', title)


def _decorate_filename(title: str, files: List[str]):
    files_available = '|'.join(files)
    return re.sub(rf'([`]*)({files_available})([`]*)', r'`\2`', title)


def _parse_title(title: str):
    if __can_relocate_words(title):
        p = re.search(r'(.*)[(\[](.*)[)\]](.*)', title)
        plain_title = f'{p.group(1)}{p.group(3)}'
        tag = p.group(2).lower().strip()
        return tag, plain_title

    p = re.search(r'(.*)[\:][ ]*(.*)', title)
    return p.group(1).lower().strip(), p.group(2).lower().strip()


def _highlight(text: str, keywords: Set[str]):
    highlighted = text
    for k in keywords:
        try:
            highlighted = re.sub(rf'(?<!`)({re.escape(k)})(?!`)', r'`\1`', highlighted)
        except re.error as ex:
            _logging('error', f'regex error during highlighting keyword {k}', str(ex))
            continue
        except Exception as ex:
            _logging('error', f'misc error during highlighting keyword {k}', str(ex))
            continue
    return highlighted


def _extend_singularize(symbols: List[str]):
    symbols.extend([singularize(symbol) for symbol in symbols])


def _extend_pluralize(symbols: List[str]):
    symbols.extend([pluralize(symbol) for symbol in symbols])


def _tokenize(symbol: str):
    stopwords = list(keyword.kwlist)
    stopwords.extend(STOPWORDS)
    return (re
            .sub(rf'\b({"|".join(stopwords)})\b', r'', humanize(underscore(symbol)).lower().strip())
            .lower().strip())


def _symbolize(raw_symbols: str):
    symbols = [_tokenize(symbol)for symbol in raw_symbols.split('\n') if len(_tokenize(symbol)) > 3]
    symbols.extend([symbol.replace(' ', '_') for symbol in symbols])
    return symbols


def main():
    symbols = _symbolize(env["symbols"])
    _extend_singularize(symbols)
    _extend_pluralize(symbols)

    keywords = sorted(set(symbols), key=len, reverse=True)

    _logging('info', 'keywords', str(keywords))

    pull_request = fetch_pull_request(
        access_token=env['access_token'],
        owner=env['owner'],
        repository=env['repository'],
        number=int(env['pull_request_number']),
    )

    if not _can_process(pull_request.title):
        return

    files = []
    for root, _, f_names in os.walk(env['src_path']):
        for f in f_names:
            file_path = os.path.join(root, f)
            if file_path.startswith('./.'):
                continue
            files.append(f)

    tag, plain_title = _parse_title(pull_request.title)
    plain_title = _decorate_number(plain_title)
    plain_title = _decorate_filename(plain_title, files)

    decorated_title = f'{tag}: {_highlight(plain_title, keywords)}'
    decorated_body = _highlight(pull_request.body, keywords)

    pull_request.edit(
        title=decorated_title or pull_request.title,
        body=decorated_body or pull_request.body,
    )


if __name__ == "__main__":
    main()
