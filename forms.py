from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


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
