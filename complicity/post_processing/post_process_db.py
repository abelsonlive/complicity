from complicity.common import articles, db

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

