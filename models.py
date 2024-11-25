from app import db, app
from datetime import datetime
import bcrypt
from cryptography.fernet import Fernet
from flask_login import UserMixin
import pyotp


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    postkey = db.Column(db.BLOB)
    pinkey = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')
    registered_on = db.Column(db.DateTime, nullable=False)
    current_login = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    blogs = db.relationship('Post')

    def __init__(self, username, password, role):
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.postkey = Fernet.generate_key()
        self.pinkey = pyotp.random_base32()
        self.role = role
        self.registered_on = datetime.now()
        self.current_login = None
        self.last_login = None


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.ForeignKey(User.password), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)

    def __init__(self, username, title, body, postkey):
        self.username = username
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        self.created = datetime.now()

    def update_post(self, title, body, postkey):
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        db.session.commit()

    def view_post(self, postkey):
        self.title = decrypt(self.title, postkey)
        self.body = decrypt(self.body, postkey)


def encrypt(data, postkey):
    return Fernet(postkey).encrypt(bytes(data, 'utf-8'))


def decrypt(data, postkey):
    return Fernet(postkey).decrypt(data).decode('utf-8')


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(username='admin@gmail.com', password='computer123', role='admin')
        db.session.add(admin)
        db.session.commit()