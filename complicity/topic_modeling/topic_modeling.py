# -*- coding: utf-8 -*-
import dataset
from text_processing import make_gensim_corpus_and_dicionary_from_texts
from gensim.models.ldamodel import LdaModel
from gensim.models import TfidfModel
from complicity.common import db, articles

# example
# import json
# nyt_articles = json.load(open('/Users/brian/Dropbox/code/measuring-the-news/data/articles-nyt/content.json'))
# texts = [a['content'] for a in nyt_articles]

# real data
texts = [r['content'] for r in db.query('SELECT content FROM articles')]

print "building gensim corpus"
corpus, id2word = make_gensim_corpus_and_dicionary_from_texts(texts)

print "tf-idf transformation"
tfidf = TfidfModel(corpus)
tfidf_corpus = tfidf[corpus]

print "fitting model"
num_topics = 30
lda = LdaModel(corpus = tfidf_corpus, id2word = id2word, num_topics = num_topics)
topics = lda.show_topics(num_topics)
for i, t in enumerate(topics):
  print "topic %d:" % i
  print t + "\n\n"