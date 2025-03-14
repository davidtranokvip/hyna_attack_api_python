# from app import create_app
# from app.extensions import socketio
# from dotenv import load_dotenv

# load_dotenv()
# app = create_app()

# if __name__ == "__main__":
#     socketio.run(app, host='0.0.0.0', port=5001, debug=True)

from app import create_app
from dotenv import load_dotenv

load_dotenv()
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
