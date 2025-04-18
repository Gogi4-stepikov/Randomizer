from flask import Flask, send_from_directory, render_template
import os

app = Flask(__name__)

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
    return render_template('fortune_wheel.html')

@app.route('/dice')
def dice():
    return render_template('dice.html')

@app.route('/generator')
def generator():
    return render_template('generator.html')

@app.route('/monetka')
def monetka():
    return render_template('monetka.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')


if __name__ == '__main__':
    app.run(port=8000, debug=True)
