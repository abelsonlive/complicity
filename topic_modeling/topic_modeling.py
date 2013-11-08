# -*- coding: utf-8 -*-
import dataset
from text_processing import make_gensim_corpus_and_dicionary_from_texts

db = dataset.connect('postgresql://brian:mc@localhost:5432/news')

texts = [r['content'] for r in db.query('SELECT content FROM articles')]

corpus, dictionary = make_gensim_corpus_and_dicionary_from_texts(texts)
print corpus, dictionary