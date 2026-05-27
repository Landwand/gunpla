import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session, g, current_app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import json
from werkzeug.security import check_password_hash, generate_password_hash
from db import db_get_cursor, db_close, db_get_collection
from utils import check_for_json, has_error, validate_req_data
from models.kit_model import KitModel


# sets up this file as main module, setting folders & files relative to it
app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = "I buy too many models"


 #instantiate the Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# must wrap close_db() with app.teardown_appcontext in main app file due to how Flask works. 
# This will close_db() with every http req.
@app.teardown_appcontext
def close_db_with_teardown(error):
    db_close(error)

# User Class which also has properties of UserMixin (flask-login)
class User(UserMixin):
    def __init__(self, id, username, hash):
        self.id = id
        self.username = username
        self.hash = hash
    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"


# load User by ID; will return None if doesn't exist
@login_manager.user_loader
def load_user(user_id):
    cursor = db_get_cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
    except:
        app.logger.info("error running load_user")
        return None
    
    '''
    creates a new instance of User class & return it. * is an UNPACKING OPERATOR, 
    so takes value from 'user' tuple and sends it to the User class constructor.
    '''
    if user:
        return User(*user)


def check_login(username, password):
        # check for USERNAME
        cursor = get_cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cursor.fetchone()

        if rows is None:
            return "no Rows returned for Username in check_login"

        if not check_password_hash(rows[2], password):
            return "Password doesn't exist for check_login"

        # Checks Passed.
        session['user_id'] = rows['id']
        username = session['username'] = rows['username']
        password = rows['hash']
        app.logger.info("session @ User_id: %s", session['user_id'],)
        user = User(id=session['user_id'], username=username, hash=password)
        app.logger.info(" user == %s", user)

        if login_user(user) == True:
            app.logger.info("check_login successful")
        else:
            app.logger.info("check_login failed")

        app.logger.info("current_user %s", current_user)
        app.logger.info("current_user if logged-in?: %s", current_user.is_authenticated)


def db_get_kits_as_rows():
    app.logger.info("%s collection route started")
    conn = sqlite3.connect('gunpla.db')
    conn.row_factory = sqlite3.Row # use built-in Row-factory to help parse Tuples
    cur = conn.cursor()
    cur.execute ("SELECT * FROM gunpla WHERE owner_id = ? ORDER BY id ASC", (session['user_id'],))
    rows = cur.fetchall()
    return rows


def db_update_gunpla(action, kit_data=None, kit_id=None):
    if not session['user_id']:
        app.logger.info("db_update_gunpla: error --- no user_id")
        return (1,{'message' : "Error: cannot find user_id in session"}) #tuple containing 1(error) and error-message

    if kit_data:
        name = str(kit_data['name'])
        scale = int(kit_data['scale'])
        notes = str(kit_data['notes'])
        condition = str(kit_data['condition'])
        grade = str(kit_data['grade'])
        material = str(kit_data['material'])
        app.logger.info("db_update_gunpla - kit data confirmed")

    if action == "create":
        cur.execute("INSERT INTO gunpla (name, scale , material, notes, condition, grade, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)", \
            (name, scale, material, notes, condition, grade, session['user_id']))
        return 0 

    elif action == "update" or action == "edit":
        cur.execute("UPDATE gunpla SET name = ?, scale = ?, material = ?, notes = ?, condition = ?, grade = ? WHERE id = ?", (name, scale, material, notes, condition, grade, kit_id))               
        app.logger.info("FUNC: db_update_gunpla EDIT now completed!!!!! %s")
        conn.commit()
        return 0

    elif action == "delete":
        cur.execute("DELETE FROM gunpla WHERE id = ?", (kit_id,))
        return 0

    else:
        print("Unknown input - db_update_gunpla in error")
        app.logger.info("Unknown input - db_update_gunpla in error")
        return 1 # error

# Refactoring various other routes into a series of RESTful endpts

