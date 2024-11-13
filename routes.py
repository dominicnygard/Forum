from app import app
from flask import render_template, request, redirect
import posts, users

@app.route("/")
def index():
    post_list = posts.get_posts()
    return render_template("index.html", count=len(post_list), messages = post_list)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        return redirect("/login")
        
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
        if users.register(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Rekisteröinti ei onnistunut")
        
@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/new", methods=["GET", "POST"])
def send():
    if request.method == "GET":
        return render_template("new.html")
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        if posts.send(title, content):
            return redirect("/")
        else:
            return render_template("error.html", message="Viestin lähetys ei onnistunut")
    
@app.route("/post/<int:id>/comment", methods=["GET", "POST"])
def comment(id):
    if request.method == "GET":
        return render_template("comment.html", id=id)
    if request.method == "POST":
        content = request.form["content"]
        if posts.comment(content, id):
            return redirect(f"/post/{id}")
        else:
            return render_template("error.html", message="Ei onnisutnut")

@app.route("/post/<int:id>")
def post(id):
    post = posts.get_post(id)
    comments = posts.get_comments(id)
    return render_template("post.html", post_id=id, post=post, comments=comments)

@app.route("/chat/<int:id>", methods=["GET", "POST"])
def chat(id):
    if request.method == "GET":
        messages = users.chat(id)
        return render_template("chat.html", id=id, messages=messages)
    if request.method == "POST":
        content = request.form["content"]
        if users.send_chat(id, content):
            return redirect(f"/chat/{id}")
        else:
            return render_template("error.html", message="Ei toimi")