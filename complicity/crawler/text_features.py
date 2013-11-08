#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re, string
import pprint
import math

# tagger
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import brown
from nltk.corpus import treebank
from nltk import tag
from nltk.tag import brill
import random
from nltk import pos_tag,FreqDist,ConditionalFreqDist

#tokenize
from nltk.tokenize import word_tokenize, sent_tokenize, regexp_tokenize
import nltk_contrib
from nltk_contrib.readability.readabilitytests import ReadabilityTool
import json

# parse
from HTMLParser import HTMLParser
from functools import wraps
import unicodedata

# LEXICONS
bias_words = [line for line in open('lexicons/bias-lexicon.txt').read().split("\n") if line !='']
neg_words = [line for line in open("lexicons/positive-lexicon.txt").read().split("\n") if line !='']
pos_words = [line for line in open("lexicons/negative-lexicon.txt").read().split("\n") if line !='']
liwc = json.load(open("lexicons/liwc-lexicon.json"))

# html stripping
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def nohtml(fn):
    @wraps(fn)
    def wrapper(text,*args,**kwargs):
        text = strip_tags(text)
        return fn(text,*args,**kwargs)
    return wrapper

# tagging
patterns = [
            (r'(.*ing$|.*ed$|.*es$)', 'V'),
            (r'(.*\'s$|.*s$)','NN'),
            (r'(.*tive$|.*ly$)','JJ'),
            (r'(.*est$)','JJS'),
            (r'(.*er$)','JJR')
        ]


brown_tagged_sents = brown.tagged_sents(categories='news')

def get_tagger():
    d_tagger = nltk.DefaultTagger('NN')
    re_tagger = nltk.RegexpTagger(patterns,backoff=d_tagger)
    # train is the proportion of data used in training; the rest is reserved
    # for testing.
    print("Loading tagged data... ")
    tagged_data =  brown_tagged_sents
    cutoff = int(1000*.8)
    training_data = tagged_data[:cutoff]
    gold_data = tagged_data[cutoff:1000]
    testing_data = [[t[0] for t in sent] for sent in gold_data]
    print("Done loading.")

    bigram_tagger = tag.BigramTagger(training_data,backoff=re_tagger)
    
    templates = [
      brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,1)),
      brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (2,2)),
      brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,2)),
      brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,3)),
      brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,1)),
      brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (2,2)),
      brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,2)),
      brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,3)),
      brill.ProximateTokensTemplate(brill.ProximateTagsRule, (-1, -1), (1,1)),
      brill.ProximateTokensTemplate(brill.ProximateWordsRule, (-1, -1), (1,1)),
      ]
    trainer = brill.FastBrillTaggerTrainer(bigram_tagger, templates, 0)
    brill_tagger = trainer.train(training_data, max_rules=100, min_score=3)

    return brill_tagger

tagger = get_tagger()

# syllable counting
def count_syllables(word, isName=True):
    vowels = "aeiouy"
    #single syllables in words like bread and lead, but split in names like Breanne and Adreann
    specials = ["ia","ea"] if isName else ["ia"]
    specials_except_end = ["ie","ya","es","ed"]  #seperate syllables unless ending the word
    currentWord = word.lower()
    numVowels = 0
    lastWasVowel = False
    last_letter = ""

    for letter in currentWord:
        if letter in vowels:
            #don't count diphthongs unless special cases
            combo = last_letter+letter
            if lastWasVowel and combo not in specials and combo not in specials_except_end:
                lastWasVowel = True
            else:
                numVowels += 1
                lastWasVowel = True
        else:
            lastWasVowel = False

        last_letter = letter

    #remove es & ed which are usually silent
    if len(currentWord) > 2 and currentWord[-2:] in specials_except_end:
        numVowels -= 1

    #remove silent single e, but not ee since it counted it before and we should be correct
    elif len(currentWord) > 2 and currentWord[-1:] == "e" and currentWord[-2:] != "ee":
        numVowels -= 1

    return numVowels


