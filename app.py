from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime


img_counter = 1

app = Flask(__name__)
app.config["SECRET_KEY"] = "591b124ad04cd0a527c2b1b7bc186bc9"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///regressors_database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# User model for our database
class User(db.Model, UserMixin):
    """Users table in our database"""

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)

    # Creating a one to many relationship with the posts table.
    posts = db.relationship("Post", backref="author", lazy=True)

    def __repr__(self):
        return f"User(Name: {self.first_name} {self.last_name}, Username: {self.username}, Email: {self.email}, " \
               f"Image file: {self.image_file})"


# Post model for our database
class Post(db.Model):
    """Post table in our database"""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_image = db.Column(db.String(20), nullable=False, default="default.jpg")
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    likes = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Post(Title: {self.title}, Date posted: {self.date_posted})"


# Registration form
class RegistrationForm(FlaskForm):

    first_name = StringField(
        label="First Name",
        render_kw={"placeholder": "Enter first name"},
        validators=[DataRequired(), Length(min=2, max=30)]
    )
    last_name = StringField(
        label="Last Name",
        render_kw={"placeholder": "Enter last name"},
        validators=[DataRequired(), Length(min=2, max=30)]
    )
    user_name = StringField(
        label="Username",
        render_kw={"placeholder": "Enter username"},
        validators=[DataRequired(), Length(min=2, max=30)]
    )
    email = StringField(
        label="Email",
        render_kw={"placeholder": "Enter email"},
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Enter password"},
        validators=[DataRequired(), Length(min=5)]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        render_kw={"placeholder": "Confirm password"},
        validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField(label="Sign Up")

    def validate_user_name(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is already taken. Please choose a different one.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is already taken. Please choose a different one.")


# Login form
class LoginForm(FlaskForm):

    email = StringField(
        label="Email",
        render_kw={"placeholder": "Enter your email"},
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Enter your password"},
        validators=[DataRequired(), Length(min=5)]
    )
    remember_me = BooleanField(label="Remember Me")
    submit = SubmitField(label="Login")


# Add post form
class AddPostForm(FlaskForm):

    title = StringField(
        label="Title",
        render_kw={"placeholder": "Enter the title"},
        validators=[DataRequired(), Length(min=2, max=60)]
    )
    content = TextAreaField(
        label="Content",
        render_kw={"placeholder": "Enter the content"},
        validators=[DataRequired(), Length(min=2, max=2000)]
    )
    submit = SubmitField(label="Add Post")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    posts = Post.query.all()
    users = User.query.all()
    return render_template("index.html", posts=posts, users=users)


@app.get("/signup")
@app.post("/signup")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            first_name=str(form.first_name.data).capitalize(),
            last_name=str(form.last_name.data).capitalize(),
            username=str(form.user_name.data).lower(),
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.user_name.data} successfully!", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", form=form)


@app.get("/login")
@app.post("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back {user.username}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Login unsuccessful. Please check your email and password.", "error")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/profile/<user_id>")
def profile(user_id):
    user = User.query.get(user_id)
    return render_template("profile.html", user=user)


@app.route("/account")
@login_required
def account():
    return render_template("account.html")


@app.get("/add")
@app.post("/add")
@login_required
def add():
    form = AddPostForm()
    if form.validate_on_submit():
        global img_counter
        img_counter += 1
        print(img_counter + 3)
        image_number = ((img_counter + 3) % 3) + 1
        print(image_number)
        post = Post(
            title=form.title.data,
            content=form.content.data,
            post_image=image_number,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash("Post added successfully!", "success")
        return redirect(url_for("home"))
    return render_template("add_post.html", form=form)


if __name__ == "__main__":
    app.run()
