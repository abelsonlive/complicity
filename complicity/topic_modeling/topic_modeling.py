# -*- coding: utf-8 -*-
import dataset
from text_processing import make_gensim_corpus_and_dicionary_from_texts
from gensim.models.ldamodel import LdaModel
from gensim.models import TfidfModel

# db = dataset.connect('postgresql://brian:mc@localhost:5432/news')

# # query for removing duplicates
# rm_query = """
#   WITH pick AS (
#     SELECT url, min(id) as id FROM articles
#     GROUP BY url

#   )
#   DELETE FROM articles WHERE id NOT IN (SELECT id FROM pick)
# """
# print "old length: %s" % len([r for r in db['articles'].all()])
# # remove duplicates
# db.query(rm_query)
# print "new length: %s" % len([r for r in db['articles'].all()])

# texts = [r['content'] for r in db.query('SELECT content FROM articles')]

# corpus, id2word = make_gensim_corpus_and_dicionary_from_texts(texts)

# example
import json

num_topics = 10
articles = json.load(open('/Users/brian/Dropbox/code/measuring-the-news/data/articles-nyt/content.json'))
texts = [a['content'] for a in articles]

print "building gensim corpus"
corpus, id2word = make_gensim_corpus_and_dicionary_from_texts(texts)

print "tf-idf transformation"
tfidf = TfidfModel(corpus)
tfidf_corpus = tfidf[corpus]

print "fitting model"
lda = LdaModel(corpus = tfidf_corpus, id2word = id2word, num_topics = num_topics)
topics = lda.show_topics(num_topics)
for i, t in enumerate(topics):
  print "topic %d:" % i
  print t + "\n\n\n"