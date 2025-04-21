from flask import Flask, send_from_directory, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'samiy_sekretniy_kluch'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(20))
    source = db.Column(db.String(100))
    password = db.Column(db.String(200), nullable=False)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'icon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/')
def home():
    return render_template('Randomizer_Web.html')

@app.route('/fortune_wheel')
def fortune_wheel():
    if 'email' not in session:
        flash('Пожалуйста, войдите для доступа к этой странице')
        return redirect(url_for('authorization'))
    return render_template('fortune_wheel.html')

@app.route('/dice')
def dice():
    if 'email' not in session:
        flash('Пожалуйста, войдите для доступа к этой странице')
        return redirect(url_for('authorization'))
    return render_template('dice.html')

@app.route('/generator')
def generator():
    if 'email' not in session:
        flash('Пожалуйста, войдите для доступа к этой странице')
        return redirect(url_for('authorization'))
    return render_template('generator.html')

@app.route('/monetka')
def monetka():
    if 'email' not in session:
        flash('Пожалуйста, войдите для доступа к этой странице')
        return redirect(url_for('authorization'))
    return render_template('monetka.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        surname = request.form.get('surname')
        name = request.form.get('name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        source = request.form.get('profession')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not password or not confirm_password:
            flash('Пароль не может быть пустым')
            return redirect(url_for('registration'))
        if password != confirm_password:
            flash('Пароли не совпадают')
            return redirect(url_for('registration'))
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует')
            return redirect(url_for('registration'))
        try:
            hashed_password = generate_password_hash(password)
            new_user = User(
                surname=surname,
                name=name,
                email=email,
                gender=gender,
                source=source,
                password=hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно! Теперь вы можете войти.')
            return redirect(url_for('authorization'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при регистрации: {str(e)}')
            return redirect(url_for('registration'))
    return render_template('registration.html')

@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['email'] = email
            session['name'] = user.name
            flash(f'Добро пожаловать, {user.name}!')
            return redirect(url_for('home'))
        else:
            flash('Неверный email или пароль')
    return render_template('authorization.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('name', None)
    flash('Вы успешно вышли из системы')
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=8000, debug=True)
