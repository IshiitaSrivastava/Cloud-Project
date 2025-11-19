# backend/app.py
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from backend.routes import bp
from backend.config import Config
from backend.models import Base
from backend.database import engine

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
app.config.from_object(Config)
jwt = JWTManager(app)
CORS(app)
app.register_blueprint(bp)

# create tables
Base.metadata.create_all(bind=engine)

# serve frontend index
@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

