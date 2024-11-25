from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    body = TextAreaField(validators=[DataRequired()])
    submit = SubmitField()