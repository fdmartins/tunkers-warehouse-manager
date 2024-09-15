
from flask import Flask, request, jsonify, render_template
from core import db, app
from core.models import User, Mission
from functools import wraps
import logging
from flask import Flask, redirect, url_for


logger = logging.getLogger(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')