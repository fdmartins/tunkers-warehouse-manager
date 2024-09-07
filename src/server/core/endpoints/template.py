from flask import  render_template
from core import db, app

@app.route('/')
def index():
    return render_template('index.html')