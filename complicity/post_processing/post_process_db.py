from complicity.common import articles, db
import numpy 

# query for removing duplicates
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


def z_score(vec, log=False):

  # convert to numpy array
  arr = numpy.array(vec)

  # if log, then log
  if log:
    arr = numpy.log(arr + 0.001)

  # calculate mean
  arr_avg = numpy.average(arr)

  # calculate standard deviation
  arr_std = numpy.std(arr)

  # 
  return [(a-arr_avg)/arr_std for a in arr]


def add_z_score_for_column_name(col_name, log = False):

  # fetch data
  query = """SELECT %s FROM articles""" % col_name
  data = [row for row in db.query(query)]
  num_vector = [row[col_name] for row in data]
  id_vector = [row['id'] for row in data]

  # calculate z-scores
  num_vector_normed = z_score(num_vector)

  # zip with ids
  items = zip(id_vector, num_vector_normed)
  
  print items

  # create new data for updating 
  new_data = [{"id" : i[0] , col_name + "_z" : i[1]} for i in items]

  for new_datum in new_data:
    articles.update(new_datum, ["id"])

