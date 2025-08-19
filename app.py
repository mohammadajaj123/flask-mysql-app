from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:0000@localhost:3306/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

@app.route('/')
def home():
    return jsonify({"message": "Welcome! Flask + MySQL + SQLAlchemy are running"})
    
@app.route('/test-db')
def test_db():
    try:
        db.session.execute(db.select(1))
        return jsonify({"message": "Database connection successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        data = request.json
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
            
        new_user = User(
            name=data['name'],
            email=data['email']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created", "id": new_user.id}), 201

    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    })

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    data = request.json
    if 'email' in data and data['email'] != user.email:
        if User.query.filter(User.email == data['email'], User.id != user_id).first():
            return jsonify({"error": "Email already in use"}), 400
    
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    
    db.session.commit()
    return jsonify({"message": "User updated"})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    Transaction.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User and their transactions deleted"})


@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        data = request.json
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        new_transaction = Transaction(
            amount=data['amount'],
            description=data.get('description', ''),
            user_id=data['user_id']
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"message": "Transaction created", "id": new_transaction.id}), 201

    transactions = Transaction.query.all()
    return jsonify([{
        "id": t.id,
        "amount": t.amount,
        "description": t.description,
        "user_id": t.user_id
    } for t in transactions])

@app.route('/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404
    return jsonify({
        "id": transaction.id,
        "amount": transaction.amount,
        "description": transaction.description,
        "user_id": transaction.user_id
    })

@app.route('/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404
        
    data = request.json
    if 'user_id' in data:
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404
    
    transaction.amount = data.get('amount', transaction.amount)
    transaction.description = data.get('description', transaction.description)
    transaction.user_id = data.get('user_id', transaction.user_id)
    
    db.session.commit()
    return jsonify({"message": "Transaction updated"})

@app.route('/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404
        
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({"message": "Transaction deleted"})


@app.route('/users/<int:user_id>/transactions', methods=['GET'])
def get_user_transactions(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": t.id,
        "amount": t.amount,
        "description": t.description
    } for t in transactions])

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)