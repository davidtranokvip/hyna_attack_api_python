from flask import Flask
from app.routes.routes import init_routes
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_routes(app)
    return app
