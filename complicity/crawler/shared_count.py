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
    
    # deal with facebook data
    if dump.has_key('Facebook'):
      dump_fb = dump['Facebook']
      fb_dict = {
        'fb_comments_box' : dump_fb['commentsbox_count'] if dump_fb.has_key('commentsbox_count') else 0,
        'fb_clicks' : dump_fb['click_count'] if dump_fb.has_key('click_count') else 0,
        'fb_total' : dump_fb['total_count'] if dump_fb.has_key('total_count') else 0,
        'fb_comments' : dump_fb['comment_count']  if dump_fb.has_key('comment_count') else 0,
        'fb_likes' : dump_fb['like_count'] if dump_fb.has_key('like_count') else 0,
        'fb_shares' : dump_fb['share_count'] if dump_fb.has_key('share_count') else 0
      }
    else:
      fb_dict = {
        'fb_comments_box': 0,
        'fb_clicks' : 0,
        'fb_total' : 0,
        'fb_comments' : 0,
        'fb_likes' : 0,
        'fb_shares' : 0   
      }

    # non facebook data
    non_fb_dict = {
      'stumble_upon_shares' : dump['StumbleUpon'],
      'reddit_shares' : dump['Reddit'],
      'delicious_shares' : dump['Delicious'],
      'pinterest_shares' : dump['Pinterest'],
      'twitter_shares' : dump['Twitter'],
      'diggs' : dump['Diggs'],
      'linked_in_shares' : dump['LinkedIn'],
      'google_plus_ones' : dump['GooglePlusOne'],
      'buzz_shares' : dump['Buzz']
    }

    # combine dicts and return
    return dict(fb_dict.items() + non_fb_dict.items())
    
  # otherwise return an empty dict
  else:
    return {}