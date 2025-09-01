from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
import datetime

app = Flask(__name__)

# ===== Database config =====
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:0000@localhost:3306/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ===== JWT config =====
app.config['SECRET_KEY'] = 'change_this_secret'
app.config['JWT_SECRET_KEY'] = 'change_this_jwt_secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# ==============================
# Models
# ==============================
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


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# ==============================
# Helpers
# ==============================
def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"


def can_act_on_user(target_user_id: int) -> bool:
    """Allow if admin OR the token's user_id matches target_user_id"""
    if is_admin():
        return True
    current_user_id = int(get_jwt_identity())
    return current_user_id == int(target_user_id)


# ==============================
# Public route
# ==============================
@app.route('/')
def home():
    return jsonify({"message": "Welcome! Flask + MySQL + SQLAlchemy are running"})


# ==============================
# Auth routes
# ==============================
@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    creds = UserCredential.query.filter_by(username=username).first()
    if not creds or not check_password_hash(creds.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    user = creds.user
    additional_claims = {"role": user.role}
    token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
    })


@app.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })


# ==============================
# Users routes
# ==============================
@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    if not is_admin():
        return jsonify({"error": "Admin privileges required"}), 403

    data = request.json or {}
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400
    if UserCredential.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400

    new_user = User(name=data['name'], email=data['email'], role=data.get('role', 'user'))
    db.session.add(new_user)
    db.session.commit()

    creds = UserCredential(
        user_id=new_user.id,
        username=data['username'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(creds)
    db.session.commit()

    return jsonify({"message": "User created", "id": new_user.id}), 201


@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    if not is_admin():
        return jsonify({"error": "Admin privileges required"}), 403
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users])


@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    if not can_act_on_user(user_id):
        return jsonify({"error": "Not authorized"}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"id": user.id, "name": user.name, "email": user.email, "role": user.role})


@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    if not can_act_on_user(user_id):
        return jsonify({"error": "Not authorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json or {}
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)

    if 'role' in data:
        if not is_admin():
            return jsonify({"error": "Admin privileges required to change role"}), 403
        user.role = data['role']

    db.session.commit()
    return jsonify({"message": "User updated"})


@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    if not is_admin():
        return jsonify({"error": "Admin privileges required"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


# ==============================
# Transactions routes
# ==============================
@app.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    current_user_id = int(get_jwt_identity())
    data = request.json or {}


    target_user_id = data.get('user_id', current_user_id)
    if not can_act_on_user(target_user_id):
        return jsonify({"error": "Not authorized"}), 403

    new_transaction = Transaction(
        amount=data['amount'],
        description=data.get('description', ''),
        user_id=target_user_id
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({"message": "Transaction created", "id": new_transaction.id}), 201


@app.route('/transactions', methods=['GET'])
@jwt_required()
def get_my_transactions():
    current_user_id = int(get_jwt_identity())
    if is_admin():
        txns = Transaction.query.all()
    else:
        txns = Transaction.query.filter_by(user_id=current_user_id).all()
    return jsonify([{"id": t.id, "amount": t.amount, "description": t.description, "user_id": t.user_id} for t in txns])


@app.route('/transactions/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    txn = Transaction.query.get(transaction_id)
    if not txn:
        return jsonify({"error": "Transaction not found"}), 404
    if not can_act_on_user(txn.user_id):
        return jsonify({"error": "Not authorized"}), 403
    return jsonify({"id": txn.id, "amount": txn.amount, "description": txn.description, "user_id": txn.user_id})


@app.route('/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    txn = Transaction.query.get(transaction_id)
    if not txn:
        return jsonify({"error": "Transaction not found"}), 404
    if not can_act_on_user(txn.user_id):
        return jsonify({"error": "Not authorized"}), 403

    data = request.json or {}
    txn.amount = data.get('amount', txn.amount)
    txn.description = data.get('description', txn.description)
    db.session.commit()
    return jsonify({"message": "Transaction updated"})


@app.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    txn = Transaction.query.get(transaction_id)
    if not txn:
        return jsonify({"error": "Transaction not found"}), 404
    if not can_act_on_user(txn.user_id):
        return jsonify({"error": "Not authorized"}), 403
    db.session.delete(txn)
    db.session.commit()
    return jsonify({"message": "Transaction deleted"})





if __name__ == '__main__':
    with app.app_context():
        # 🚨 Development only:
        # Drop all tables and recreate them each run
        db.drop_all()
        db.create_all()

        # Ensure default admin exists
        if not User.query.filter_by(role='admin').first():
            admin_user = User(
                name='Default Admin',
                email='admin@example.com',
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()

            admin_creds = UserCredential(
                user_id=admin_user.id,
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin_creds)
            db.session.commit()

            print("Default admin user created!")
            print("Username: admin")
            print("Password: admin123")

    app.run(debug=True)
