from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from flask_marshmallow import Marshmallow
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
ma = Marshmallow()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String, nullable=False)
    token = db.Column(db.String, unique=True)

    def __init__(self, name, email, password):
        self.id = self.set_id()
        self.name = name
        self.email = email
        self.password = self.set_password(password)
        self.token = self.set_token(30)

    def set_id(self):
        return str(uuid.uuid4())

    def set_token(self, length):
        return secrets.token_hex(length)
    
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash
    
    def __repr__(self):
        return 'User has been added to the database'


class Book(db.Model):
    id = db.Column(db.String, primary_key=True)
    collection_status = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String, nullable=True)
    average_rating = db.Column(db.String, nullable=True)
    user_rating = db.Column(db.String, nullable=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    user_token = db.Column(db.String, db.ForeignKey('user.token'), nullable=False)
    date_holder = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, nullable=True)

    def __init__(self, user_rating, title, author, user_token , image_url, average_rating, collection_status=''):
        self.id = self.set_id()
        self.user_rating = user_rating
        self.average_rating = average_rating
        self.collection_status = collection_status
        self.image_url = image_url
        self.title = title
        self.author = author
        self.user_token = user_token



    def set_id(self):
        return secrets.token_urlsafe()

    def __repr__(self):
        return 'A book has been added to your collection'
    
class BookSchema(ma.Schema):
    class Meta:
        fields = ['id', 'user_rating', 'title', 'author', 'average_rating', 'collection_status', 'image_url', 'date_holder', 'date_completed' ]

book_schema = BookSchema()
books_schema = BookSchema(many=True)