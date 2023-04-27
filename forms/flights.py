from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class FlightForm(FlaskForm):
    city1 = StringField('Город отправления', validators=[DataRequired()])
    city2 = StringField('Город прибытия', validators=[DataRequired()])
    date = StringField('Дата', default='12.12.23')
    time = StringField('Время', default='12:12')
    plane = StringField('Самолет', default='B737')
    submit = SubmitField('Применить')
