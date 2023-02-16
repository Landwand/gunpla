import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

# for server-side session storage

# sets up this file as main module, setting folders & files relative to it
app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = "I buy too many models"

 #instantiate the Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# con = sqlite3.connect("gunpla.db")  
 # threading issue when writing to db -- ask about it
 # isolation level = autocommit > on.  Ask about this, too
conn = sqlite3.connect('gunpla.db', check_same_thread=False, isolation_level=None) # accesses the DB, or implicitly creates it in DIR
conn.row_factory = sqlite3.Row # use built-in Row-factory to help parse Tuples
cur = conn.cursor()


# User Class which also has properties of UserMixin (flask-login)
class User(UserMixin):
    def __init__(self, id, username, hash):
        self.id = id
        self.username = username
        self.hash = hash
    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"


# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        conn = sqlite3.connect('gunpla.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
    except:
        app.logger.info("cannot find username from load_user")
        return None
    finally:
        c.close()
    '''
    creates a new instance of User class & return it. * is an UNPACKING OPERATOR, 
    so takes value from 'user' tuple and sends it to the User class constructor.
    '''
    if user:
        return User(*user)



def has_error(inputs):

    app.logger.info("check_inputs started")
    app.logger.info("inputs %s", inputs)

    #initilize return values
    check_value = 0 # 1 in case-of error
    msg = "good"
    kit_vals = inputs
        
    name = inputs['name']
    scale = inputs['scale']
    notes = inputs['notes']
    condition = inputs['condition']
    grade = inputs['grade']
    material = inputs['material']
    
    if len(name) < 1:
        msg = "name too short"
        app.logger.info(msg)
        check_value = 1 # error
        return check_value, msg, kit_vals  
    if not condition:
        condition = 'new'
    if not grade:
        grade = None
    if not material:
        material = 'plastic'
    if not notes:
        notes = None

    if not scale:
        match grade:
            case "hg":
                scale = 144
            case "fg":
                scale = 144
            case "rg":
                scale = 144
            case "mg":
                scale = 100
            case "eg":
                scale = 144
            case "pg":
                scale = 60
            case _:
                scale = None        
    try:
        if int(scale) < 1:
            check_value = 1
            msg = "scale too small"
            return check_value, msg, kit_vals
    except:
        msg = "ERROR: 'Scale' not a valid number!"
        check_value = 1
        return check_value, msg, kit_vals

    # save corrected form inputs to kit_vals and prep to return
    kit_vals = {}
    for variable in ["name", "scale", "grade", "condition", "material", "notes"]:
        kit_vals[variable] = eval(variable)
    # check_value: 0 = good, 1 = error
    return check_value, msg, kit_vals


def update_gunpla(action, kit_data=None, kit_id=None):

    if not session['user_id']:
        app.logger.info("update_gunpla: error --- no user_id")
        return 1

    if kit_data:
        name = str(kit_data['name'])
        scale = int(kit_data['scale'])
        notes = str(kit_data['notes'])
        condition = str(kit_data['condition'])
        grade = str(kit_data['grade'])
        material = str(kit_data['material'])
        app.logger.info("update gunpla - kit data confirmed")

    if action == "create":
        cur.execute("INSERT INTO gunpla (name, scale , material, notes, condition, grade, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)", \
            (name, scale, material, notes, condition, grade, session['user_id']))
        return 0 

    elif action == "update" or action == "edit":
        cur.execute("UPDATE gunpla SET name = ?, scale = ?, material = ?, notes = ?, condition = ?, grade = ? WHERE id = ?", (name, scale, material, notes, condition, grade, kit_id))               
        app.logger.info("FUNC: update_gunpla EDIT now completed!!!!! %s")
        conn.commit()
        return 0

    elif action == "delete":
        cur.execute("DELETE FROM gunpla WHERE id = ?", (kit_id,))
        return 0

    else:
        print("Unknown input - update_gunpla in error")
        app.logger.info("Unknown input - update_gunpla in error")
        return 1 # error


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
            update_gunpla(action="create", kit_data=kit_data)      
        else:
            return render_template('error.html', msg = msg)
        
        return render_template("success.html", action="add", kit_data=kit_data)


@app.route('/collection, <kits>', methods=["GET", "POST"])
@login_required
def collection(kits):

    conn = sqlite3.connect('gunpla.db')
    conn.row_factory = sqlite3.Row # use built-in Row-factory to help parse Tuples
    cur = conn.cursor()
    cur.execute ("SELECT * FROM gunpla WHERE owner_id = ? ORDER BY id ASC", (session['user_id'],))
    rows = cur.fetchall()
    return render_template('collection.html', kits=rows)


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

            if update_gunpla(action="delete",kit_id=kit_id) == 1 :
                app.logger.info("Kit id = %s , Error with update_gunpla DELETE ", kit_id)
            else:
                app.logger.info("update_gunpla function DELETE successful")
            return render_template('success.html', action="delete", kit_data=kit_data)

        if request.form.get("choice") == "Update Kit":
            app.logger.info("%s EDIT/ update kit*******, ", kit_id)

            has_error_result, msg, kit_vals = has_error(kit_data)

            if has_error_result == 0:
                kit_data = kit_vals

                update_gunpla(kit_data=kit_data, action="update", kit_id = kit_id) 
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

        # check PW
        if not check_password_hash(rows[2], password):
            return render_template('error.html', msg="Password error!")

        # Checks Passed. Remember which user has logged in
        session['user_id'] = rows['id']
        username = session['username'] = rows['username']
        password = rows['hash']
        user = User(id=session['user_id'],username=username,hash=hash)
        try:
            login_user(user)
            app.logger.info("Login OK")
        except:
            app.logger.info("Login NOT OK")

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


@app.route('/chammy', methods = ["GET", "POST"])
def show():
    d = {
        'name': 'Chammy',
        'birthday': 'June 25',
        'age': 3,
        'food': 'blueberry',
        'color': 'pink'
    }
    app.logger.info (type(d))
    return d


@app.route('/jsonv/<v>', methods = ["GET", "POST"])
def showv(v):
    msg = "This is the message: " + v
    message_dict = {'message': msg}
    return jsonify(message_dict)


@app.route("/success", methods=["GET", "POST"])
def success(action, kit_data):
    return render_template("success.html", action=action, kit_data=kit_data)    
