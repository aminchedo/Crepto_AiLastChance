# Bolt AI Crypto - AI-Powered Trading Dashboard

A production-ready, full-stack cryptocurrency trading dashboard with AI-powered predictions, real-time market data, and comprehensive monitoring.

## 🚀 Features

### Core Functionality
- ✅ **User Authentication** - JWT-based auth with refresh tokens
- ✅ **Real-Time Market Data** - Live prices from CoinGecko & Binance
- ✅ **AI Predictions** - LSTM neural network for price predictions
- ✅ **Technical Analysis** - RSI, MACD, Bollinger Bands, SMA/EMA
- ✅ **Portfolio Management** - Track positions and P&L
- ✅ **Interactive Charts** - Candlestick charts with indicators
- ✅ **News Feed** - Latest crypto news with sentiment analysis

### Infrastructure
- ✅ **FastAPI Backend** - High-performance Python API
- ✅ **React Frontend** - Modern TypeScript UI
- ✅ **PostgreSQL Database** - Persistent data storage
- ✅ **Redis Cache** - High-speed caching layer
- ✅ **Docker Deployment** - Containerized architecture
- ✅ **Nginx Reverse Proxy** - SSL termination & load balancing
- ✅ **Prometheus & Grafana** - Comprehensive monitoring

### Operational Excellence
- ✅ **Health Checks** - Readiness, liveness, and startup probes
- ✅ **Automated Backups** - Database and Redis backups
- ✅ **Rollback Scripts** - Quick recovery procedures
- ✅ **Structured Logging** - JSON-formatted logs
- ✅ **Rate Limiting** - API protection
- ✅ **Security Hardening** - Input validation, HTTPS, secrets management

## 📋 Prerequisites

- **Docker** 24.0+
- **Docker Compose** 2.20+
- **Node.js** 20+ (for local development)
- **Python** 3.11+ (for local development)
- **Git**

## 🏃 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/bolt-ai-crypto.git
cd bolt-ai-crypto
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.production .env

# Generate secret key
openssl rand -hex 32

# Edit .env and add your configuration
nano .env
```

**Required Variables:**
```env
SECRET_KEY=<generated-secret-key>
POSTGRES_PASSWORD=<strong-password>
GRAFANA_PASSWORD=<admin-password>
```

### 3. Deploy
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Deploy application
./scripts/deploy.sh production
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

## 📁 Project Structure

```
bolt-ai-crypto/
├── backend/                    # FastAPI backend
│   ├── api/                   # API endpoints
│   │   ├── auth.py           # Authentication
│   │   ├── market.py         # Market data
│   │   └── predictions.py    # AI predictions
│   ├── db/                    # Database configuration
│   │   ├── database.py       # SQLAlchemy setup
│   │   └── redis_client.py   # Redis client
│   ├── models/                # Database models
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   ├── alert.py
│   │   └── model_metrics.py
│   ├── ml/                    # Machine learning
│   │   ├── model.py          # LSTM model
│   │   └── trainer.py        # Training logic
│   ├── services/              # Business logic
│   │   ├── auth_service.py
│   │   └── market_service.py
│   ├── monitoring/            # Monitoring & health
│   │   ├── metrics.py
│   │   └── health.py
│   ├── schemas/               # Pydantic schemas
│   ├── alembic/               # Database migrations
│   ├── config.py              # Configuration
│   ├── main.py                # FastAPI app
│   └── requirements.txt       # Python dependencies
│
├── src/                       # React frontend
│   ├── components/            # React components
│   ├── contexts/              # React contexts
│   │   └── AuthContext.tsx   # Authentication context
│   ├── pages/                 # Page components
│   │   ├── Login.tsx
│   │   └── Register.tsx
│   ├── services/              # API services
│   ├── types/                 # TypeScript types
│   ├── App.tsx                # Main app component
│   └── main.tsx               # Entry point
│
├── nginx/                     # Nginx configuration
│   ├── nginx.conf            # Main config
│   ├── frontend.conf         # Frontend config
│   └── ssl/                  # SSL certificates
│
├── monitoring/                # Monitoring configuration
│   ├── prometheus.yml        # Prometheus config
│   └── grafana/              # Grafana dashboards
│
├── scripts/                   # Deployment scripts
│   ├── deploy.sh             # Deployment script
│   ├── backup.sh             # Backup script
│   └── rollback.sh           # Rollback script
│
├── docs/                      # Documentation
│   ├── DEPLOYMENT.md         # Deployment guide
│   ├── API.md                # API documentation
│   └── OPERATIONS.md         # Operations runbook
│
├── docker-compose.yml         # Docker Compose config
├── Dockerfile.backend         # Backend Dockerfile
├── Dockerfile.frontend        # Frontend Dockerfile
└── README.md                  # This file
```

## 🔧 Development

### Local Development Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Run development server
python main.py
```

