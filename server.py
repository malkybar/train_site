from  flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['Cors_HEADERS'] = 'Content-Type'

@app.route("/")
def hello():
     return "hello world"
 
@app.route("/trains", methods=["GET", "POST"])
def trains():
    endpoint = 'api.rtt.io/api/v1/json/search/DRM'
    return jsonify(request.args.get(endpoint))