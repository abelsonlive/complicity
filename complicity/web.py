import json
from datetime import datetime

from flask import Response, request
from flask import Flask

from complicity import default_settings
from complicity.common import db

app = Flask(__name__)
app.config.from_object(default_settings)


class JSONEncoder(json.JSONEncoder):
    """ This encoder will serialize all entities that have a to_dict
    method by calling that method and serializing the result. """

    def encode(self, obj):
        if hasattr(obj, 'to_dict'):
            obj = obj.to_dict()
        return super(JSONEncoder, self).encode(obj)

    def default(self, obj):
        if hasattr(obj, 'as_dict'):
            return obj.as_dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        raise TypeError("%r is not JSON serializable" % obj)


def jsonify(obj, status=200, headers=None):
    """ Custom JSONificaton to support obj.to_dict protocol. """
    jsondata = json.dumps(obj, cls=JSONEncoder)
    if 'callback' in request.args:
        jsondata = '%s(%s)' % (request.args.get('callback'), jsondata)
    return Response(jsondata, headers=headers,
                    status=status, mimetype='application/json')


@app.route("/sql")
def sql():
  # parse args  
  query = request.args.get('q', None)

  # return json 
  return "<h1 style='font-family:Helvetica'> bubble-up </h1>"

@app.route("/")
def index():
  """
  example:
  localhost:5006/?soc_dir=-1&soc_imp=0.2&read_dir=-1&read_imp=0.2&len_dir=1&len_imp=0.2&pos_dir=1&pos_imp=-1&neg_dir=1&neg_imp=0.2&bias_dir=1&bias_imp=0.2
  """
  # parse args  
  soc_dir = int(request.args.get('soc_dir', 1))
  soc_imp = float(request.args.get('soc_imp', 0))

  read_dir = int(request.args.get('read_dir', 1))
  read_imp = float(request.args.get('read_imp', 0))

  len_dir = int(request.args.get('len_dir', 1))
  len_imp = float(request.args.get('len_imp', 0))

  pos_dir = int(request.args.get('pos_dir', 1))
  pos_imp = float(request.args.get('pos_imp', 0))

  neg_dir = int(request.args.get('neg_dir', 1))
  neg_imp = float(request.args.get('neg_imp', 0))

  bias_dir = int(request.args.get('bias_dir', 1))
  bias_imp = float(request.args.get('bias_imp', 0))
  
  # pack up vals
  vals =  (
    soc_dir, soc_imp,
    read_dir, read_imp,
    len_dir, len_imp,
    pos_dir, pos_imp,
    neg_dir, neg_imp,
    bias_dir, bias_imp
  )
  print vals

  # generate query
  query = """SELECT 
               url, title, namn, 
               social_media, flesh_readability, word_count,
               pos_word_per, neg_word_per, bias_word_per,

               (social_media_z * %d * %f) + 
               (flesh_readability_z * %d * %f) +
               (word_count_z * %d * %f) + 
               (pos_word_per_z * %d * %f) +
               (neg_word_per_z * %d * %f) +
               (bias_word_per_z * %d * %f) AS pref_score

             FROM articles
             ORDER BY pref_score DESC
             LIMIT 5
          """ % vals

  print query

  # return json 
  return jsonify([row for row in db.query(query)])

if __name__ == '__main__':
    app.debug = default_settings.DEBUG
    app.run(port=5006)



