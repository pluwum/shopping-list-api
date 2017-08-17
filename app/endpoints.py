from flask import flash
from app import app

@app.route("/", methods=['GET', 'POST'])
def index():
    return "Test"