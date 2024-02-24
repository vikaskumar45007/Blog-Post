from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_avatars import Avatars
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user,login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text,ForeignKey,join
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm,RegistrationForm,LoginForm,CommentForm
from typing import List



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)


avatars = Avatars(app)

# TODO: Configure Flask-Login

login_manager = LoginManager()
login_manager.init_app(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)



# TODO: Create a User table for all your registered users. 

class Users(db.Model,UserMixin):
    __tablename__ = "blog_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True,nullable=False)
    mail: Mapped[str] = mapped_column(String, unique=True,nullable=False)
    password: Mapped[str] = mapped_column(String)
    user : Mapped[List["BlogPost"]] = relationship(back_populates="blog_author")
    comment_user : Mapped[List["BlogComment"]] = relationship(back_populates="comment_user")



# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id : Mapped[int] = mapped_column(ForeignKey("blog_users.id"))
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    blog_author : Mapped["Users"] = relationship(back_populates="user")
    blog : Mapped["BlogComment"] = relationship(back_populates="blog_comment")


class BlogComment(db.Model):
    __tablename__ = 'blog_comments'
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    post_id : Mapped[int] = mapped_column(ForeignKey("blog_posts.id"))
    user_id : Mapped[int] = mapped_column(ForeignKey("blog_users.id"))
    comment : Mapped[str] = mapped_column(String,nullable=False)
    blog_comment: Mapped["BlogPost"] = relationship(back_populates="blog")
    comment_user : Mapped["Users"] = relationship(back_populates="comment_user")




with app.app_context():
    db.create_all()



class noth:
    def __init__(self) -> None:
        pass

@login_manager.user_loader
def load_user(user_id):
    record = db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()
    return(Users(id = int(user_id),name = record.name,mail = record.mail))




def admin_user(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return fun(*args, **kwargs)
    return wrapper_fun



# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods = ["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = Users(name = form.name.data, mail = form.email.data, password = generate_password_hash(password=form.passwd.data,method="scrypt",salt_length=6))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html",form=form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        record = db.session.execute(db.select(Users).where(Users.mail == form.email.data)).scalar()

        if not record:
            flash("Please enter a valid mail address.")
        elif not check_password_hash(record.password , form.passwd.data):
            flash("Please enter a valid password.")

        else:
            login_user(record)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html",form= form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>",methods = ['POST','GET'])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    if form.validate_on_submit() :  
        if current_user.is_authenticated:
            comment = BlogComment(post_id = post_id, comment = form.comment.data,user_id = current_user.id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('show_post',post_id = post_id))
        else:
            return redirect(url_for('login'))
    post_comments = db.session.execute(db.select(BlogComment,Users).join(Users).where(BlogComment.post_id == post_id)).all()
    return render_template("post.html", post=requested_post,form = form, comments = post_comments, avatars = avatars)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@login_required
# @admin_user
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user.name,
            author_id = current_user.id,
            date=date.today().strftime("%M %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user.name
        post.author_id = current_user.id
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@login_required
@admin_user
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    comments_to_delete = db.session.execute(db.select(BlogComment).where(BlogComment.post_id == post_id)).scalars()
    for comment in comments_to_delete:
        db.session.delete(comment)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=False, port=5002)