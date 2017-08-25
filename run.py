"""This file starts the Flask web service on port 5000"""
from app import create_app

config_name = "development"
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
