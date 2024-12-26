from app import create_app
from app.db import db
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv()

app = create_app()
CORS(app)  # Enable CORS for all routes

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI", "mysql+pymysql://username:password@localhost/dbname")
db.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
