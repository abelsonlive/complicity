from complicity.common import articles, db
import numpy 
import os 

# query for removing duplicates
def remove_duplicates():
  print "removing duplicates..."
  rm_query = """
    WITH pick AS (
      SELECT url, min(id) as id FROM articles
      GROUP BY url

    )
    DELETE FROM articles WHERE id NOT IN (SELECT id FROM pick)
  """
  print "old length: %s" % len([r for r in articles.all()])
  # remove duplicates
  db.query(rm_query)
  print "new length: %s" % len([r for r in articles.all()])

def update_data(data):
  for d in data:
    articles.update(d, ["id"]) 

def add_social_media_count():
  print "adding social media sum..."
  query = """SELECT id, 
               fb_total + google_plus_ones + twitter_shares as social_media
             FROM articles"""
  data = [row for row in db.query(query)]
  update_data(data)

def add_min_to_read():
  print "adding minutes to read..."
  query = """SELECT id, word_count FROM articles"""
  data = [row for row in db.query(query)]
  new_data = []

  # calculate minutes to read
  for d in data:
    if d['word_count'] is not None:
      min_to_read = float(d['word_count']) / 250.0
    else:
      min_to_read = None
    new_row = {'id': d['id'], 'min_to_read': min_to_read}
    new_data.append(new_row)

  # update databse
  update_data(new_data)

def add_normalized_lexicon_pers():
  print "adding normalized lexicon percentages..."
  query = """SELECT id, pos_word_count, neg_word_count, bias_word_count, word_count FROM articles"""
  data = [row for row in db.query(query)]

  # calculate normalized counts
  new_data = []
  for d in data:
    wc = d['word_count']
    if wc is not None and wc > 0:
      new_row = {
        'id' : d['id'],
        'pos_word_per' : float(d['pos_word_count']) / float(wc),
        'neg_word_per' : float(d['neg_word_count']) / float(wc),
        'bias_word_per' : float(d['bias_word_count']) / float(wc)
      }
    else:
      new_row = {
        'id' : d['id'],
        'pos_word_per' : None,
        'neg_word_per' : None,
        'bias_word_per' : None   
      }
    new_data.append(new_row)

  # insert new data
  update_data(new_data)

def z_score(vec, na2zero, log):

  # convert nones to zero
  if na2zero:
    new_vec = []
    for v in vec:
      if v is not None:
        new_vec.append(v)
      else:
        new_vec.append(0)
    vec = new_vec

  # extract arr and safe array
  arr = numpy.array(vec)
  safe_arr = numpy.array([a for a in arr if a is not None])

  if log:
    safe_arr = numpy.log(safe_arr + 0.001)

  # calculate mean safely
  arr_avg = numpy.average(safe_arr)

  # calculate standard deviation safely
  arr_std = numpy.std(safe_arr)

  # loop through entire array
  arr_z = []
  for a in arr:
    if a is not None:
      if log:
        a = numpy.log(a + 0.001)
      arr_z.append((a-arr_avg)/arr_std)
    else:
      arr_z.append(None)

  return arr_z

def add_z_score_for_column_name(col_name, na2zero, log):
  print "adding z scores for %s..." % col_name

  # fetch data
  query = """SELECT id, %s FROM articles""" % col_name
  data = [row for row in db.query(query)]
  num_vector = [row[col_name] for row in data]
  id_vector = [row['id'] for row in data]

  # calculate z-scores
  num_vector_normed = z_score(vec = num_vector, na2zero = na2zero, log = log)

  # zip with ids
  items = zip(id_vector, num_vector_normed)
  
  # create new data for updating
  new_col_name = col_name + "_z" 
  new_data = [{"id" : i[0] , new_col_name : i[1]} for i in items]

  # update database
  update_data(new_data)

def post_process_db():
  remove_duplicates()
  add_social_media_count()
  add_min_to_read()
  add_normalized_lexicon_pers()

  # (col_name, na2zero, log)
  z_args = [
    ("social_media", True, True),
    ("flesh_readability", False, False),
    ("word_count", True, False),
    ("min_to_read", False, False),
    ("pos_word_per", True, False),
    ("neg_word_per", True, False),
    ("bias_word_per", True, False)
  ]

  for arg in z_args:
    add_z_score_for_column_name(
      col_name = arg[0],
      na2zero = arg[1],
      log = arg[2]
    )

if __name__ == '__main__':
  post_process_db()


