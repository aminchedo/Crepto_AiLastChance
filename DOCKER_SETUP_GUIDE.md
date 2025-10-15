# 🐳 Docker Setup Guide

## Quick Start

```bash
cd /mnt/c/project/Crepto_Ai
docker-compose build
docker-compose up -d
docker-compose ps
```

## Access URLs
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Common Commands

### Build
```bash
docker-compose build
docker-compose build --no-cache
```

### Run
```bash
docker-compose up -d
docker-compose logs -f
```

### Stop
```bash
docker-compose stop
docker-compose down
```

## Troubleshooting

```bash
# View logs
docker-compose logs backend

# Restart service
docker-compose restart backend

# Clean up
docker system prune -a
```