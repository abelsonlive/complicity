import os
import dataset

db = dataset.connect(os.getenv('DATABASE_URL'))
articles = db['articles']
newspapers = db['newspapers']