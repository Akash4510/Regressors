from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from forms import RegistrationForm, LoginForm
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "591b124ad04cd0a527c2b1b7bc186bc9"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///regressors_database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
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
        return f"User(Username: {self.username}, Email: {self.email}, Image file: {self.image_file})"


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


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/signup")
@app.post("/signup")
def signup():
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
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@email.com" and form.password.data == "admin_password":
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Login unsuccessful", "error")
    return render_template("login.html", form=form)


if __name__ == "__main__":
    app.run()
