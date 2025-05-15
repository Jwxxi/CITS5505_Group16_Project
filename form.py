# forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, EmailField, FloatField,
    SelectField, DateField, FileField, HiddenField
)
from wtforms.validators import DataRequired, Email, Length, Optional


class SignUpForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])


class SignInForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class EditProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("New Password", validators=[Optional()])


class TransactionForm(FlaskForm):
    transaction_id = HiddenField()
    description = StringField("Description", validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired()])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired()])


class ImportCsvForm(FlaskForm):
    file = FileField("CSV File", validators=[DataRequired()])