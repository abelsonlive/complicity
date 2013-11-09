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
  return jsonify([row for row in db.query(query)])

@app.route("/")
def index():
  # parse args  
  query = request.args.get('q', None)

  # return json 
  return jsonify([row for row in db.query(query)])

if __name__ == '__main__':
    app.debug = default_settings.DEBUG
    app.run(port=5006)



