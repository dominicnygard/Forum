from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    sql = text("""SELECT P.title, P.content, U.username, P.sent_at 
            FROM Posts P, Users U 
            WHERE P.user_id=U.id ORDER BY P.id;""")
    result = db.session.execute(sql).fetchall()
    return render_template("index.html", count=len(result), messages = result)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if login(username, password):
            return redirect("/")
        else:
            return redirect("/login")

def login(username, password):
    sql =  text("SELECT id, password FROM users WHERE username = :username")
    user = db.session.execute(sql, {"username": username}).fetchone()
    if not user:
        return False
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["user_id"] = user.id
            return True
        else:
            return False

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            return render_template("error.html", message="Salasanat eroavat")
        if register(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Rekisteröinti ei onnistunut")

def register(username, password):
    hash_value = generate_password_hash(password)
    try:
        sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
        db.session.execute(sql, {"username": username, "password": hash_value})
        db.session.commit()
    except Exception as e:
        print(e)
        return False
    return login(username, password)

@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/send", methods=["POST"])
def send():
    title = request.form["title"]
    content = request.form["content"]
    if send(title, content):
        return redirect("/")
    else:
        return render_template("error.html", message="Viestin lähetys ei onnistunut")

def send(title, content):
    user_id = session.get("user_id",0)
    if user_id == 0:
        return False
    sql = text("INSERT INTO posts (title, content, user_id, sent_at) VALUES (:title, :content, :user_id, NOW())")
    db.session.execute(sql, {"title":title, "content":content, "user_id":user_id})
    db.session.commit()
    return True

@app.route("/post/<int:id>")
def post(id):
    sql = text("""SELECT id FROM posts WHERE id = :id""")
    id = db.session.execute(sql, {"id":id}).fetchone()
    return render_template("post.html", post_id=id[0])