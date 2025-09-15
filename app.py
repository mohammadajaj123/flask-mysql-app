from flask import Flask, jsonify
import datetime
from extensions import db, jwt   

def create_app():
    app = Flask(__name__)

    import sys
    sys.stdout.flush()
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:0000@localhost:3306/flaskdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'change_this_secret'
    app.config['JWT_SECRET_KEY'] = 'change_this_jwt_secret'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)

    db.init_app(app)   
    jwt.init_app(app)

    from routers.auth import bp as auth_bp
    from routers.users import bp as users_bp
    from routers.transactions import bp as transactions_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(transactions_bp, url_prefix="/transactions")

    @app.route("/")
    def home():
        return jsonify({"message": "Welcome! Flask + MySQL + SQLAlchemy are running"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)