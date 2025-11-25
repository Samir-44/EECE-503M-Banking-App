from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    full_name = StringField('Full name', validators=[DataRequired(), Length(max=128)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    phone = TelField('Phone', validators=[Length(max=32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    full_name = StringField('Full name', validators=[DataRequired(), Length(max=128)])
    phone = TelField('Phone', validators=[Length(max=32)])
    submit = SubmitField('Save')
