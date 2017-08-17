from flask import Flask

app = Flask(__name__)

from app import endpoints

app.config.from_object('config')