@app.route('/api/collection', methods=['GET'])
@login_required
def get_collection():
    """Retrieve all kits for the logged-in user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in.'}), 401

    # Use the refactored function from db.py
    kits = db_get_collection(user_id)
    return jsonify({'kits': kits}), 200


@app.route('/api/kit/<int:kit_id>', methods=['GET'])
@login_required
def get_kit(kit_id):
    """Retrieve a specific kit by its ID."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in.'}), 401

    with sqlite3.connect('gunpla.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gunpla WHERE id = ? AND owner_id = ?", (kit_id, user_id))
        row = cursor.fetchone()

    if row:
        return jsonify(dict(row)), 200
    else:
        return jsonify({'error': 'Kit not found.'}), 404
    

# this route looks incomplete; it validates the data, but does it actually summon the fn create_kit ()?
@app.route('/api/kit/', methods=['POST'])
@login_required
def create_kit():
    json_success, result = check_for_json(request)
    if not json_success:
        return jsonify({'error': result}), 400  # Use the error message from `check_for_json`

    data = request.get_json()
    data['owner_id'] = session['user_id']
    
    validation_success, validated_kit_data = validate_req_data(**data)

    if validation_success:
        # db_create_kit(**validated_kit_data) # pass into DB function
        db_create_kit(**validated_kit_data.model_dump())  # Use model_dump() instead of dict()

        response = {
            'message': 'Kit added successfully',
            'kit': validated_kit_data
        }
        status_code = 201
    else:
        response = {
        'error': validated_kit_data['message'],
        'details': validated_kit_data['details']
        }  
        status_code = 400
        
    return jsonify(response), status_code


@app.route('/api/kit/', methods=['DELETE'])
@login_required
def delete_kit():
    json_success, result = check_for_json(request)
    if not json_success:
        return jsonify({'error': result}), 400  # Use the error message from `check_for_json`
    
    data = request.get_json()
    data['owner_id'] = session['user_id']
    data['kit_id'] 







# no caching of request responses into browser to ensure accuracy when building/troubleshooting
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


"""
debugger function.  
To use (print to Terminal)
- in Jinja: {{ mdebug("any text or variable") }}
- find type: {{ mdebug(each) }} type of each
"""
@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))
        #print (str(type(message)), "is the type")  # prints the type
    return dict(mdebug=print_in_console)


@app.route("/", methods=["GET", "POST"])
def index():

    if not session.get('username'):
        return render_template('login.html')

    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':        
        condition = request.form.get("condition")
        grade = request.form.get("grade")
        name = request.form.get("name")
        notes = request.form.get("notes")
        scale = request.form.get("scale")
        material = request.form.get("material")
            
        kit_data = {
            'condition' : condition,
            'grade' : grade,
            'name' : name,
            'notes' : notes,
            'scale' : scale,
            'material' : material}

        has_error_result, msg, kit_vals = has_error(kit_data)
        
        if has_error_result == 0:
            kit_data = kit_vals
            db_update_gunpla(action="create", kit_data=kit_data)      
        else:
            return render_template('error.html', msg = msg)
        
        return render_template("success.html", action="add", kit_data=kit_data)


@app.route("/collection, <kits>", methods=["GET", "POST"])
@login_required
def collection(kits):
    app.logger.info("%s collection route started")
    collected_rows = db_get_collection(session['user_id'])

    # rows = get_kit_as_rows_from_db
    return render_template('collection.html', kits=collected_rows)


@app.route('/edit/<kit_id>', methods=["GET", "POST"])
@login_required
def edit(kit_id=None):

    if request.method == "GET":        
        # GET request
        print("Edit page loaded in GET mode")
        cur.execute ("SELECT * FROM gunpla WHERE id = ?", [kit_id,])
        row = cur.fetchone()
        kit_data = {
            'name' : row['name'],
            'scale' : row['scale'],
            'grade' : row['grade'],
            'condition': row['condition'],
            'notes': row['notes'],
            'material': row['material'],
            'id': row['id']}
        return render_template('edit.html', kit_data=kit_data, kit_id=kit_id)

    if request.method == "POST":
        app.logger.info("%s edit page ===== POSTING, ", kit_id)
        kit_data = {
        'condition' : request.form.get("condition"),
        'grade' : request.form.get("grade"),
        'name' : request.form.get("name"),
        'notes' : request.form.get("notes"),
        'scale' : request.form.get("scale"),
        'material' : request.form.get("material"),
        'id': kit_id}

        if request.form.get("choice") == "Delete Kit":
            app.logger.info("%s (id) delete chosen from EDIT page ",kit_id)

            if db_update_gunpla(action="delete",kit_id=kit_id) == 1 :
                app.logger.info("Kit id = %s , Error with update_gunpla DELETE ", kit_id)
            else:
                app.logger.info("update_gunpla function DELETE successful")
            return render_template('success.html', action="delete", kit_data=kit_data)

        if request.form.get("choice") == "Update Kit":
            app.logger.info("%s EDIT/ update kit*******, ", kit_id)

            has_error_result, msg, kit_vals = has_error(kit_data)

            if has_error_result == 0:
                kit_data = kit_vals
                db_update_gunpla(kit_data=kit_data, action="update", kit_id = kit_id) 
                return render_template("success.html", action="add", kit_data=kit_data)        
            else:
                return render_template('error.html', msg = msg)

    return render_template('error.html', msg="If statements not working")


