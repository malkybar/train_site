from  flask import Flask, request, jsonify, render_template
import requests
import json
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

USERNAME = 'rttapi_malcybar'
PASSWORD = '88128c2486220ad3b31c9d5e3d61a6d08a2bc0db'

@app.route("/")
def home():
     return render_template('home.html'), 200

@app.route('/results/<station>')
def results(station, methods=['GET']):
     json_data = None
     error_message = None

     try:
          response = requests.get('https://api.rtt.io/api/v1/json/search/' + station, auth=(USERNAME, PASSWORD))
          response.raise_for_status()
          data = response.json()
     except requests.exceptions.RequestException as e:
          error_message = str(e)

     return render_template('results.html', data=data)
     
@app.route("/live_times")
def live():
     return render_template("live_times.html"), 200
     

@app.route("/saved_stations")
def saved():
     return render_template("saved_stations.html"), 200

if __name__ == "__main__":
     app.run(host='0.0.0.0', debug=True)