# tokenizers
punct = re.compile('[%s]+' % re.escape(string.punctuation))

@nohtml
def tokenize_words(text, lower=False):
    if lower:
        return [w.lower().strip() for w in word_tokenize(text) if w is not punct.search(w)]
    else:
        return [w for w in word_tokenize(text) if w is not punct.search(w)]

@nohtml
def tokenize_sents(text):
    return [s for s in sent_tokenize(text)]

def tokenize_grafs(text):
    return regexp_tokenize(text, r'\<\/p\>', gaps=True)

# count things
def word_count(words):
    return len(words)

def punct_count(text, punct="?"):
    return len(re.findall("\\"+ punct, text))

def avg_word_length(words):
    words = [len(w) for w in words]
    return reduce(lambda x, y: x + y, words) / float(len(words))

def avg_word_syllables(words):
    words = [float(count_syllables(w)) for w in words]
    return reduce(lambda x, y: x + y, words) / float(len(words))

def pos_count(words, tag='NN'):
    cfd = ConditionalFreqDist((tag,1) for word,tag in  tagger.tag(words))
    return cfd[tag].N()

def pos_percentages(words, tag='NN'):
    cfd = ConditionalFreqDist((tag,1) for word,tag in  tagger.tag(words))
    relevant_tags = filter(lambda c: re.match(tag,c), cfd.conditions())
    sum_tags = sum([ cfd[c].N() for c in  relevant_tags ])
    return float(sum_tags)/float(len(words))

def liwc_count(words, word_type="ppron"):    
    liwc_type_list = liwc[word_type]
    matched_words = []
    for w in words:
        for t in liwc_type_list:
            if t['is_globbed']==1:
                if re.search("%s.*" % t['word'], w):
                    matched_words.append(w)
            else:
                if t['word'] == w:
                    matched_words.append(w)

    return len(matched_words)

def bias_word_count(words):
    return len([w for w in words if w in frozenset(bias_words)])

def pos_word_count(words):
    return len([w for w in words if w in frozenset(pos_words)])

def neg_word_count(words):
    return len([w for w in words if w in frozenset(neg_words)])

def sentence_count(sents):
    return len(sents)

def avg_sentence_length(sents):
    sent_lengths = [len(tokenize_words(s)) for s in sents]
    return reduce(lambda x, y: x + y, sent_lengths) / float(len(sent_lengths))

def number_of_grafs(grafs):
    return len(grafs)

def avg_graf_length(grafs):
    graf_lengths = [len(tokenize_words(p)) for p in grafs]
    return reduce(lambda x, y: x + y, graf_lengths) / len(graf_lengths)

def length_of_first_graf(grafs):
    return len(tokenize_words(grafs[0]))

@nohtml
def flesch_readability(text):
    rt = ReadabilityTool()
    contrib_score = rt.FleschReadingEase(text)
    return contrib_score

@nohtml
def smog_readability(text):
    rt = ReadabilityTool()
    contrib_score = rt.SMOGIndex(text)
    return contrib_score

@nohtml
def coleman_liau_readability(text):
    rt = ReadabilityTool()
    contrib_score = rt.ColemanLiauIndex(text)
    return contrib_score
    
def text_features(text):
    words = tokenize_words(text)
    words_lower = tokenize_words(text, lower=True)
    sents = tokenize_sents(text)
    grafs = tokenize_grafs(text)
 
    return {
         "word_count": word_count(words) if words is not None and len(words)>10 else None,
         "pos_word_count": pos_word_count(words_lower)  if words_lower is not None and len(words_lower)>10 else None,
         "neg_word_count": neg_word_count(words_lower)  if words_lower is not None and len(words_lower)>10 else None,
         "flesh_readability": flesch_readability(text) if text is not None and len(text)>100 else None,
         "bias_word_count": bias_word_count(text) if text is not None and len(text)>100 else None,
    }


