from flask import Flask
from config import Config
from models import db
from routes import bp
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)
app.register_blueprint(bp)

@app.before_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
