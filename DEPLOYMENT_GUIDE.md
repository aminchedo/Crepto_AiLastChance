# 🚀 Crypto AI - Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Crypto AI application with real API integration in a production environment.

## 📋 Pre-Deployment Checklist

### 1. Security Configuration
- [ ] All API keys stored in environment variables
- [ ] `.env.local` file excluded from git
- [ ] Security headers configured
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Circuit breakers enabled

### 2. Environment Setup
- [ ] Production environment variables configured
- [ ] Feature flags set appropriately
- [ ] Monitoring and logging configured
- [ ] Error tracking enabled (Sentry, etc.)

### 3. Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Load testing completed
- [ ] Security testing completed

## 🔧 Environment Configuration

### Production Environment Variables

Create a `.env.production` file with your production API keys:

```bash
# Production Environment Configuration
VITE_USE_REAL_APIS=true
VITE_ENABLE_API_CACHE=true
VITE_CACHE_TTL=60
VITE_API_RATE_LIMIT=30
VITE_CIRCUIT_BREAKER_THRESHOLD=3
VITE_API_DEBUG_LOGGING=false

# Production API Keys
VITE_CMC_API_KEY_PRIMARY=your_production_cmc_key
VITE_CMC_API_KEY_BACKUP=your_backup_cmc_key
VITE_CRYPTOCOMPARE_KEY=your_production_cryptocompare_key
VITE_ETHERSCAN_KEY=your_production_etherscan_key
VITE_BSCSCAN_KEY=your_production_bscscan_key
VITE_TRONSCAN_KEY=your_production_tronscan_key
VITE_NEWSAPI_KEY=your_production_newsapi_key
VITE_WHALEALERT_KEY=your_production_whalealert_key

# Monitoring
VITE_SENTRY_DSN=your_sentry_dsn
VITE_ANALYTICS_ENDPOINT=your_analytics_endpoint
```

### Staging Environment Variables

Create a `.env.staging` file for staging deployment:

```bash
# Staging Environment Configuration
VITE_USE_REAL_APIS=true
VITE_ENABLE_API_CACHE=true
VITE_CACHE_TTL=30
VITE_API_RATE_LIMIT=60
VITE_CIRCUIT_BREAKER_THRESHOLD=5
VITE_API_DEBUG_LOGGING=true

# Staging API Keys (use test keys if available)
VITE_CMC_API_KEY_PRIMARY=your_staging_cmc_key
VITE_CMC_API_KEY_BACKUP=your_backup_cmc_key
# ... other keys
```

## 🏗️ Build Configuration

### Vite Configuration

Update `vite.config.ts` for production:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false, // Disable sourcemaps in production
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'charts': ['chart.js', 'react-chartjs-2', 'recharts'],
          'crypto': ['crypto-js']
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  }
});
```

### Package.json Scripts

Add production scripts to `package.json`:

```json
{
  "scripts": {
    "build:staging": "vite build --mode staging",
    "build:production": "vite build --mode production",
    "preview:staging": "vite preview --mode staging",
    "preview:production": "vite preview --mode production",
    "test:unit": "vitest run",
    "test:integration": "vitest run --config vitest.integration.config.ts",
    "test:e2e": "playwright test",
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit"
  }
}
```

## 🐳 Docker Deployment

### Dockerfile

Create `Dockerfile.production`:

```dockerfile
# Multi-stage build for production
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build:production

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx/nginx.production.conf /etc/nginx/nginx.conf

# Copy environment variables
COPY .env.production /usr/share/nginx/html/.env

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  crypto-ai:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/nginx.production.conf:/etc/nginx/nginx.conf
    depends_on:
      - crypto-ai
    restart: unless-stopped
```

## ☁️ Cloud Deployment

### AWS Deployment

1. **S3 + CloudFront Setup**:
   ```bash
   # Build the application
   npm run build:production
   
   # Upload to S3
   aws s3 sync dist/ s3://your-bucket-name --delete
   
   # Invalidate CloudFront cache
   aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
   ```

2. **Environment Variables in AWS**:
   - Use AWS Systems Manager Parameter Store
   - Use AWS Secrets Manager for sensitive data
   - Configure in CloudFront or Lambda@Edge

### Vercel Deployment

1. **vercel.json**:
   ```json
   {
     "builds": [
       {
         "src": "package.json",
         "use": "@vercel/static-build",
         "config": {
           "distDir": "dist"
         }
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "/index.html"
       }
     ],
     "env": {
       "VITE_USE_REAL_APIS": "true"
     }
   }
   ```

2. **Deploy**:
   ```bash
   npm install -g vercel
   vercel --prod
   ```

### Netlify Deployment

1. **netlify.toml**:
   ```toml
   [build]
     command = "npm run build:production"
     publish = "dist"
   
   [build.environment]
     VITE_USE_REAL_APIS = "true"
   
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

2. **Deploy**:
   ```bash
   npm install -g netlify-cli
   netlify deploy --prod
   ```

## 🔍 Monitoring & Observability

### Health Checks

Add health check endpoint:

```typescript
// src/utils/healthCheck.ts
export const healthCheck = async () => {
  const health = CryptoDataOrchestrator.getSystemHealth();
  
  return {
    status: health.overall.status,
    timestamp: new Date().toISOString(),
    services: health.overall.healthyServices,
    total: health.overall.totalServices,
    uptime: process.uptime()
  };
};
```

