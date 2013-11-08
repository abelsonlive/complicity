# -*- coding: utf-8 -*-
# from boilerpipe.extract import Extractor
from readability.readability import Document
import requests
from HTMLParser import HTMLParser
from urlparse import urlparse
import re

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
    raw_text = s.get_data()
    raw_text = re.sub(r'\n|\t', ' ', raw_text)
    return re.sub('\s+', ' ', raw_text).strip()

def parse_url(url):
  o = urlparse(url)
  return "%s://%s%s" % (o.scheme, o.netloc, o.path)

def extract_article(url):
  r = requests.get(url)
  
  # the the url exists, continue
  if r.status_code == 200:
    
    # extract and parse response url
    url = parse_url(r.url)

    # extract html
    html = r.content.decode('utf-8', errors='ignore')

    # run boilerpipe
    # boilerpipe_extractor = Extractor(html=html)

    # run readability
    readability_extractor = Document(html)

    html = readability_extractor.summary()
    # return article data
    return {
      'title': readability_extractor.short_title(),
      'html': html,
      'content': strip_tags(html).encode('utf-8', errors='ignore'),
      'url': url
    }

  # otherwise return an empty dict
  else:
    return {}

if __name__ == '__main__':
  url = 'http://www.eleconomista.net/capital/148956-suben-inversiones-del-igss.html'
  print extract_article(url)