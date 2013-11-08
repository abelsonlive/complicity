import os
import dataset
import os 

db = dataset.connect(os.getenv('DATABASE_URL'))
articles = db['articles']
newspapers = db['newspapers']