from flask import Flask, render_template, redirect, url_for, request, flash, abort
from random import randint
from sqlalchemy import String, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from datetime import datetime
from secrets import token_hex
from flask_login import LoginManager, current_user, login_user, login_required, logout_user, UserMixin
from forms import LoginForm, SignUpForm, ContactForm, PostForm, CommentForm
from smtplib import SMTP
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
# from flask_gravatar import Gravatar
import os


# APP CONFIG BELOW
app = Flask(__name__)
app.config['SECRET_KEY'] = token_hex(30)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///blogster.db')
current_date = datetime.now()

bootstrap = Bootstrap5()
bootstrap.init_app(app)
ckeditor = CKEditor()
ckeditor.init_app(app)
# gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, use_ssl=False, base_url=None)

# LOGIN STUFF BELOW
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# DATABASE STUFF BELOW
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Post(db.Model):
    __tablename__ = 'post'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String[250], unique=True, nullable=False)
    date: Mapped[str] = mapped_column(String[100], nullable=False)
    edit_date: Mapped[str] = mapped_column(String[100], nullable=True)
    subtitle: Mapped[str] = mapped_column(String[250], nullable=False)
    img_url: Mapped[str] = mapped_column(String[250], nullable=False)
    content: Mapped[str] = mapped_column(Text[1050], nullable=False)
    # Relation with user - One user many posts
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='posts')
    # Relation with Comments - One Post many comments
    comments: Mapped[list['Comments']] = relationship(back_populates='post')

    def __repr__(self):
        return f"{self.title} by {self.author}"


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String[250], unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String[250], nullable=False)
    last_name: Mapped[str] = mapped_column(String[250], nullable=False)
    password: Mapped[str] = mapped_column(String[250], nullable=False)
    posts: Mapped[list['Post']] = relationship(back_populates='user')
    comments_posted: Mapped[list['Comments']] = relationship(back_populates='user')

    def __repr__(self):
        return f"{self.name} - {self.email}"

class Comments(db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_text:Mapped[str] = mapped_column(String[1000], nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('post.id'))
    post: Mapped['Post'] = relationship(back_populates='comments')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='comments_posted')



with app.app_context():
    db.create_all()


# ROUTES BELOW

def admin_only(fun):
    wraps(fun)

    def decorated(*args, **kwargs):
        if current_user.id not in [1, 2, 3] or not current_user.is_authenticated:
            return abort(403)
        return fun(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    posts = db.session.execute(db.Select(Post)).scalars().all()
    return render_template('index.html', year=datetime.now().year, posts=posts)

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        email = form.email.data
        phone = form.phone.data
        message = form.message.data
        name = form.name.data
        message_to_send = f"Subject:Contact Request received\n\nYour name: {name}\nYour Phone: {phone}\nMessage: {message}"
        with SMTP('smtp.gmail.com') as connection:
            connection.starttls()
            connection.login(user=os.environ.get("SMTP_USER"), password=os.environ.get("SMTP_PASSWORD"))
            connection.sendmail(from_addr=os.environ.get("SMTP_USER"), to_addrs=email, msg=message_to_send)
        return render_template('contact.html', year=current_date.year, form=form, msg_sent=True)
    return render_template('contact.html', year=datetime.now().year, form=form)

@app.route('/about')
def about():
    return render_template('about.html', year=datetime.now().year)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_exists = db.session.execute(db.Select(User).where(User.email == form.email.data)).scalar()
        if not user_exists:
            flash("Email not registered. Please check your email or register first")
            return redirect(url_for('login'))
        else:
            if not check_password_hash(password=form.password.data, pwhash=user_exists.password):
                flash("Incorrect Password! Please try again.")
                return redirect(url_for('login'))
            else:
                login_user(user_exists)
                return redirect(url_for('index'))
    return render_template('login.html', year=datetime.now().year, form=form)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        email_exists = db.session.execute(db.Select(User).where(User.email == form.email.data)).scalar()
        if email_exists:
            flash('Email Already Exists. Please login instead!')
            return redirect(url_for('signup'))
        else:
            if form.password1.data != form.password2.data:
                flash("Passwords don't match. Please try again!")
            else:
                password_hash = generate_password_hash(password=form.password1.data, method='pbkdf2:sha256', salt_length=10)
                new_user = User(
                    email=form.email.data,
                    password=password_hash,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data
                )
                db.session.add(new_user)
                db.session.commit()

                user = db.session.execute(db.Select(User).where(User.email == form.email.data)).scalar()
                login_user(user)
                return redirect(url_for('index'))
    return render_template('signup.html', year=datetime.now().year, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@admin_only
@app.route('/create-post', methods=['POST', 'GET'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=datetime.now().strftime('%b %d, %Y'),
            content=form.content.data,
            img_url=form.img_url.data,
            user_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('make_post.html', year=datetime.now().year, form=form)

@admin_only
@app.route('/update-post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def update(post_id):
    selected_post = db.session.execute(db.Select(Post).where(Post.id == post_id)).scalar()
    if selected_post:
        form = PostForm(
            title=selected_post.title,
            subtitle=selected_post.subtitle,
            img_url=selected_post.img_url,
            content=selected_post.content
        )
        if form.validate_on_submit():
            selected_post.title = form.title.data
            selected_post.subtitle = form.subtitle.data
            selected_post.img_url = form.img_url.data
            selected_post.content = form.content.data
            selected_post.edit_date = datetime.now().strftime("%b %d, %Y")
            db.session.commit()
            print(current_date.strftime("%b %d, %Y"))
            return redirect(url_for('post', post_id=selected_post.id))
    else:
        return redirect(url_for('index'))
    return render_template('make_post.html', year=datetime.now().year, form=form)

@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
def post(post_id):
    selected_post = db.session.execute(db.Select(Post).where(Post.id == post_id)).scalar()
    if not selected_post:
        return redirect(url_for('index'))
    form = CommentForm()
    if form.validate_on_submit():
        print(form.comment.data)
        new_comment = Comments(
            comment_text=form.comment.data,
            post_id=post_id,
            user_id=current_user.id
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post', post_id=selected_post.id))
    return render_template('post.html', year=datetime.now().year, post=selected_post, form=form)

@admin_only
@app.route('/delete/<int:post_id>')
@login_required
def delete(post_id):
    post_to_delete = db.session.execute(db.Select(Post).where(Post.id == post_id)).scalar()
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False, port=5080, host='0.0.0.0')