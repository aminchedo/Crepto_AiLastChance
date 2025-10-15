# Bolt AI Crypto - Backend API

FastAPI backend for the AI-powered cryptocurrency trading dashboard.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)

### 3. Initialize Database

```bash
# Create database tables
alembic upgrade head
```

### 4. Run Development Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── api/                  # API endpoints
│   ├── auth.py          # Authentication endpoints
│   ├── market.py        # Market data endpoints
│   └── deps.py          # Dependencies (auth, etc.)
├── db/                   # Database configuration
│   ├── database.py      # SQLAlchemy setup
│   └── redis_client.py  # Redis client
├── models/               # Database models
│   ├── user.py
│   ├── portfolio.py
│   ├── alert.py
│   └── ...
├── schemas/              # Pydantic schemas
│   ├── auth.py
│   └── market.py
├── services/             # Business logic
│   ├── auth_service.py
│   └── market_service.py
├── config.py             # Configuration
├── main.py               # FastAPI app
└── requirements.txt      # Dependencies
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/me` - Update user profile
- `POST /api/auth/change-password` - Change password

### Market Data
- `GET /api/market/prices` - Get current prices
- `GET /api/market/candlestick/{symbol}` - Get candlestick data
- `GET /api/market/indicators/{symbol}` - Get technical indicators

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Testing

```bash
pytest
```

## Production Deployment

See `../docs/DEPLOYMENT.md` for production deployment instructions.

