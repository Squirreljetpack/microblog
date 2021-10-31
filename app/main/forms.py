from flask_wtf import FlaskForm
from flask import request, current_app
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed
from app.models import User

class PostForm(FlaskForm):
    post = TextAreaField('', validators=[DataRequired(), Length(min=6, max=1000, message="Post should be between 6 and 1000 characters.")])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)