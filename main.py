from flask import Flask, render_template, request, redirect, flash, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from form import LoginForm, Registration, PostBlog, CommentForm
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from flask_gravatar import Gravatar

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any secret string'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blogs.db"
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


class Blog(db.Model, UserMixin):
    __tablename__ = 'blog'
    id = Column(Integer, primary_key=True)
    title = Column(String(250))
    subtitle = Column(String(250))
    date = Column(String(20))
    body = Column(String(250))
    blogs = relationship('Comment', cascade='all, delete', backref='blog', lazy=True)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50))
    password = Column(String(50))
    comments = relationship('Comment', cascade='all, delete', backref='user', lazy=True)


class Comment(db.Model, UserMixin):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True)
    text = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    blog_id = Column(Integer, ForeignKey('blog.id'))


db.create_all()

# gravatar implementation

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)





@app.route("/")
def home():
    blogs = db.session.query(Blog).all()
    print(blogs)
    return render_template("index.html", blogs=blogs)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect('/blog')
            else:
                flash("Invalid credential")
                return redirect('/login')
        else:
            flash("This email is not registered yet. Register first")
            return redirect('/registration')
    return render_template("login.html", form=form, current_user=current_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@app.route("/registration", methods=["POST", "GET"])
def registration():
    form = Registration()
    if request.method == "POST":
        name = form.name.data
        email = form.email.data
        # print(email)
        # email_check = User.query.filter_by(email=email).first()
        if not User.query.filter_by(email=email).first():
            password = form.password.data
            c_password = form.c_password.data
            if password == c_password:
                hashed_password = generate_password_hash(password=password, method="pbkdf2:sha256", salt_length=8)
                new_user = User(name=name, email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)

                return redirect('/blog')
            else:
                flash("please enter password correctly")
                return redirect(url_for('registration'))
        else:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

    return render_template("registration.html", form=form, current_user=current_user)


@app.route("/blog")
def blog():
    all_blog = db.session.query(Blog).all()
    return render_template("blog.html", blogs=all_blog, current_user=current_user, logged_in=True)


@app.route("/blog/<int:id>", methods=["POST", "GET"])
def blog_details(id):
    individual_blog = Blog.query.get(id)
    blogs = db.session.query(Blog).all()
    commentform = CommentForm()
    comments = Comment.query.filter_by(blog_id=id).all()

    print(comments)
    if request.method == "POST":
        print("inside")
        text = commentform.body.data
        comment = Comment(text=text, user=current_user, blog=individual_blog)
        print(text)
        db.session.add(comment)
        db.session.commit()
        return redirect('/blog')
    return render_template("blog_details.html", blog=individual_blog, blogs=blogs, current_user=current_user,
                           form=commentform, comments=comments, gravatar=gravatar)


@app.route("/post", methods=["POST", "GET"])
@admin_only
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
    return render_template("post.html", form=form, current_user=current_user)


@app.route("/update/<int:id>", methods=["POST", "GET"])
@admin_only
def update(id):
    blog_post = Blog.query.get(id)
    print(blog_post)
    blog_record = PostBlog(
        title=blog_post.title,
        subtitle=blog_post.subtitle,
        body=blog_post.body
    )
    if blog_record.validate_on_submit():
        blog_post.title = blog_record.title.data
        blog_post.subtitle = blog_record.subtitle.data
        blog_post.body = blog_record.body.data
        db.session.commit()
        return redirect("/blog")
    return render_template("update.html", form=blog_record, current_user=current_user)


@app.route("/delete/<int:id>")
@admin_only
def delete(id):
    blog_to_delete = Blog.query.get(id)
    db.session.delete(blog_to_delete)
    db.session.commit()
    return redirect("/blog")


# @app.route("/comments", methods=["POST", "GET"])
# @login_required
# def comments():
#     if request.method == "POST":
#         text = request.form.get('body')
#         comment = Comment(text=text, user=current_user)
#         db.session.add(comment)
#         db.session.commit()
#         return redirect('/blog')
#     return render_template("blog_details.html")


if __name__ == '__main__':
    app.run(debug=True)
