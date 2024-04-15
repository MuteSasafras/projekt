from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.models import User


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Nazwa użytkownika jest zajęta! Proszę o utworzenie innej.')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Ten adres e-mail znajduje sie już w użyciu! Proszę o użycie innego.')

    username = StringField(label='Nazwa użytkownika:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Adres E-mail:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Utwórz hasło:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Potwierdź hasło:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Utwórz konto')


class LoginForm(FlaskForm):
    username = StringField(label='Nazwa użytkownika:', validators=[DataRequired()])
    password = PasswordField(label='Hasło:', validators=[DataRequired()])
    submit = SubmitField(label='Zaloguj sie')

class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Kup przedmiot')

class SellItemForm(FlaskForm):
    submit = HiddenField()