from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, EmailField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
    email = EmailField(label="Enter your email", validators=[DataRequired()])
    password = PasswordField(label="Enter your password", validators=[DataRequired()])


class Registration(FlaskForm):
    name = StringField(label="Enter your full name", validators=[DataRequired()])
    email = EmailField(label="Enter your email", validators=[DataRequired()])
    password = PasswordField(label="Enter your password", validators=[DataRequired()])
    c_password = PasswordField(label="Confirm your password", validators=[DataRequired()])


class PostBlog(FlaskForm):
    title = StringField(label="Enter the Blog title", validators=[DataRequired()])
    subtitle = StringField(label="Enter the sub-title", validators=[DataRequired()])
    # author = StringField(label="name")
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField("Submit")
