import os
import time
from flask import Flask, jsonify
import datetime
from extensions import db, jwt
from services.salary_service import salary_service
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Database configuration with Docker support
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Fallback for Docker Compose
        database_url = (
            "mysql+pymysql://flaskuser:flask_app_password_456@mysql:3306/flaskdb"
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret-key")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Wait for database to be ready (Docker-specific)
    with app.app_context():
        max_retries = 5
        for i in range(max_retries):
            try:
                db.engine.connect()
                print(" Database connection successful!")
                break
            except Exception as e:
                if i == max_retries - 1:
                    print(f" Failed to connect to database: {e}")
                    raise
                print(f"⚠️  Database not ready, retrying... ({i+1}/{max_retries})")
                time.sleep(5)

    # Register blueprints and start services
    from routers.telegram_test import bp as telegram_test_bp
    from routers.auth import bp as auth_bp
    from routers.users import bp as users_bp
    from routers.transactions import bp as transactions_bp

    app.register_blueprint(telegram_test_bp, url_prefix="/telegram")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(transactions_bp, url_prefix="/transactions")

    # Start salary service
    salary_service.start()

    @app.route("/")
    def home():
        return jsonify(
            {
                "message": "Welcome! Flask + MySQL + Docker are running",
                "status": "healthy",
            }
        )

    @app.route("/health")
    def health():
        try:
            db.session.execute("SELECT 1")
            db_status = "healthy"
        except Exception:
            db_status = "unhealthy"

        return jsonify(
            {
                "status": "running",
                "database": db_status,
                "timestamp": datetime.datetime.utcnow().isoformat(),
            }
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
