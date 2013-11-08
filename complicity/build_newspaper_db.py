import dataset
import json

def parse_file(f):

  data = []
  # extract columns, lower case
  columns = [c['label'].lower() for c in f['cols']]

  # loop through rows
  for row in f['rows']:

    this_row = {}
    cells = row['c']

    # loop through cells
    for i, cell in enumerate(cells):

      # assign value to associated column key
      this_row[columns[i]] = cell['v']
    
    # remove id column
    this_row.pop('id', None)
    
    # append to list
    data.append(this_row)

  return data

def files_to_database(easy=True):

  # connect to database
  db = dataset.connect('postgresql://brian:mc@localhost:5432/news')
  table = db['newspapers']
  # table.delete()
  # table = db['newspapers']

  if not easy:
    # read in list of json files
    file_list = json.load(open('big-data-file.json'))

    # loop through list of json files
    for i, f in enumerate(file_list):

      # parse and insert
      table.insert_many(parse_file(f)) 

  else:
    data = json.load(open('all-newspapers.json'))['results']
    table.insert_many(data)

if __name__ == '__main__':
  files_to_database()

