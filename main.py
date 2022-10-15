from flask import Flask, render_template, request, redirect
from form import LoginForm, Registration, PostBlog
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, DateTime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any secret string'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blogs.db"
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)
db = SQLAlchemy(app)


class Blog(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(250))
    subtitle = Column(String(250))
    date = Column(String(20))
    body = Column(String(250))


db.create_all()


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
    all_blog = db.session.query(Blog).all()
    return render_template("blog.html", blogs=all_blog)


@app.route("/blog/<int:id>")
def blog_details(id):
    individual_blog = Blog.query.get(id)
    blogs = db.session.query(Blog).all()
    return render_template("blog_details.html", blog=individual_blog, blogs=blogs)


@app.route("/post", methods=["POST", "GET"])
def post():
    form = PostBlog()
    if form.validate_on_submit():
        title = form.title.data
        subtitle = form.subtitle.data
        body = form.body.data
        now = datetime.now()
        blog = Blog(title=title, subtitle=subtitle, date=now.strftime('%b %d, %Y'), body=body)
        db.session.add(blog)
        db.session.commit()
        return redirect('/blog')
    return render_template("post.html", form=form)


@app.route("/update/<int:id>")
def update(id):
    pass


@app.route("/delete/<int:id>")
def delete(id):
    blog_to_delete = Blog.query.get(id)
    db.session.delete(blog_to_delete)
    db.session.commit()
    return redirect("/blog")



if __name__ == '__main__':
    app.run(debug=True)