### Logging Configuration

```typescript
// src/utils/logger.ts
import { FEATURE_FLAGS } from '../config/cryptoApiConfig';

export const logger = {
  info: (message: string, data?: any) => {
    if (FEATURE_FLAGS.DEBUG_LOGGING) {
      console.log(`[INFO] ${message}`, data);
    }
  },
  error: (message: string, error?: Error) => {
    console.error(`[ERROR] ${message}`, error);
  },
  warn: (message: string, data?: any) => {
    console.warn(`[WARN] ${message}`, data);
  }
};
```

### Metrics Collection

```typescript
// src/utils/metrics.ts
export const collectMetrics = () => {
  const metrics = CryptoDataOrchestrator.getSystemHealth();
  
  // Send to monitoring service
  if (import.meta.env.VITE_ANALYTICS_ENDPOINT) {
    fetch(import.meta.env.VITE_ANALYTICS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metrics)
    }).catch(console.error);
  }
  
  return metrics;
};
```

## 🚦 Deployment Strategy

### Blue-Green Deployment

1. **Prepare Green Environment**:
   ```bash
   # Build new version
   npm run build:production
   
   # Deploy to green environment
   docker-compose -f docker-compose.green.yml up -d
   ```

2. **Health Check**:
   ```bash
   # Wait for health check to pass
   curl -f http://green-environment/health
   ```

3. **Switch Traffic**:
   ```bash
   # Update load balancer to point to green
   # Monitor for issues
   ```

4. **Cleanup**:
   ```bash
   # Remove blue environment after verification
   docker-compose -f docker-compose.blue.yml down
   ```

### Canary Deployment

1. **Deploy to 10% of traffic**:
   ```bash
   # Configure load balancer for 10% traffic
   # Monitor metrics and errors
   ```

2. **Gradual rollout**:
   ```bash
   # Increase to 25%, 50%, 100%
   # Monitor at each stage
   ```

3. **Rollback if needed**:
   ```bash
   # Revert to previous version
   # Investigate issues
   ```

## 🔒 Security Hardening

### Content Security Policy

Add to `index.html`:

```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.coinmarketcap.com https://api.coingecko.com;
  font-src 'self';
">
```

### Security Headers

Configure in nginx:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline';" always;
```

## 📊 Performance Optimization

### Bundle Analysis

```bash
# Analyze bundle size
npm install -g webpack-bundle-analyzer
npm run build:production
npx webpack-bundle-analyzer dist/assets/*.js
```

### Caching Strategy

1. **Static Assets**: Cache for 1 year
2. **API Responses**: Cache for 30 seconds
3. **HTML**: Cache for 5 minutes

### CDN Configuration

```typescript
// Configure CDN for static assets
const CDN_URL = 'https://cdn.yourdomain.com';

export const getAssetUrl = (path: string) => {
  return `${CDN_URL}/${path}`;
};
```

## 🧪 Testing in Production

### Smoke Tests

```bash
# Run smoke tests after deployment
npm run test:smoke

# Check critical endpoints
curl -f https://your-domain.com/health
curl -f https://your-domain.com/api/prices
```

### Load Testing

```bash
# Install artillery
npm install -g artillery

# Run load test
artillery run load-test.yml
```

## 🔄 Rollback Procedure

### Quick Rollback

```bash
# Revert to previous version
git checkout previous-commit
npm run build:production
docker-compose up -d

# Or use blue-green deployment
docker-compose -f docker-compose.blue.yml up -d
```

### Database Rollback

```bash
# If database changes were made
npm run migrate:rollback
```

## 📈 Post-Deployment Monitoring

### Key Metrics to Monitor

1. **API Performance**:
   - Response times
   - Error rates
   - Rate limit hits
   - Circuit breaker trips

2. **Application Health**:
   - Memory usage
   - CPU usage
   - Cache hit rates
   - Service availability

3. **Business Metrics**:
   - User engagement
   - Feature usage
   - Error frequency

### Alerting Rules

```yaml
# Example alerting rules
alerts:
  - alert: HighErrorRate
    expr: error_rate > 0.05
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"

  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
```

## 🆘 Troubleshooting

### Common Issues

1. **API Rate Limits**:
   - Check rate limiting configuration
   - Verify API key limits
   - Implement request queuing

2. **Circuit Breaker Open**:
   - Check service health
   - Verify API endpoints
   - Review error logs

3. **High Memory Usage**:
   - Check cache configuration
   - Monitor memory leaks
   - Adjust cache TTL

### Debug Commands

```bash
# Check service health
curl -f https://your-domain.com/health

# View logs
docker-compose logs -f crypto-ai

# Check metrics
curl -f https://your-domain.com/metrics
```

## 📚 Additional Resources

- [Security Implementation Guide](./SECURITY_IMPLEMENTATION.md)
- [API Documentation](./docs/API.md)
- [Monitoring Setup](./docs/MONITORING.md)
- [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)

---

**⚠️ IMPORTANT**: Always test deployments in staging environment first. Monitor closely after production deployment and be prepared to rollback if issues arise.
