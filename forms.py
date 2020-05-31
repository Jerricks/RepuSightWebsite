from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, validators, TextAreaField, DateField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired("Input Required")])
    password = PasswordField('Password', validators=[DataRequired()])


class SignupForm(FlaskForm):

    name = StringField('name', [validators.InputRequired('Insert Name !!')])
    email = StringField('email', [validators.DataRequired(), validators.Email()])
    designation = StringField('designation', [validators.DataRequired()])
    mobile = StringField('mobile', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired()])
    propName = StringField('propName', [validators.DataRequired()])
    propAdder = StringField('propAdder', [validators.DataRequired()])
    propLocatCountry = SelectField('propLocatCountry', [validators.DataRequired()])
    propLocatState = SelectField('propLocatState', [validators.DataRequired()])
    propLocatCity = SelectField('propLocatCity', [validators.DataRequired()])
    propLocat = SelectField('propLocat', [validators.DataRequired()])
    username = StringField('username', [validators.DataRequired()])
    propType = SelectField('propType', [validators.DataRequired()], choices = [('None', '--Select--'), ('Hotel', 'Hotel'), ('Restaurant', 'Restaurant'), ('Cafe', 'Cafe')])


class ForgetPasswordForm(FlaskForm):

    username = StringField('username', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired()])
    confirmPassword = PasswordField('confirmPassword', [validators.DataRequired()])