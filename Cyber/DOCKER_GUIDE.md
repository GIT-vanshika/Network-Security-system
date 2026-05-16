# Docker Deployment Guide

## Prerequisites
- Docker installed ([Get Docker](https://www.docker.com/products/docker-desktop))
- Docker Compose installed (comes with Docker Desktop)

## Quick Start

### 1. Build and Run with Docker Compose
```bash
# Navigate to project directory
cd Cyber

# Build and start all services (FastAPI app + MongoDB)
docker-compose up -d

# View logs
docker-compose logs -f app
```

The application will be available at:
- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB Express**: http://localhost:8081

### 2. Running Just the FastAPI App
```bash
# Build the image
docker build -t network-security-app .

# Run the container
docker run -p 8000:8000 \
  -e MONGO_DB_URL=mongodb://your-mongo-host:27017 \
  network-security-app
```

## Docker Compose Services

### app (FastAPI Application)
- **Port**: 8000
- **Environment Variables**:
  - `MONGO_DB_URL`: MongoDB connection string
  - `PYTHONUNBUFFERED=1`: Unbuffered Python output

### mongo (MongoDB Database)
- **Port**: 27017
- **Username**: admin
- **Password**: admin123
- **Volume**: `mongo_data` (persists database)

### mongo-express (MongoDB GUI)
- **Port**: 8081
- **Purpose**: Web interface for viewing MongoDB data
- **Optional**: Can be removed from compose file if not needed

## Volume Mapping
Directories are mounted to persist data:
- `./logs` → `/app/logs`
- `./prediction_output` → `/app/prediction_output`
- `./uploads` → `/app/uploads`
- `./Artifacts` → `/app/Artifacts`

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (removes database data)
docker-compose down -v

# View service logs
docker-compose logs -f [service-name]

# Rebuild images
docker-compose build --no-cache

# Run command in container
docker-compose exec app bash

# Check service status
docker-compose ps
```

## Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```
MONGO_DB_URL=mongodb://admin:admin123@mongo:27017
PYTHONUNBUFFERED=1
```

## Accessing the API

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Training Pipeline in Docker

To run the training pipeline:

```bash
# Option 1: Using docker-compose (interactive)
docker-compose exec app python main.py

# Option 2: Create a separate service in docker-compose.yml
# Add a 'training' service that runs main.py
```

## Production Deployment

For production:
1. Update MongoDB credentials in `.env`
2. Configure proper resource limits in `docker-compose.yml`
3. Use environment-specific configuration
4. Enable SSL/TLS for MongoDB
5. Use persistent volumes on production storage
6. Implement proper logging and monitoring

## Troubleshooting

**Port already in use**:
```bash
# Change port mapping in docker-compose.yml
# ports:
#   - "8001:8000"  # Map to different port
```

**MongoDB connection issues**:
```bash
# Check if mongo service is running
docker-compose ps

# Check mongo service logs
docker-compose logs mongo
```

**Build failures**:
```bash
# Clean build without cache
docker-compose build --no-cache
```

## Notes
- The health check monitors the API availability
- Containers will automatically restart unless stopped
- All dependencies from `requirements.txt` are installed
- The Python package is installed in editable mode (`-e .`)