#### Frontend
```bash
npm install
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test
```

## 🚢 Deployment

### Production Deployment to VPS

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete deployment guide.

**Quick Deploy:**
```bash
./scripts/deploy.sh production
```

### SSL Configuration
```bash
# Install Certbot
sudo apt install certbot -y

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

### Automated Backups
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/bolt-ai-crypto/scripts/backup.sh
```

## 📊 Monitoring

### Grafana Dashboards
Access Grafana at `http://localhost:3001` (default: admin/admin)

**Key Metrics:**
- API request rate and latency
- Database connections and query performance
- Cache hit/miss ratio
- Model prediction accuracy
- Active users and WebSocket connections

### Prometheus Metrics
Access Prometheus at `http://localhost:9090`

**Available Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `predictions_total` - Total predictions made
- `db_connections_active` - Active database connections
- `cache_hits_total` / `cache_misses_total` - Cache performance

## 🔐 Security

### Security Features
- JWT authentication with refresh tokens
- Password hashing with bcrypt
- Rate limiting (100 req/min per user)
- Input validation with Pydantic
- SQL injection prevention
- XSS protection
- HTTPS enforcement
- Secrets management via environment variables

### Security Checklist
- [ ] Change all default passwords
- [ ] Configure SSL certificates
- [ ] Enable firewall (ports 22, 80, 443 only)
- [ ] Setup automated backups
- [ ] Configure monitoring alerts
- [ ] Review access logs regularly
- [ ] Update dependencies monthly

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Complete VPS deployment instructions
- **[API Documentation](docs/API.md)** - API endpoints and examples
- **[Operations Runbook](docs/OPERATIONS.md)** - Troubleshooting and maintenance
- **[Backend README](backend/README.md)** - Backend-specific documentation

## 🛠️ Technology Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- Lucide React (icons)
- Axios (HTTP client)

### Backend
- FastAPI (Python web framework)
- SQLAlchemy 2.0 (ORM, async)
- Alembic (database migrations)
- TensorFlow/Keras (AI/ML)
- CCXT (exchange integration)
- Redis (caching)
- Prometheus Client (metrics)

### Infrastructure
- PostgreSQL 15 (database)
- Redis 7 (cache)
- Nginx (reverse proxy)
- Docker & Docker Compose
- Prometheus (monitoring)
- Grafana (visualization)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for educational and demonstration purposes only. It is **not financial advice**. Cryptocurrency trading involves significant risk. Always do your own research before making investment decisions.

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Open an issue on GitHub
- **Logs**: `docker-compose logs -f [service]`
- **Health Check**: `curl http://localhost:8000/health`

## 🗺️ Roadmap

### Completed ✅
- [x] User authentication system
- [x] Real-time market data integration
- [x] AI prediction model (LSTM)
- [x] Technical indicators
- [x] Portfolio management
- [x] Docker deployment
- [x] Monitoring & health checks
- [x] Comprehensive documentation

### Planned 🚧
- [ ] Advanced signal generation with backtesting
- [ ] Real-time alert system (Telegram, Email)
- [ ] WebSocket for real-time updates
- [ ] Admin dashboard
- [ ] Rate limiting middleware
- [ ] Multi-exchange support
- [ ] Paper trading mode
- [ ] Mobile app (React Native)
- [ ] Social features (share signals)

## 📊 Status

**Current Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: October 2025

---

**Built with ❤️ using React, FastAPI, and TensorFlow**

For questions or support, please open an issue on GitHub.

