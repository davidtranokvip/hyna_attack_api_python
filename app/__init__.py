from flask import Flask
from app.routes.routes import init_routes
from app.config import Config
from app.extensions import socketio
import os
from app.db import db
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)  # Enable CORS for all routes
    
    socketio.init_app(app)
    init_routes(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI", "mysql+pymysql://username:password@localhost/dbname")
    db.init_app(app)

    with app.app_context():
        db.create_all()
    
    return app