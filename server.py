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

@app.route('/live_times/results/<station1>/<query>/<station2>')
def dep_results(station1, query, station2, methods=['GET']):
     json_data = None
     error_message = None

     try:
          if station2 == 'BLANK' and query == 'to':
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1, auth=(USERNAME, PASSWORD))
          elif query == 'to':
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1 + '/to/' + station2, auth=(USERNAME, PASSWORD))
          elif station2 == 'BLANK' and query == 'from':
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1 + '/arrivals', auth=(USERNAME, PASSWORD))
          elif query == 'from':
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1 + '/from/' + station2 + '/arrivals', auth=(USERNAME, PASSWORD))
          
          response.raise_for_status()
          data = response.json()
     except requests.exceptions.RequestException as e:
          error_message = str(e)

     return render_template('results.html', data=data), 200
     
@app.route("/live_times/")
def live():
     f = open('stations.json')
     data = json.load(f)
     
     f.close()
     return render_template('live_times.html', data=data), 200
     

@app.route("/saved_stations")
def saved():
     return render_template("saved_stations.html"), 200

if __name__ == "__main__":
     app.run(host='0.0.0.0', debug=True)