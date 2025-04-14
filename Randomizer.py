from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    with open('Randomizer_Web.html', 'r', encoding='utf-8') as file:
        return file.read()


if __name__ == "__main__":
    app.run(port='8000', host='127.0.0.1', debug=True)
