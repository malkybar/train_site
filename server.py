from  flask import Flask, request, render_template, g, redirect, url_for, session
import requests, json, sqlite3, secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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
          with app.open_resource('var/schema.sql', mode='r') as f:
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
     return render_template("saved_stations.html"), 200

@app.route("/account")
def account():
     return render_template("account.html"), 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
          username = request.form['username']
          password = request.form['password']
          email = request.form['email']
          
          conn = get_db()
          cursor = conn.cursor()

          cursor.execute("SELECT * FROM users WHERE username=?", (username,))
          existing_user = cursor.fetchone()

          if existing_user:
               conn.close()
               return "Username already exists! Please choose a different one."
          else:
               cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
               conn.commit()
               conn.close()
               return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = username  # Store username in session
            conn.close()
            return redirect('/dashboard')
        else:
            conn.close()
            return "Invalid username or password. Please try again."

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome, {session['username']}! This is your dashboard."
    else:
        return redirect('/login')
   
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == "__main__":
     app.run(host='0.0.0.0', debug=True)