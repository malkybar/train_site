#imports
from flask import Flask, request, render_template, g, redirect, session
import requests, json, sqlite3, secrets, re

app = Flask(__name__)

#generate random token for user
app.secret_key = secrets.token_hex(16)

#api authentication details
USERNAME = 'rttapi_malcybar'
PASSWORD = '88128c2486220ad3b31c9d5e3d61a6d08a2bc0db'

#location of sqlite3 database
db_location = 'var/database.db'

#function to read in database
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

#function to create database, called using external python script          
def init_db():
     with app.app_context():
          db = get_db()
          with app.open_resource('schema.sql', mode='r') as f:
               db.cursor().executescript(f.read())
          db.commit()

#function to check if an email is valid          
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

#function to check if password is valid
def validate_password(password):
    if len(password) >= 8:
        return True
    return False

#function to check if username is valid
def validate_username(username):
    if len(username) >= 1:
        return True
    return False

#function to read json file containin stations and station codes
def read_stations():
     f = open('stations.json')
     stationdata = json.load(f)
     f.close()
     return stationdata
     
#default root
@app.route("/")
def home():
     #return home page template
     return render_template('home.html'), 200

#/live_times
@app.route('/live_times/departures/<station1>/to/<station2>')
def depart(station1, station2, methods=['GET']):
     json_data = None
     error_message = None
     stationdata = read_stations()

     #get json from live train data server api
     try:
          if station2 == 'BLANK':
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1, auth=(USERNAME, PASSWORD))
          else:
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1 + '/to/' + station2, auth=(USERNAME, PASSWORD))
          
          response.raise_for_status()
          data = response.json()
     except requests.exceptions.RequestException as e:
          error_message = str(e)

     #return departures page template
     return render_template('departures.html', data=data, station1=station1, station2=station2, stationdata=stationdata), 200

@app.route('/live_times/arrivals/<station1>/from/<station2>')
def arrive(station1, station2, methods=['GET']):
     json_data = None
     error_message = None
     stationdata = read_stations()

     #get json from live train data server api
     try:
          if station2 == 'BLANK':
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1 + '/arrivals', auth=(USERNAME, PASSWORD))
          else:
               response = requests.get('https://api.rtt.io/api/v1/json/search/' + station1 + '/from/' + station2 + '/arrivals', auth=(USERNAME, PASSWORD))
          
          response.raise_for_status()
          data = response.json()
     except requests.exceptions.RequestException as e:
          error_message = str(e)
          
     #return arrivals page template
     return render_template('arrivals.html', data=data, station1=station1, station2=station2, stationdata=stationdata), 200

#/live_times route     
@app.route("/live_times/")
def live():
     data = read_stations()
     return render_template('live_times.html', data=data), 200
     
#/register route
@app.route('/register', methods=['GET', 'POST'])
def register():
     error = ""
     if request.method == 'POST':
               #get username, password and email
               username = request.form['username']
               password = request.form['password']
               email = request.form['email']
               
               #connect to database
               conn = get_db()
               cursor = conn.cursor()

               #checks if username has already been taken using sql code
               cursor.execute("SELECT * FROM users WHERE username=?", (username,))
               existing_user = cursor.fetchone()

               #validation for details, displays error on page if inputs are invalid
               if existing_user and validate_email(email) == False and validate_password(password) == False:
                    conn.close()
                    error = "Username already exists! Please choose a different one.\nInvalid Password and Email Address"
                    return render_template("register.html", error=error)
               
               elif existing_user and validate_password(password) == False:
                    error = "Username already exists! Please choose a different one.\nInvalid Password"
                    return render_template("register.html", error=error)
               
               elif existing_user and validate_email(email) == False:
                    error = "Username already exists! Please choose a different one.\nInvalid Email"
                    return render_template("register.html", error=error)
               
               elif validate_email(email) == False and validate_password(password) == False:
                    error = "Invalid Password and Email Address"
                    return render_template("register.html", error=error)
               
               elif existing_user:
                    conn.close()
                    error = "Username already exists! Please choose a different one."
                    return render_template("register.html", error=error)
               
               elif validate_password(password) == False:
                    error = "Invalid Password"
                    return render_template("register.html", error=error)
               
               elif validate_email(email) == False:
                    error = "Invalid Email Address"
                    return render_template("register.html", error=error)
               
               else: #if all is valid insert form data into users table
                    cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
                    conn.commit()
                    conn.close()
                    return redirect('/login')

     return render_template('register.html', error=error)

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
     error = ""
     if request.method == 'POST':
          #get username and password
          username = request.form['username']
          password = request.form['password']

          #connect to database
          conn = get_db()
          cursor = conn.cursor()

          #using sql statement finds users
          cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
          user = cursor.fetchone()

          #checks if details are valid
          if user:
               session['username'] = username
               conn.close()
               return redirect('/account')
          else:
               conn.close()
               error = "Invalid Username or Password"
               return render_template("login.html", error=error)

     return render_template('login.html')

#/account route
@app.route('/account')
def dashboard():
     if 'username' in session:
          return render_template('account.html', username=session.get('username'))
     else:
          return redirect('/login')

#/logout route   
@app.route('/logout')
def logout():
     session.pop('username', None)
     return redirect('/')

#update database route
@app.route('/update_database', methods=['POST'])
def update_database():
     try:
          username = session.get('username')
          #check if user is in session
          if username:
               data = request.json
               if all(key in data for key in ['key1', 'key2', 'key3', 'key4', 'key5']): #validate keys in the received json
                    conn = get_db()
                    cursor = conn.cursor()

                    #find user id for username in session
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    user = cursor.fetchone()

                    if user:
                         user_id = user[0]
                         
                         #insert data to be saved into saves table
                         cursor.execute("INSERT INTO saves (crs_1, station_1, crs_2, station_2, dep_arr, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                                        (data['key1'], data['key2'], data['key3'], data['key4'], data['key5'], user_id))
                         conn.commit()
                         conn.close()
                         
                         #redirect to saved stations page
                         return redirect('/saved_stations')
                    else:
                         conn.close()
                         return 'User not found'
               else:
                    return 'Invalid data received' #handle invalid or missing keys in received json
          else:
               return redirect('/login')
     except Exception as e:
          return f"An error occurred: {str(e)}"

#/saved_stations route
@app.route("/saved_stations")
def saved():
     try:
          username = session.get('username')  #get the username from the session

          #checks if a user is logged in
          if username:
               conn = get_db()  # Replace with your database connection details
               cursor = conn.cursor()

               #get users data from database
               cursor.execute("SELECT * FROM saves WHERE user_id = (SELECT id FROM users WHERE username = ?)",(username,))
               data = cursor.fetchall()

               conn.close()

               # Render an HTML page with the fetched data
               return render_template('saved_stations.html', data=data)
          else: 
               return redirect('/login') #redirects to login page if no active session
     except Exception as e:
          return f"An error occurred: {str(e)}"

#/gallery route
@app.route("/gallery")
def gallery():
     #return home page template
     return render_template('gallery.html'), 200

if __name__ == "__main__":
     app.run(host='0.0.0.0', debug=True)