import dataset
db = dataset.connect('postgresql://brian:mc@localhost:5432/news')
articles = db['articles']