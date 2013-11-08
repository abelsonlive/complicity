import os
import dataset
<<<<<<< HEAD
import os 
=======

>>>>>>> 2cc94996b0a4cd4aa5744066783d1b869dc3e1ee
db = dataset.connect(os.getenv('DATABASE_URL'))
articles = db['articles']
newspapers = db['newspapers']