from flask import Flask
from app.routes.routes import init_routes
from app.config import Config
from app.extensions import socketio
import os
from app.db import db
from flask_cors import CORS
from .services.cache_service import cache
# from app.models import init_models

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['REDIS_HOST'] = 'localhost'
    app.config['REDIS_PORT'] = 6379
    app.config['REDIS_DB'] = 0
    app.config['REDIS_DEFAULT_TTL'] = 86400 
    CORS(app)  # Enable CORS for all routes
    
    cache.init_app(app)
    socketio.init_app(app)
    init_routes(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI", "mysql+pymysql://username:password@localhost/dbname")
    db.init_app(app)

    with app.app_context():
        # init_models()
        db.create_all()
    
    return app