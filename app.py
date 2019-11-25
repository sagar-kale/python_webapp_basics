from flask import Flask, redirect, request, render_template, url_for, Response
from classes.user import User
import uuid

users = []

app = Flask(__name__)

title = "Python Web Page - Web Site"


@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        std_id = request.form.get("id")
        name = request.form.get("name")
        email = request.form.get("email")
        address = request.form.get("addr")
        user = User(std_id, name, address, email)
        users.append(user)
        redirect(url_for("hello_world"))
    print(request)
    return render_template("index.html", title=title, users=users, id=uuid.uuid4())


if __name__ == '__main__':
    app.run(debug=True)
