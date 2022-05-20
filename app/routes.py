from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
@app.route('/index/<name>')
def index(name="Hello world"):  # put application's code here
    return render_template('index.html', text=name)

@app.route('/cos')
def cos():
    return 'Eryk Tabiś'
