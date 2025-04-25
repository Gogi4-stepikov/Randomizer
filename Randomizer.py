from flask import Flask, render_template, redirect, url_for, request, session, flash, make_response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import math
import random
from io import BytesIO
import base64
import pygame
import sys

pygame.init()
pygame.font.init()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
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

wheel_options = ["Приз 1", "Приз 2", "Приз 3", "Приз 4"]
wheel_angle = 0
is_spinning = False
spin_speed = 0
result = None

def generate_wheel_image():
    try:
        if not pygame.get_init():
            pygame.init()
            pygame.font.init()

        width, height = 500, 500
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((255, 255, 255, 0))
        
        center = (width // 2, height // 2)
        radius = 200
        
        global wheel_options, wheel_angle
        if not isinstance(wheel_options, list) or not wheel_options:
            wheel_options = ["Приз 1", "Приз 2", "Приз 3"]
        if not isinstance(wheel_angle, (int, float)):
            wheel_angle = 0
        colors = [
            (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            for _ in range(len(wheel_options))
        ]
        sector_angle = 360 / len(wheel_options)
        
        for i, (option, color) in enumerate(zip(wheel_options, colors)):
            start_angle = math.radians(i * sector_angle + wheel_angle - 90)
            end_angle = math.radians((i + 1) * sector_angle + wheel_angle - 90)
            
            points = [center]
            points.extend([
                (center[0] + radius * math.cos(a), center[1] + radius * math.sin(a))
                for a in (start_angle, end_angle)
            ])
            pygame.draw.polygon(surface, color, points)
            
            font = pygame.font.SysFont('Arial', 20)
            text = font.render(option, True, (0, 0, 0))
            text_angle = math.radians(i * sector_angle + sector_angle/2 + wheel_angle - 90)
            text_pos = (
                center[0] + radius * 0.7 * math.cos(text_angle) - text.get_width()/2,
                center[1] + radius * 0.7 * math.sin(text_angle) - text.get_height()/2
            )
            surface.blit(text, text_pos)
        
        pygame.draw.circle(surface, (200, 200, 200), center, 20)
        
        buffer = BytesIO()
        pygame.image.save(surface, buffer, "PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Ошибка генерации колеса: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template('Randomizer_Web.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'icon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/fortune_wheel', methods=['GET', 'POST'])
def fortune_wheel():
    global wheel_options, wheel_angle, is_spinning, spin_speed, result
    
    if 'email' not in session:
        flash('Требуется авторизация', 'error')
        return redirect(url_for('authorization'))
    
    if request.method == 'POST':
        if 'update' in request.form:
            new_options = request.form.get('options', '')
            wheel_options = [opt.strip() for opt in new_options.split('\n') if opt.strip()]
            if not wheel_options:
                wheel_options = ["Приз 1", "Приз 2", "Приз 3"]
            wheel_angle = 0
            is_spinning = False
            spin_speed = 0
            result = None
        
        elif 'spin' in request.form and not is_spinning:
            is_spinning = True
            spin_speed = random.uniform(5, 10)
            result = None
    
    if is_spinning:
        wheel_angle = (wheel_angle + spin_speed) % 360
        spin_speed *= 0.985
        
        if spin_speed < 0.1:
            is_spinning = False
            spin_speed = 0
            sector = int((360 - wheel_angle % 360) / (360 / len(wheel_options)))
            result = wheel_options[sector % len(wheel_options)]
    
    wheel_image = generate_wheel_image()
    
    if not wheel_image:
        flash('Ошибка генерации колеса. Проверьте настройки.', 'error')
    
    response = make_response(render_template(
        'fortune_wheel.html',
        wheel_image=wheel_image,
        options='\n'.join(wheel_options),
        result=result,
        is_spinning=is_spinning
    ))
    
    if is_spinning:
        response.headers['Refresh'] = '0.05'
    
    return response

@app.route('/dice')
def dice():
    if 'email' not in session:
        flash('Пожалуйста, войдите для доступа к этой странице')
        return redirect(url_for('authorization'))
    return render_template('dice.html')

@app.route('/monetka')
def monetka():
    if 'email' not in session:
        flash('Пожалуйста, войдите для доступа к этой странице')
        return redirect(url_for('authorization'))
    return render_template('monetka.html')

@app.route('/generator')
def generator():
    if 'email' not in session:
        flash('Пожалуйста, войдите для доступа к этой странице')
        return redirect(url_for('authorization'))
    return render_template('generator.html')

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
