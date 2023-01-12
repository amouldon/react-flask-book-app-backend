from flask import Flask
from .auth.routes import auth
from .databaseAPI.routes import database_api
from models import db, ma, login_manager
from config import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.register_blueprint(auth)
app.register_blueprint(database_api)

app.config.from_object(Config)
db.init_app(app)
login_manager.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)

