from  flask import Flask, request, jsonify, render_template
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

USERNAME = 'rttapi_malcybar'
PASSWORD = '88128c2486220ad3b31c9d5e3d61a6d08a2bc0db'

@app.route("/")
def home():
     return render_template('home.html'), 200

@app.route("/live_times/<station>")
def get_train(station):
     try:
          auth = HTTPBasicAuth(USERNAME, PASSWORD)
        
          # Make a GET request to the authenticated endpoint
          response = requests.get('https://api.rtt.io/api/v1//json/search/' + station , auth=auth)

          # Check for HTTP errors
          response.raise_for_status()

          data = response.json()
          return jsonify(data)
     
     except requests.exceptions.RequestException as e:
          return jsonify({"error": str(e)}), 500  # Internal Server Error
     

@app.route("/saved_stations")
def route():
     return render_template("saved_stations.html"), 200

if __name__ == "__main__":
     app.run(host='0.0.0.0', debug=True)