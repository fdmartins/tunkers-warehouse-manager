from flask import  render_template
from core import db, app
from flask import Blueprint

def register_template_routes():
    @app.route('/')
    def index():
        return render_template('index.html')