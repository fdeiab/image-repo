"""
author: Fattima Deiab

This file contains 2 classes: registerForm and loginForm.
These 2 classes are used to allow users to create an account
or login to an existing one on the Flask web application.
"""
from flask_wtf import FlaskForm
from imagerepo.database import Users
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError

class registerForm(FlaskForm):
    # requires a user to enter a valid username, email, and password to sign up successfully
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=25), Regexp(r'^[\w@+-]+$')])
    user_email = StringField('Email', validators=[DataRequired(), Email()])
    user_pass = PasswordField('Password', validators=[DataRequired()])
    user_passConf = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('user_pass', message="Passwords must match")])
    submit = SubmitField('Sign Up')

    # check to see if an account with that username already exists
    # raises a validation error if true
    def validate_username(self, username):
        user = Users.query.filter_by(username = username.data).first()
        # a user with that username exists, raise error
        if user:
            raise ValidationError("This username is already taken. Please choose another.")

    # check to see if an account with that email already exists 
    # raises a validation error if true
    def validate_user_email(self, user_email):
        user = Users.query.filter_by(userEmail = user_email.data).first()
        # a user with that email exists, raise error
        if user:
            raise ValidationError("This email is already registered to an account.")

class loginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    user_pass = PasswordField('Password', validators=[DataRequired()])
    rememberUser = BooleanField('Remember Me')
    submit = SubmitField('Login')