# Crepto AI Development Environment Setup Script
# This script sets up both frontend and backend with proper Python version

Write-Host "🚀 Setting up Crepto AI Development Environment..." -ForegroundColor Green

# Check if Python 3.11 is available
Write-Host "`n📋 Checking Python installation..." -ForegroundColor Yellow
$python311 = Get-Command python3.11 -ErrorAction SilentlyContinue
$python311Alt = Get-Command py -ErrorAction SilentlyContinue

if ($python311Alt) {
    Write-Host "✅ Found Python launcher" -ForegroundColor Green
    $pythonCmd = "py -3.11"
}
elseif ($python311) {
    Write-Host "✅ Found Python 3.11" -ForegroundColor Green
    $pythonCmd = "python3.11"
}
else {
    Write-Host "❌ Python 3.11 not found. Please install Python 3.11 from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "   Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "`n🔧 Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "⚠️  Virtual environment already exists. Removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

& $pythonCmd -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "`n🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Upgrade pip and install build tools
Write-Host "`n📦 Upgrading pip and installing build tools..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

# Install backend dependencies
Write-Host "`n🐍 Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
python -m pip install fastapi uvicorn python-multipart python-jose passlib sqlalchemy alembic aiosqlite redis pydantic-settings

# Create .env file if it doesn't exist
Write-Host "`n⚙️  Setting up environment variables..." -ForegroundColor Yellow
Set-Location ..
if (-not (Test-Path ".env")) {
    $envContent = @"
DATABASE_URL=sqlite:///./crypto_ai.db
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"@
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Created .env file with default values" -ForegroundColor Green
}

# Install frontend dependencies
Write-Host "`n📱 Installing frontend dependencies..." -ForegroundColor Yellow
npm install

# Test backend
Write-Host "`n🧪 Testing backend startup..." -ForegroundColor Yellow
Set-Location backend
python -c "import sys; print('Python version:', sys.version)"
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
Set-Location ..

Write-Host "`n✅ Setup complete! You can now run:" -ForegroundColor Green
Write-Host "   npx tsx scripts/run-all.ts" -ForegroundColor Cyan
Write-Host "   or" -ForegroundColor Gray
Write-Host "   .\run-dev.bat" -ForegroundColor Cyan

Write-Host "`n📝 Notes:" -ForegroundColor Yellow
Write-Host "   - Backend will run on http://localhost:8000" -ForegroundColor Gray
Write-Host "   - Frontend will run on http://localhost:3000" -ForegroundColor Gray
Write-Host "   - Make sure to activate the virtual environment before running Python commands" -ForegroundColor Gray
Write-Host "   - To activate: .venv\Scripts\Activate.ps1" -ForegroundColor Gray
