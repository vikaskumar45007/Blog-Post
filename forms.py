from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,EmailField,PasswordField,TextAreaField
from wtforms.validators import DataRequired, URL,Email
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
    
class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Mail Address",validators=[DataRequired()])
    passwd = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# TODO: Create a LoginForm to login existing users
    
class LoginForm(FlaskForm):
    email = EmailField("Email",validators=[DataRequired()])
    passwd = PasswordField("PAssword", validators=[DataRequired()])
    submit = SubmitField("Submit")


# TODO: Create a CommentForm so users can leave comments below posts
    
class CommentForm(FlaskForm):
    comment = TextAreaField("Add a comment",validators=[DataRequired()])
    submit = SubmitField("Submit")