@app.route('/error', methods = ["GET"])
def error(msg):
    return render_template('error.html', msg=msg)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template('error.html', msg="must provide username")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('error.html', msg="must provide password")

        password = request.form.get('password')
        username = request.form.get('username')

        # check USERNAME
        conn = sqlite3.connect('gunpla.db')
        conn.row_factory = sqlite3.Row # use built-in Row-factory to help parse Tuples
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cur.fetchone()
        conn.close()

        if rows is None:
            return render_template('error.html', msg="username is wrong!")

        if not check_password_hash(rows[2], password):
            return render_template('error.html', msg="Password error!")

        # Checks Passed. Remember which user has logged in
        session['user_id'] = rows['id']
        username = session['username'] = rows['username']
        password = rows['hash']
        app.logger.info("session @ user_id = %s", session['user_id'])
        app.logger.info("testing")

        user = User(id=session['user_id'],username=username,hash=hash)
        try:
            login_user(user)
            app.logger.info("Login OK - 365")
        except:
            app.logger.info("Login NOT OK line 369")

        # Redirect user to home page
        return redirect("/")

    # GET request
    else:
        return render_template('login.html')


@app.route("/logout")
def logout():
    conn = sqlite3.connect('gunpla.db')
    session.clear()
    logout_user()
    # Redirect user to login form
    return redirect("/")


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        pwconfirm = request.form.get('confirm')

        if not username or len(username) < 1:
            return render_template('error.html', msg="Username is too short!")
        elif not password or len(password) < 1:
            return render_template ('error.html', msg="Password is too short!")
        elif not pwconfirm or len(pwconfirm) < 1:
            return render_template ('error.html', msg="Check your confirm-password fields")
        elif not pwconfirm == password:
            return render_template('error.html', msg="Password needs to match confirm")

        # check for existing Username  
        conn = sqlite3.connect('gunpla.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cur.fetchall()
        if len(rows) > 0:
            return render_template('error.html', msg="Error: username taken!")
        
        # hash pw and store new User
        hashed_pw = generate_password_hash(password)
        app.logger.info("creating User . . .!")
        cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_pw))
        app.logger.info("user created!")
        conn.commit()

        session['username'] = username # store it for later use in app
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        rows = cur.fetchone()
        session['user_id'] = rows['id']

        conn.close()      
        return render_template('index.html')
   
    return render_template('register.html')


@app.route('/api/logout', methods = ['POST'])
@login_required
def api_logout():
    logout_user()
    session.clear()
    username = session.get('username')
    app.logger.info('logged-out Username: %s', username)
    return jsonify({'message': "Successfully logged out."}, 200)


@app.route('/api/login', methods = ['GET', 'POST'])
def api_login():
    if request.method == 'GET':
        # app.logger.info("GET method")

        if 'username' in session:
            return jsonify({'message': 'You are logged in!'}), 200
        else:
            return jsonify({'error': 'You are not logged in yet'}), 200
        
    if request.method == 'POST':
        app.logger.info("api_login route: `POST`:")
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        # verify the username and password
        login_error = check_login(username=username, password=password)

        # problem
        if login_error == True:
            app.logger.info("login error: %s", login_error)
            return jsonify({'error': login_error}), 401

        if current_user.is_authenticated == True:
            app.logger.info("`current user` is authenticated! %s", current_user)
            app.logger.info("username is: %s ", session['username'])
            messaging = {}
            messaging['message'] = "API login successful."
            return jsonify(messaging), 200

        else:
            app.logger.info("no`login_user`")
            return jsonify({'error':"login attempt failed"}), 401


@app.route('/api/chammy', methods = ["GET", "POST"])
def show():
    chammy_data = {
        'name': 'Chammy',
        'birthday': 'June 25',
        'age': 3,
        'food': 'blueberry',
        'color': 'pink'
    }
    return jsonify(chammy_data), 400
 

@app.route('/api/jsonv/', methods = ["GET", "POST"])
@login_required
def showv(v="Whatever"):
    msg = "Piew piew "
    message_dict = {'message': msg}
    return jsonify(message_dict)


@app.route('/success', methods=["GET", "POST"])
def success(action, kit_data):
    return render_template("success.html", action=action, kit_data=kit_data)