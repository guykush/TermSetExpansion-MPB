import sys
from gensim.corpora.wikicorpus import *
import os
import six



def tokenize(content):     # override original method in wikicorpus.py in order to preserve punctuation
    return [token.encode('utf8') for token in content.split()
            if len(token) <= 15 and not token.startswith('_')]


def process_article(args):    # override original method in wikicorpus.py
    text, lemmatize, title, pageid = args
    text = filter_wiki(text)
    if lemmatize:
        result = utils.lemmatize(text)
    else:
        result = tokenize(text)
    return result, title, pageid


class MyWikiCorpus(WikiCorpus):
    def __init__(self, fname, processes=None, lemmatize=utils.has_pattern(), dictionary=None, filter_namespaces=('0',)):
        WikiCorpus.__init__(self, fname, processes, lemmatize, dictionary, filter_namespaces)

    def get_texts(self):
        articles, articles_all = 0, 0
        positions, positions_all = 0, 0
        texts = ((text, self.lemmatize, title, pageid) for title, text, pageid in
                 extract_pages(bz2.BZ2File(self.fname), self.filter_namespaces))
        pool = multiprocessing.Pool(self.processes)
        for group in utils.chunkize(texts, chunksize=10 * self.processes, maxsize=1):
            for tokens, title, pageid in pool.imap(process_article, group):
                articles_all += 1
                positions_all += len(tokens)
                if len(tokens) < ARTICLE_MIN_WORDS or any(title.startswith(ignore + ':') for
                                                          ignore in IGNORED_NAMESPACES):
                    continue
                articles += 1
                positions += len(tokens)
                if self.metadata:
                    yield (tokens, (pageid, title))
                else:
                    yield tokens
        pool.terminate()
        self.length = articles  # cache corpus length


def make_corpus(corpus, text_file_dir):
    wiki = MyWikiCorpus(corpus)
    print("finished initializing")
    i = 0
    texts = wiki.get_texts()
    for text in texts:
        file_add = text_file_dir + str(i).zfill(7)
        file = open(file_add, 'w')
        if six.PY3:
            file.write(b' '.join(text).decode('utf-8') + '\n')
        else:
            file.write(space.join(text) + "\n")
        file.close()
        i = i + 1
        if i % 10000 == 0:
            print('Processed ' + str(i) + ' articles')
    print('Processing complete!')


if __name__ == '__main__':
    input_file = "enwiki-latest-pages-articles.xml.bz2"
    output_dir = "textFiles/"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    make_corpus(input_file, output_dir)

