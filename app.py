from flask import Flask, render_template, request, redirect, session, send_from_directory
import os, hashlib, random, string

app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = "storage"
if not os.path.exists(BASE_DIR):
    os.mkdir(BASE_DIR)


# ---------- Helpers ----------
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def user_exists(username):
    if not os.path.exists("users.txt"):
        return False
    with open("users.txt") as f:
        for line in f:
            u, _ = line.strip().split(",")
            if u == username:
                return True
    return False

def generate_captcha():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = hash_password(request.form["password"])

        if os.path.exists("users.txt"):
            with open("users.txt") as f:
                for line in f:
                    user, pw = line.strip().split(",")
                    if user == u and pw == p:
                        session["user"] = u
                        return redirect("/dashboard")
        return "Invalid login"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        captcha = request.form["captcha"]
        if captcha != session["captcha"]:
            return "Captcha wrong!"

        username = request.form["username"]
        password = request.form["password"]

        if user_exists(username):
            return "User already exists!"

        with open("users.txt", "a") as f:
            f.write(f"{username},{hash_password(password)}\n")

        os.mkdir(os.path.join(BASE_DIR, username))
        return redirect("/")

    session["captcha"] = generate_captcha()
    return render_template("register.html", captcha=session["captcha"])


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    user = session["user"]
    user_dir = os.path.join(BASE_DIR, user)

    if request.method == "POST":
        file = request.files["file"]
        file.save(os.path.join(user_dir, file.filename))

    files = os.listdir(user_dir)
    return render_template("dashboard.html", files=files)


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(os.path.join(BASE_DIR, session["user"]), filename, as_attachment=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


app.run(debug=True)
