#!/bin/bash

echo "=== Flask MySQL App Docker Setup ==="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cat > .env << EOF
MYSQL_ROOT_PASSWORD=super_secure_root_password_123
MYSQL_PASSWORD=flask_app_password_456
DATABASE_URL=mysql+pymysql://flaskuser:flask_app_password_456@mysql:3306/flaskdb
SECRET_KEY=your_flask_secret_key_change_this_in_production_789
JWT_SECRET_KEY=your_jwt_secret_key_change_this_in_production_012
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
EOF
    echo ".env file created! Please edit it with your actual values."
fi

echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to start..."
sleep 10

echo "Checking services status..."
docker-compose ps

echo "=== Setup Complete! ==="
echo "Flask App: http://localhost:5000"
echo "MySQL: localhost:3306"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
