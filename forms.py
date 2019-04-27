from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired

class bookmarkform(FlaskForm):
    link = StringField(label='link', validators=[DataRequired()])
    #description = StringField(label='description', widget=TextArea())
    author = StringField(label='author', validators=[DataRequired()])
