import keyword
import os
import re
from os import environ as env
from typing import List, Set

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


def __multireplace(string, replacements, ignore_case=False):
    """
    Given a string and a replacement map, it returns the replaced string.
    :param str string: string to execute replacements on
    :param dict replacements: replacement dictionary {value to find: value to replace}
    :param bool ignore_case: whether the match should be case insensitive
    :rtype: str
    """
    if not replacements:
        # Edge case that'd produce a funny regex and cause a KeyError
        return string
    
    # If case insensitive, we need to normalize the old string so that later a replacement
    # can be found. For instance with {"HEY": "lol"} we should match and find a replacement for "hey",
    # "HEY", "hEy", etc.
    if ignore_case:
        def normalize_old(s):
            return s.lower()

        re_mode = re.IGNORECASE

    else:
        def normalize_old(s):
            return s

        re_mode = 0

    replacements = {normalize_old(key): val for key, val in replacements.items()}
    
    # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    rep_sorted = sorted(replacements, key=len, reverse=True)
    rep_escaped = map(re.escape, rep_sorted)
    
    # Create a big OR regex that matches any of the substrings to replace
    pattern = re.compile("|".join(rep_escaped), re_mode)
    
    # For each match, look up the new string in the replacements, being the key the normalized old string
    return pattern.sub(lambda match: replacements[normalize_old(match.group(0))], string)


def __highlight(text: str, keywords: Set[str]):
    rep = dict((re.escape(k), f'`{k}`') for k in keywords)
    return __multireplace(text, rep)
    # print(rep)
    # pattern = re.compile("|".join(rep.keys()))
    # return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)


def main():
    owner = env['owner']
    repo = env['repository']
    pull_request_num = int(env['pull_request_number'])
    token = env['access_token']
    src_path = env['src_path']
    symbols = env["symbols"]
    keywords = set(symbols.split('\n'))

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
