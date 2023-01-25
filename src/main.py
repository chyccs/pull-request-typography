import glob
from os import environ, walk, path
import yake
from yake.highlight import TextHighlighter
import keyword


def main():
    pull_request = environ.get("pull_request", default={})
    title = pull_request.get('title')
    body = pull_request.get('body')
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
    decorated_title = th.highlight(title, keywords)
    decorated_body = th.highlight(body, keywords)
    print(f"::set-output name=title::{decorated_title}")
    print(f"::set-output name=body::{decorated_body}")

if __name__ == "__main__":
	main()
