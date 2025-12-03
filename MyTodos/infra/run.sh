#!/usr/bin/env bash
# infra/run.sh
# Make executable: chmod +x infra/run.sh
set -e

# Ensure .env exists in repo root
if [ ! -f .env ]; then
  echo ".env not found in repo root. Copy infra/.env.template to .env and edit if needed."
  cp infra/.env.prod .env
  echo "A template .env was created. Please edit it and re-run this script."
  exit 1
fi

echo "Building and starting services..."
docker compose -f infra/docker-compose.yml up --build -d

echo
echo "Services started:"
echo "- Frontend: http://localhost (port 80)"
echo "- Backend (optional): http://localhost:${BACKEND_PORT:-3000}"

echo
echo "To view logs: docker compose -f infra/docker-compose.yml logs -f"

echo
echo "To stop services: docker compose -f infra/docker-compose.yml down"