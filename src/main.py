import glob
from os import environ, walk, path
import os
import yake
from yake.highlight import TextHighlighter
import keyword

from services import get_github_repo, get_pull_request, update_pull_request


def main():
    repository_name = os.environ['repository_name']
    pull_request_number = os.environ['pull_request_number']
    access_token = os.environ['access_token']
    pull_request = get_pull_request(
        repo=get_github_repo(access_token=access_token, repository_name=repository_name), 
        number=pull_request_number,
    )
    
    src_path = environ.get("src_path", default='sample/')
    stopwords = environ.get("stopwords", default=[])
    
    texts = {}
    
    for x in walk(src_path):
        for y in glob.glob(path.join(x[0], '*.py')):
            if not y.startswith('./.venv'):
                file = open(y, "r")
                strings = file.readlines()
                texts[y] = '\n'.join(strings)

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
    
    for kw, v in keywords:
        print("yake: ",kw, "/ score", v)
        
    th = TextHighlighter(
        max_ngram_size = 3, 
        highlight_pre = "`", 
        highlight_post= "`",
    )

    decorated_title = th.highlight(pull_request.title, keywords)
    decorated_body = th.highlight(pull_request.body, keywords)

    update_pull_request(pull_request=pull_request, title=decorated_title, body=decorated_body)


if __name__ == "__main__":
	main()
