import requests
import urllib

def shared_count(url):
  """
  get shared count data for a url
  """
  # hit api
  api_url = "http://api.sharedcount.com/?url=" + urllib.quote_plus(url)
  r = requests.get(api_url)

  # if everythings okay, return data
  if r.status_code == 200:
    dump = r.json()
    return {
      'stumble_upon_shares' : dump['StumbleUpon'],
      'reddit_shares' : dump['Reddit'],
      'delicious_shares' : dump['Delicious'],
      'pinterest_shares' : dump['Pinterest'],
      'twitter_shares' : dump['Twitter'],
      'diggs' : dump['Diggs'],
      'linked_in_shares' : dump['LinkedIn'],
      'fb_comments_box' : dump['Facebook']['commentsbox_count'],
      'fb_clicks' : dump['Facebook']['click_count'],
      'fb_total' : dump['Facebook']['total_count'],
      'fb_comments' : dump['Facebook']['comment_count'],
      'fb_likes' : dump['Facebook']['like_count'],
      'fb_shares' : dump['Facebook']['share_count'],
      'google_plus_ones' : dump['GooglePlusOne'],
      'buzz_shares' : dump['Buzz']
    }

  # otherwise return an empty dict
  else:
    return {}