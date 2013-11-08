# -*- coding: utf-8 -*-
from gensim import corpora
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, PorterStemmer, SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, wordpunct_tokenize
from string import punctuation
from nltk import clean_html
import re

def remove_non_ascii(string):
  """
  Remove all non-ascii characters from input string
  """
  return ''.join(character for character in string if ord(character)<128)

def remove_URLs(string):
  """
  Remove all URLs from input string
  """
  pattern = r'((http|ftp|https):\/\/)?[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
  return re.sub(pattern, ' ', string)

def clean_text(
      text, 
      html=False, 
      digits=False, 
      urls=False, 
      ascii=False
  ):
  """
  Remove html, digits, weird white space, URLs, non-ascii chars from raw text
  """
  # text is none, return an empty string
  if text is None:
    return ''

  if html is False:
    # strip html markup
    text = clean_html(text)
  if digits is False:
    # remove digits
    text = re.sub(r'\d', ' ', text)
  if urls is False:
    # remove all urls
    text = remove_URLs(text)
  if ascii is False:
    # remove all non-ascii characters
    text = remove_non_ascii(text)

  # standardize white space
  text = re.sub(r'\s+', ' ', text) 

  # return 
  return text

def tokenize_and_normalize_text(
      text,
      wordpunct=True,
      filter_stopwords=True,
      normalizer='wordnet',
      lang='english'
  ):
  """
  Remove stopwords, bare punctuation, capitalization; lemmatize or stem words

  Parameters
  ----------
  text : string
    a single string of words and punctuation, a "text"
  filter_stopwords : boolean (default True)
    if True, filter out stopwords in nltk.corpus.stopwords
  normalizer : string or None (default 'wordnet')
    if 'wordnet', lemmatizes words
    if in ['porter', 'lancaster', 'snowball'], stems words
    if None, doesn't normalize words
  lang : string (default 'english')
    language to use for stopwords and snowball stemmer

  Returns
  -------
  norm_words : list of strings
    list of normalized words comprising text
  """

  # check input
  if not isinstance(text, basestring):
    print '**WARNING: text is not a string!'
    return None

  # check stopwords arg
  if lang not in stopwords.fileids():
    print '***ERROR: lang', lang, 'not in', stopwords.fileids(), '!'
    return None
  stops = set(stopwords.words(lang))

  # toxenize words
  if wordpunct is True:
    words = wordpunct_tokenize(text.lower())
  else:
    words = word_tokenize(text.lower())

  if filter_stopwords is True:
    good_words = (word for word in words
            #if word not in list(punctuation)
            if not all([char in punctuation for char in word])
            and len(word) > 0 and len(word) < 25
            and word not in stops)
  else:
    good_words = (word for word in words
            #if word not in list(punctuation)
            if not all([char in punctuation for char in word])
            and len(word) > 0 and len(word) < 25)

  normalizers = ['wordnet', 'porter', 'lancaster', 'snowball']
  if normalizer == 'wordnet':
    lemmatizer = WordNetLemmatizer()
    norm_words = [lemmatizer.lemmatize(word) for word in good_words]
  elif normalizer in ['porter', 'lancaster', 'snowball']:
    if normalizer == 'porter':
      stemmer = PorterStemmer()
    elif normalizer == 'lancaster':
      stemmer = LancasterStemmer()
    elif normalizer == 'snowball':
      if lang not in SnowballStemmer.languages:
        print '***ERROR: lang', lang, 'not in', SnowballStemmer.languages, '!'
        return None
      stemmer == SnowballStemmer(lang)
    norm_words = [stemmer.stem(word) for word in good_words]
  elif normalizer is None:
    norm_words = good_words
  else:
    print '***ERROR: normalizer', normalizer, 'not in', normalizers, '!'
    return None

  return norm_words

def make_gensim_corpus_from_texts(texts, **kwargs):
  """
  Given a list of texts, cleans and normalizes text then
  returns a dictionary of word<->ID mappings
  and a corpus of sparse vectors of bag-of-word-IDs
  """

  # parse args
  filter_stopwords = kwargs.get('filter_stopwords', True)
  normalizer = kwargs.get('normalizer', 'wordnet')
  lang = kwargs.get('lang', 'english')

  # clean texts
  cleaned_texts = [clean_text(t) for t in texts]

  # normalize texts
  normed_texts = [
    tokenize_and_normalize_text(
      text=t, 
      filter_stopwords=filter_stopwords,
      normalizer=normalizer,
      lang=lang
    )
    for t in cleaned_texts
  ]
  # convert to gensim corpus
  texts = [list(text) for text in normed_texts]
  return corpora.Dictionary(texts)
