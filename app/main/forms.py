from flask_wtf import FlaskForm
from flask import request, current_app
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=1000)])
    my_avatar = HiddenField('imagebase64')
    noavatar = BooleanField('Delete avatar')
    submit = SubmitField('Submit')
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=6, max=1000, message="Post should be between 6 and 1000 characters.")])
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