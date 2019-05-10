from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired

class bookmarkform(FlaskForm):
    link = StringField(label='link', validators=[DataRequired()])
    #description = StringField(label='description', widget=TextArea())
    author = StringField(label='author', validators=[DataRequired()])

class loginform(FlaskForm):
	passphrase = PasswordField(label='passphrase', validators=[DataRequired()])

class signupform(FlaskForm):
	existing_passphrase = PasswordField(label='existing_passphrase', validators=[DataRequired()])
	new_passphrase = PasswordField(label='new_passphrase', validators=[DataRequired()])
