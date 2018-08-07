from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SelectField
from wtforms import FloatField
from wtforms import RadioField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from wtforms_alchemy import PhoneNumberField
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Введите почту', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    email = StringField('Введите почту', validators=[DataRequired(), Email()])
    first_name = StringField('Введите имя', validators=[DataRequired()])
    second_name = StringField('Введите фамилию', validators=[DataRequired()])
    phone = PhoneNumberField('Введите номер телефона', validators=[DataRequired()])
    password = PasswordField('Введите пароль для входа', validators=[DataRequired()])
    pass_submit = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Выберите другое имя')

class newBillfold(FlaskForm):
    wallets = SelectField("Выберите валюту", choices=[
        ("Евро", "Евро"), ("Доллары", "Доллары"), ("Рубли", "Рубли")])
    summ = StringField("Сумма для первоначального пополнения", validators=[DataRequired()])
    submit = SubmitField("Создать счет")
    
class upBillfold(FlaskForm):
    bills = SelectField('Счёт для пополнения')
    upSumm = StringField("Сумма для пополнения", validators=[DataRequired()])
    submit = SubmitField("Пополнить счет")

class TransferMoney(FlaskForm):
    bills = SelectField("Выберите счёт, с которого хотите осуществить перевод")
    transBill = StringField("Введите счет, на который будет совершен перевод",
                validators=[DataRequired()])
    transSum = FloatField("Введите сумму для перевода", validators=[DataRequired()])
    message = TextAreaField("Вы можете ввести сообщение для получателя")
    submit = SubmitField("Перевести")

class deleteBillfold(FlaskForm):
    button_delete = SubmitField("Удалить счёт")