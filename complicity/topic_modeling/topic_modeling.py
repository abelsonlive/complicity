# -*- coding: utf-8 -*-
import dataset
from text_processing import process_texts
from gensim.models.ldamodel import LdaModel
from gensim.models import TfidfModel
from complicity.common import db, articles
import pickle

def train_model(texts, **kwargs):

  # parse args
  filter_stopwords = kwargs.get('filter_stopwords', True)
  normalizer = kwargs.get('normalizer', 'porter')
  tfidf = kwargs.get('tfidf', True)
  num_topics = kwargs.get('num_topics', 20)
  min_freq = kwargs.get('min_freq', 2)
  use_pickle = kwargs.get('use_pickle', True)
  update_pickle = kwargs.get('update_pickle', True)
  report = kwargs.get('report', True)
  
  # build corpus or read it in from pickle
  if use_pickle:
    print "loading pickled corpus and word hash"
    corpus = pickle.load( open( "corpus.p", "rb" ) )
    id2word = corpora.Dictionary(pickle.load( open( "id2word.p", "rb" ) ))
            
  else:
    print "processing text and building corpus..."
    corpus, id2word = process_texts(
      texts = texts, 
      filter_stopwords = filter_stopwords,
      normalizer = normalizer,
      min_freq = min_freq
    )
    if update_pickle:
      # pickle files
      print "updating pickled coprus and word hash"
      pickle.dump(corpus, open( "pickles/corpus.p", "wb" ) )
      pickle.dump(corpus, open( "pickles/id2word.p", "wb" ) )

  # optional tfidf transformation
  if tfidf:
    print "applying tfidf transformation..."
    tfidf = TfidfModel(corpus)
    corpus = tfidf[corpus]

  # fit model
  print "fitting model..."
  lda = LdaModel(corpus = corpus, id2word = id2word, num_topics = num_topics)

  # report
  if report:
    print "\nperplexity: ", lda.bound(corpus)
    topics = lda.show_topics(num_topics)
    for i, t in enumerate(topics):
      print "topic %d:" % i
      print t

if __name__ == '__main__':
  
  # # nyt example
  # import json
  # nyt_articles = json.load(open('/Users/brian/Dropbox/code/measuring-the-news/data/articles-nyt/content.json'))
  # texts = [a['content'] for a in nyt_articles]

  # real data
  texts = [r['content'] for r in db.query('SELECT content FROM articles')][1:100]
    
  train_model(
    texts = texts, 
    num_topics = 10,
    min_freq = 2,
    use_pickle = False,
    update_pickle = False
  )