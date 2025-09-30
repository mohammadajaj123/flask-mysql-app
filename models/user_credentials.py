from extensions import db

class UserCredential(db.Model):
    __tablename__ = 'user_credentials'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    telegram_chat_id = db.Column(db.String(50), nullable=True) 
    
    user = db.relationship('User', backref=db.backref('credential', uselist=False))