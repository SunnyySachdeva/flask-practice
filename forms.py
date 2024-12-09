from wtforms import StringField, SubmitField, PasswordField, EmailField, URLField
from wtforms.validators import InputRequired, Email, URL, Length
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm

BUTTON_STYLE = {'style': 'margin-top: 10px;'}
FIELD_STYLE = {'style': 'border-top: 0px; border-left: 0px; border-right: 0px; border-radius: 20px;'}

class PostForm(FlaskForm):
    title = StringField(label='Title', validators=[InputRequired()], render_kw=FIELD_STYLE)
    subtitle = StringField(label='Subtitle', validators=[InputRequired()], render_kw=FIELD_STYLE)
    img_url = URLField(label='Image URL', validators=[InputRequired(), URL()], render_kw=FIELD_STYLE)
    content = CKEditorField(label='Post Content', validators=[InputRequired()])
    submit = SubmitField(label='Submit', render_kw=BUTTON_STYLE)

class ContactForm(FlaskForm):
    name = StringField(label='Your Name', validators=[InputRequired()], render_kw=FIELD_STYLE)
    email = StringField(label='Email', validators=[InputRequired(), Email()], render_kw=FIELD_STYLE)
    phone = StringField(label='Contact No.', validators=[InputRequired(), Length(min=10, max=10)], render_kw=FIELD_STYLE)
    message = CKEditorField(label='Your Message', validators=[InputRequired()], render_kw=FIELD_STYLE)
    submit = SubmitField(label='Submit', render_kw=BUTTON_STYLE)

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[InputRequired(), Email()], render_kw=FIELD_STYLE)
    password = PasswordField(label='Password', validators=[InputRequired()], render_kw=FIELD_STYLE)
    submit = SubmitField(label='Login', render_kw=BUTTON_STYLE)


class SignUpForm(FlaskForm):
    first_name = StringField(label='First Name', validators=[InputRequired()], render_kw=FIELD_STYLE)
    last_name = StringField(label='Last Name', validators=[InputRequired()], render_kw=FIELD_STYLE)
    email = EmailField(label='Email', validators=[InputRequired(), Email()], render_kw=FIELD_STYLE)
    password1 = PasswordField(label='Password', validators=[InputRequired()], render_kw=FIELD_STYLE)
    password2 = PasswordField(label='Confirm Password', validators=[InputRequired()], render_kw=FIELD_STYLE)
    submit = SubmitField(label='Sign Up', render_kw=BUTTON_STYLE)


class CommentForm(FlaskForm):
    comment = CKEditorField(label='Post Comment', validators=[InputRequired()], render_kw=FIELD_STYLE)
    submit = SubmitField(label='Post', render_kw=BUTTON_STYLE)