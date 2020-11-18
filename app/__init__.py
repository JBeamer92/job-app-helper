from flask import Flask
from .blueprints.page import page

def create_app():
    app = Flask(__name__)
    app.register_blueprint(page)
    return app