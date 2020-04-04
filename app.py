from flask import Flask, redirect, url_for, redirect, request, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "very secret"
app.permanent_session_lifetime = timedelta(days=15)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

''' Users Database Model '''
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))
    content = db.relationship('todos', backref='owner')

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

''' Todos Database Model '''
class todos(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    content = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, content, owner_id):
        self.content = content
        self.owner_id = owner_id

''' Main Sites '''
@app.route("/")
@app.route("/home")
def home():
    if "usname" in session and "passwd" in session:
        user = users.query.filter_by(username=session["usname"]).first()
        td = todos.query.filter_by(owner_id=user._id).all()

        return render_template('index.html', td=td)
    
    else:
        return redirect(url_for('login'))

@app.route("/remove/<cID>")
def remove(cID):
    if "usname" in session and "passwd" in session:
        user = users.query.filter_by(username=session["usname"]).first()
        toRemove = todos.query.filter_by(_id = cID, owner=user).first()
        db.session.delete(toRemove)
        db.session.commit()

        return redirect(url_for('home'))

    else:
        return redirect(url_for('login'))

@app.route("/add", methods = ["POST"])
def add():
    if "usname" in session and "passwd" in session:
        content = request.form["toAdd"]
        user = users.query.filter_by(username=session["usname"]).first()
        toAdd = todos(content, user._id)
        db.session.add(toAdd)
        db.session.commit()
        
        return redirect(url_for('home'))

    else:
        return redirect(url_for('login'))

''' Login/Register '''
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if "usname" in session and "passwd" in session:
            flash("Already loged in!")
            return redirect(url_for("home"))

        else:
            return render_template("login.html")
    
    if request.method == "POST":
        usname = request.form["usname"]
        passwd = request.form["passwd"]

        print(usname, passwd)
        
        try:
            found_user = users.query.filter_by(username=usname).first()
            print(found_user.username)
            print()
            if found_user.username == usname and found_user.password == passwd:
                session["usname"] = usname
                session["passwd"] = passwd

                return redirect(url_for("home"))
            
            else:
                flash("Wrong Username/Password!")
                return render_template("login.html")
        
        except:
            flash("User not found!")
            return render_template("login.html")
        
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        if "usname" in session and "passwd" in session:
            flash("Already loged in!")
            return redirect(url_for("home"))

        else:
            return render_template("register.html")
    
    if request.method == "POST":
        usname = request.form["usname"]
        email = request.form["email"]
        passwd = request.form["passwd"]
        
        
        found_user = users.query.filter_by(username=usname).first()
        if found_user:
            if found_user.username == usname or found_user.email == email:
                flash("Email/Username Already taken!")
                return render_template("register.html")

        else:

            user = users(usname, passwd, email)
            db.session.add(user)
            db.session.commit()

            flash("Account Created!")
            return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host='192.168.0.120')