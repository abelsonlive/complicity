# -*- coding: utf-8 -*-
import feedparser
from thready import threaded

# custom modules:
from complicity.common import articles, db
from complicity.crawler.article_extractor import extract_article
from complicity.crawler.shared_count import shared_count
from complicity.crawler.google_translate import translate_to_english
from complicity.crawler.text_features import text_features


# query for existing rss feeds
query = """ SELECT * from newspapers WHERE rss != '' and language = 'English' """

# fetch data
newspaper_data = [row for row in db.query(query)]

def zip_entries(entries, newspaper_datum):
  """
  zip entries into tuple with newspaper datum
  for use with threaded()
  """
  return [(entry, newspaper_datum) for entry in entries]

def parse_one_entry(feed_item):
  """
  parse an entry in an rss feed
  """

  # breakout tuple
  entry, newspaper_datum = feed_item

  # extract url
  url = entry['link']

  # extract language
  language = newspaper_datum['language']

  # extract article from url's html
  article_datum = extract_article(url)

  # get the cleaned url
  if article_datum.has_key('url') and article_datum.has_key('content'):
    clean_url = article_datum['url']

    # extract shared count data using the cleaned url
    # sometimes this fails because of weird facebook formattting
    try:
      share_datum = shared_count(clean_url)
    except:
      share_datum = {}

    # extract text features
    text_features_datum = text_features(article_datum['content'])

    # # if article is not in english, translate
    # if language != 'English':
    #   translation_datum = {
    #     'english_content' : translate_to_english(clean_url, language, article_datum['content'])
    #   }

    # # otherwise return english content
    # else:
    #   translation_datum = {
    #     'english_content' : article_datum['content']
    #   }
    print "upserting %s\n" % clean_url
  else:
    print '**ERROR parsing %s' % url
    share_datum = {}
    text_features_datum = {}
    # translation_datum = {}


  # put all the data together
  complete_datum = dict(
    article_datum.items() + 
    newspaper_datum.items() + 
    share_datum.items() +
    text_features_datum.items() # +
    # translation_datum.items()
  )

  # remove pesky id column
  complete_datum.pop('id', None)
  
  # upsert the data
  articles.insert(complete_datum, ["url"])
  

def parse_one_feed(newspaper_datum):
  """
  parse all the items in an rss feed
  """
  rss = newspaper_datum['rss']
  print "parsing %s\n" % rss
  feed_data = feedparser.parse(rss)
  feed_items = zip_entries(feed_data['entries'], newspaper_datum)

  # thread that shit!
  threaded(feed_items, parse_one_entry, 3, 1000)

  # # debug mode:
  # for item in feed_items:
  #   parse_one_entry(item)

def parse_all_feeds(newspaper_data):
  """
  parse all teh feedz
  """
  # thread that shit!
  threaded(newspaper_data, parse_one_feed, 2, 25)

  # # debug mode:
  # for datum in newspaper_data:
  #   parse_one_feed(datum)

def run():
  """
  run the crawler
  """
  # parse all teh feedz
  parse_all_feeds(newspaper_data) 

if __name__ == '__main__':
  run()