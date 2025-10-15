# API Documentation - Bolt AI Crypto

Complete API reference for the Bolt AI Crypto backend.

## Base URL

```
Production: https://yourdomain.com/api
Development: http://localhost:8000/api
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle
- **Access Token**: Expires in 30 minutes
- **Refresh Token**: Expires in 7 days

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "Password123!",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-10-14T12:00:00Z"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### Refresh Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### Update Profile
```http
PUT /api/auth/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Smith",
  "telegram_enabled": true,
  "email_enabled": false
}
```

#### Change Password
```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!"
}
```

---

### Market Data

#### Get Market Prices
```http
GET /api/market/prices?symbols=BTC,ETH,BNB
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "bitcoin",
    "symbol": "BTC",
    "name": "Bitcoin",
    "price": 43250.75,
    "change_24h": 1250.30,
    "change_percent_24h": 2.98,
    "volume_24h": 28500000000,
    "market_cap": 850000000000,
    "high_24h": 43800.50,
    "low_24h": 41950.25,
    "timestamp": 1697280000000
  }
]
```

#### Get Candlestick Data
```http
GET /api/market/candlestick/BTC?interval=1h&limit=100
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `interval`: 1m, 5m, 15m, 1h, 4h, 1d
- `limit`: 1-1000 (default: 100)

**Response:**
```json
[
  {
    "time": 1697280000000,
    "open": 43000.00,
    "high": 43500.00,
    "low": 42800.00,
    "close": 43250.75,
    "volume": 1250000
  }
]
```

#### Get Technical Indicators
```http
GET /api/market/indicators/BTC?interval=1h
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "rsi": 65.5,
  "macd": {
    "macd": 125.5,
    "signal": 110.2,
    "histogram": 15.3
  },
  "sma_20": 42800.00,
  "sma_50": 41500.00,
  "ema_12": 43100.00,
  "ema_26": 42500.00,
  "bb": {
    "upper": 44000.00,
    "middle": 43000.00,
    "lower": 42000.00
  }
}
```

---

### AI Predictions

#### Get Prediction
```http
GET /api/predictions/BTC
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "symbol": "BTC",
  "bullish_probability": 0.65,
  "bearish_probability": 0.20,
  "neutral_probability": 0.15,
  "confidence": 0.65,
  "prediction": "BULL",
  "risk_score": 0.35,
  "model_version": "1.0.0"
}
```

#### Start Training (Admin Only)
```http
POST /api/predictions/train
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "epochs": 50,
  "symbols": ["BTC", "ETH", "BNB"]
}
```

#### Stop Training (Admin Only)
```http
POST /api/predictions/train/stop
Authorization: Bearer <admin_access_token>
```

#### Get Training Status
```http
GET /api/predictions/train/status
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "is_training": true,
  "current_epoch": 25,
  "max_epochs": 50
}
```

---

### Health & Monitoring

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-14T12:00:00Z",
  "checks": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

#### Readiness Check
```http
GET /health/ready
```

#### Liveness Check
```http
GET /health/live
```

#### Metrics (Prometheus)
```http
GET /metrics
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Too Many Requests
- `500` - Internal Server Error

### Validation Error Example
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Rate Limiting

- **Authentication endpoints**: 10 requests/minute
- **General API endpoints**: 100 requests/minute
- **Rate limit headers**:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

---

## WebSocket (Future Implementation)

### Connection
```javascript
const ws = new WebSocket('wss://yourdomain.com/ws');
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'access_token'
  }));
};
```

### Subscribe to Channels
```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['market_data', 'predictions', 'alerts']
}));
```

---

## SDK Examples

### Python
```python
import requests

BASE_URL = "https://yourdomain.com/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "user@example.com",
    "password": "Password123!"
})
tokens = response.json()
access_token = tokens["access_token"]

# Get market data
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/market/prices", headers=headers)
market_data = response.json()
```

### JavaScript
```javascript
const BASE_URL = "https://yourdomain.com/api";

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'Password123!'
  })
});
const { access_token } = await loginResponse.json();

// Get market data
const marketResponse = await fetch(`${BASE_URL}/market/prices`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const marketData = await marketResponse.json();
```

---

## Interactive Documentation

Visit the interactive API documentation:
- **Swagger UI**: https://yourdomain.com/api/docs
- **ReDoc**: https://yourdomain.com/api/redoc

