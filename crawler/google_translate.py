# -*- coding: utf-8 -*-
import os
import requests
import urllib

# language lookup
language_lookup = {
  'Afrikaans' : 'af',
  'Albanian' : 'sq',
  'Arabic' : 'ar',
  'Azerbaijani' : 'az',
  'Basque' : 'eu',
  'Bengali' : 'bn',
  'Belarusian' : 'be',
  'Bulgarian' : 'bg',
  'Catalan' : 'ca',
  'Chinese Simplified' : 'zh-CN',
  'Chinese Traditional' : 'zh-TW',
  'Croatian' : 'hr',
  'Czech' : 'cs',
  'Danish' : 'da',
  'Dutch' : 'nl',
  'English' : 'en',
  'Esperanto' : 'eo',
  'Estonian' : 'et',
  'Filipino' : 'tl',
  'Finnish' : 'fi',
  'French' : 'fr',
  'Galician' : 'gl',
  'Georgian' : 'ka',
  'German' : 'de',
  'Greek' : 'el',
  'Gujarati' : 'gu',
  'Haitian Creole' : 'ht',
  'Hebrew' : 'iw',
  'Hindi' : 'hi',
  'Hungarian' : 'hu',
  'Icelandic' : 'is',
  'Indonesian' : 'id',
  'Irish' : 'ga',
  'Italian' : 'it',
  'Japanese' : 'ja',
  'Kannada' : 'kn',
  'Korean' : 'ko',
  'Latin' : 'la',
  'Latvian' : 'lv',
  'Lithuanian' : 'lt',
  'Macedonian' : 'mk',
  'Malay' : 'ms',
  'Maltese' : 'mt',
  'Norwegian' : 'no',
  'Persian' : 'fa',
  'Polish' : 'pl',
  'Portuguese' : 'pt',
  'Romanian' : 'ro',
  'Russian' : 'ru',
  'Serbian' : 'sr',
  'Slovak' : 'sk',
  'Slovenian' : 'sl',
  'Spanish' : 'es',
  'Swahili' : 'sw',
  'Swedish' : 'sv',
  'Tamil' : 'ta',
  'Telugu' : 'te',
  'Thai' : 'th',
  'Turkish' : 'tr',
  'Ukrainian' : 'uk',
  'Urdu' : 'ur',
  'Vietnamese' : 'vi',
  'Welsh' : 'cy',
  'Yiddish' : 'yi'
}

def translate_to_english(url, language, text):
  """
  see documentation here: https://developers.google.com/translate/v2/using_rest
  """
  # google api parameters
  api_key = os.getenv('GOOGLE_API_KEY')
  simple_api_url = 'https://www.googleapis.com/language/translate/v2?key=' + \
           api_key + '&target=en&q='
  complex_api_url = 'https://www.googleapis.com/language/translate/v2?key=' + \
           api_key + '&source=%s&target=en&q='

  # get lengths so we can translate in acceptably-sized chunks
  max_chunk_len = 1000
  simple_chunk_len = max_chunk_len - (len(api_key) + len(simple_api_url))
  complex_chunk_len = max_chunk_len - (len(api_key) + len(complex_api_url))

  # try to submit a source language
  if language_lookup.has_key(language):
    query_url = complex_api_url % language_lookup[language]
    chunk_len = complex_chunk_len

  # otherwise let google guess language
  else:
    query_url = simple_api_url
    chunk_len = simple_chunk_len

  # generate text_ranges
  text_len_index = len(text) - 1
  text_ranges = range(0, text_len_index, chunk_len) + [text_len_index]

  # loop through text ranges and generate query urls google for translation
  translated_chunks = []
  for i, start in enumerate(text_ranges[:-1]):

    # chunk text
    end = text_ranges[i+1]
    text_chunk = text[start:end]

    # hit url
    url = query_url + urllib.quote_plus(text_chunk)
    r = requests.get(url)

    # print r.status_code, url
    if r.status_code == 200:
      translated_chunks.append(r.json()['data']['translations'][0]['translatedText'])
    else:
      translated_chunks.append("")

  # print translated_chunks
  return " ".join(translated_chunks)

