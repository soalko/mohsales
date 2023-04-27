from flask_wtf import FlaskForm
from sqlalchemy_serializer import SerializerMixin
from wtforms import SubmitField, EmailField, IntegerField, FileField, StringField
from wtforms.validators import DataRequired


class BuyForm(FlaskForm, SerializerMixin):
    email = EmailField('Почта')
    card_num = IntegerField('Номер карты', validators=[DataRequired()])
    srok = StringField('Действует до', validators=[DataRequired()])
    cvc = StringField('CVC код', validators=[DataRequired()])
    submit = SubmitField('Купить')
