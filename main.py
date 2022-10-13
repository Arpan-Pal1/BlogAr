from flask import Flask, render_template, request
from form import LoginForm, Registration, PostBlog
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any secret string'

bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST":
        # if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        print(email)
        print(password)
        return f"{email} {password}"
    return render_template("login.html", form=form)


@app.route("/registration", methods=["POST", "GET"])
def registration():
    form = Registration()
    if request.method == "POST":
        name = form.name.data
        email = form.email.data
        password = form.password.data
        c_password = form.c_password.data
        return f"{name} {email} {password} {c_password}"
    return render_template("registration.html", form=form)


@app.route("/blog")
def blog():
    return render_template("blog.html")


@app.route("/blog/<int:id>")
def blog_details(id):
    return render_template("blog.html")


@app.route("/post")
def post():
    form = PostBlog()
    return render_template("post.html", form=form)



if __name__ == '__main__':
    app.run(debug=True)
