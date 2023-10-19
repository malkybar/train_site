from  flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

@app.route("/")
def hello():
     return "hello world"

USERNAME = 'rttapi_malcybar'
PASSWORD = '88128c2486220ad3b31c9d5e3d61a6d08a2bc0db'

@app.route("/train")
def get_train():
     try:
          auth = HTTPBasicAuth(USERNAME, PASSWORD)
        
          # Make a GET request to the authenticated endpoint
          response = requests.get('https://api.rtt.io/api/v1//json/search/DRM/2023/10/19/1206', auth=auth)

          # Check for HTTP errors
          response.raise_for_status()

          data = response.json()
          return jsonify(data)
     
     except requests.exceptions.RequestException as e:
          return jsonify({"error": str(e)}), 500  # Internal Server Error

if __name__ == "__main__":
     app.run(host='0.0.0.0', debug=True)