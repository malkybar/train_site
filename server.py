from  flask import Flask, request, jsonify, render_template, g
import requests, json, sqlite3
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

USERNAME = 'rttapi_malcybar'
PASSWORD = '88128c2486220ad3b31c9d5e3d61a6d08a2bc0db'

db_location = 'var/database.db'
def get_db():
     db = getattr(g, 'db', None)
     if db is None:
          db = sqlite3.connect(db_location)
          g.db = db
     return db

@app.teardown_appcontext
def close_db_connection(exception):
     db = getattr(g, 'db', None)
     if db is not None:
          db.close()
          
def init_db():
     with app.app_context():
          db = get_db()
          with app.open_resource('schema.sql', mode='r') as f:
               db.cursor().executescript(f.read())
          db.commit()

@app.route("/")
def home():
     return render_template('home.html'), 200

@app.route('/live_times/departures/<station1>/to/<station2>')
def depart(station1, station2, methods=['GET']):
     json_data = None
     error_message = None

     try:
          if station2 == 'BLANK':
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1, auth=(USERNAME, PASSWORD))
          else:
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1 + '/to/' + station2, auth=(USERNAME, PASSWORD))
          
          response.raise_for_status()
          data = response.json()
     except requests.exceptions.RequestException as e:
          error_message = str(e)

     return render_template('departures.html', data=data), 200

@app.route('/live_times/arrivals/<station1>/from/<station2>')
def arrive(station1, station2, methods=['GET']):
     json_data = None
     error_message = None

     try:
          if station2 == 'BLANK':
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1 + '/arrivals', auth=(USERNAME, PASSWORD))
          else:
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1 + '/from/' + station2 + '/arrivals', auth=(USERNAME, PASSWORD))
          
          response.raise_for_status()
          data = response.json()
     except requests.exceptions.RequestException as e:
          error_message = str(e)

     return render_template('arrivals.html', data=data), 200
     
@app.route("/live_times/")
def live():
     f = open('stations.json')
     data = json.load(f)
     
     f.close()
     return render_template('live_times.html', data=data), 200
     

@app.route("/saved_stations")
def saved():
     db = get_db()
     db.cursor().execute('insert into user values ("1", "hello@world.com", "1234")')
     db.commit()
     
     page = []
     page.append('<html><ul>')
     sql = "SELECT * FROM user"
     for row in db.cursor().execute(sql):
          page.append('<li>')
          page.append(str(row))
          page.append('</li>')
     
     page.append('</ul></html>')
     return ''.join(page)
     #return render_template("saved_stations.html"), 200

if __name__ == "__main__":
     app.run(host='0.0.0.0', debug=True)