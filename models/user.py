from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.Enum('admin', 'user', name='user_roles'),
                     nullable=False, server_default='user')

    credentials = db.relationship('UserCredential', backref='user', uselist=False, cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', backref='user', cascade="all, delete-orphan")

class UserCredential(db.Model):
    __tablename__ = 'user_credentials'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
