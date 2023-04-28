import os
import sqlite3
from flask import Flask, request, render_template, redirect, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from werkzeug.exceptions import abort
from data import db_session
from forms.buyform import BuyForm
from data.loginform import LoginForm
from data.flights import Flights
from data.users import User
from data.bilets import Bilets
from forms.flights import FlightForm
from forms.user import RegisterForm

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    flt = db_sess.query(Flights)
    return render_template("index.html", flt=flt)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")

        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/buy', methods=['GET', 'POST'])
def buy():
    form = BuyForm()
    idd = request.args.get('my_var', None)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        a = db_sess.query(Flights).filter(Flights.id == idd).first()
        b = a.city1
        c = a.city2
        d = a.date
        f = a.time
        bilet = Bilets(
            email=form.email.data,
            city1=b,
            city2=c,
            date=d,
            time=f
        )
        homeDir = os.path.expanduser('~')

        def saveFile():
            f = open(f'{homeDir}/Desktop/Ticket.txt', encoding='utf-8', mode='w')
            f.write(f'Вы купили билет на рейс {b} - {c}. Спасибо, что выбрали MOHSales!\n')
            f.write(f'\n*****\n\n')
            f.write(f'Адрес электронной почты: {form.email.data}\n')
            f.write(f'Номер карты: {form.card_num.data}\n')
            f.write(f'\n*****\n\n')
            f.write(f'Правила этикета на борту:\n')
            f.write(f'- вежливо общаться с другими пассажирами;\n')
            f.write(f'- не вступать в конфликты с окружающими;\n')
            f.write(f'- не провоцировать скандалы и разбирательства;\n')
            f.write(f'- не слушать музыку без наушников;\n')
            f.write(f'- не разговаривать громко с собеседником по телефону;\n')
            f.write(f'- ответственно выполнять все команды бортпроводников.\n')
            f.write(f'\nДругие правила и всю подробную информацию вы узнаете на борту лайнера.\n')
            f.write(f'\n*****\n\n')
            f.write(f'Приятного полета!')
            f.close()

        db_sess.add(bilet)
        db_sess.commit()
        saveFile()
        return redirect('/thanks')
    return render_template('buy.html', title='Покупка билета', form=form)


@app.route('/thanks', methods=['GET', 'POST'])
def thanks():
    return render_template('thanks.html')


@app.route('/bilets', methods=['GET', 'POST'])
def bilets():
    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    cursor = cur.execute('SELECT id,email,city1,city2,date,time FROM bilets')
    items = cursor.fetchall()
    return render_template('bilets.html', items=items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/flt', methods=['GET', 'POST'])
@login_required
def add_flt():
    form = FlightForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        flt = Flights()
        flt.city1 = form.city1.data
        flt.city2 = form.city2.data
        flt.date = form.date.data
        flt.time = form.time.data
        flt.plane = form.plane.data
        flt.user_id = current_user.id
        current_user.flights.append(flt)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('flt.html', title='Добавление новости',
                           form=form)


@app.route('/flt/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_flt(id):
    form = FlightForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        flt = db_sess.query(Flights).filter(Flights.id == id,
                                            Flights.user == current_user
                                            ).first()
        if flt:
            form.city1.data = flt.city1
            form.city2.data = flt.city2
            form.date.data = flt.date
            form.time.data = flt.time
            form.plane.data = flt.plane
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        flt = db_sess.query(Flights).filter(Flights.id == id,
                                            Flights.user == current_user
                                            ).first()
        if flt:
            flt.city1 = form.city1.data
            flt.city2 = form.city2.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('flt.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/flt_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def flt_delete(id):
    db_sess = db_session.create_session()
    flt = db_sess.query(Flights).filter(Flights.id == id).first()
    if flt:
        db_sess.delete(flt)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
