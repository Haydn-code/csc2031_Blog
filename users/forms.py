from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
import re


def character_check(form, field):
    excluded_chars = "<&%"

    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed.")


def validate_data(form, data_field):
    p = re.compile(r"(?=.*\d)(?=.*[a-z])^.{8,15}$")

    if not p.match(data_field.data):
        raise ValidationError("Must contain 1 digit(0-9) and one lower case word character(a-z) and be between 8-15")


class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Email(), character_check])
    password = PasswordField(validators=[DataRequired(), character_check, validate_data])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password',
                                                                        message='Both password fields must be equal!')])
    submit = SubmitField()


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    pin = StringField(validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField()
