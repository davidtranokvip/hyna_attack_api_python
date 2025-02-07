from flask import Flask
from app.routes.routes import init_routes
from app.config import Config
from app.extensions import socketio

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    socketio.init_app(app)
    init_routes(app)
    
    return app
