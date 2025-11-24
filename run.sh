set -e

[ ! -f .env ] && cp .env.example .env


docker-compose up --build -d

echo "http://localhost:8000"