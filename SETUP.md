# Crepto AI Development Setup

This guide will help you set up the development environment for Crepto AI, which includes both a React/TypeScript frontend and a Python FastAPI backend.

## 🚨 Prerequisites

**Important**: This project requires **Python 3.11** (not Python 3.13) due to compatibility issues with pandas/numpy packages.

### Required Software

1. **Python 3.11** - Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ Make sure to check "Add Python to PATH" during installation
   - Verify installation: `python --version` should show 3.11.x

2. **Node.js** - Download from [nodejs.org](https://nodejs.org/)
   - Verify installation: `node --version` and `npm --version`

3. **Git** - Download from [git-scm.com](https://git-scm.com/)

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Setup Script

Run the PowerShell setup script:

```powershell
# Make sure you're in the project directory
cd C:\project\Crepto_Ai

# Run the setup script
.\setup-dev.ps1
```

This script will:
- ✅ Check for Python 3.11
- ✅ Create a virtual environment
- ✅ Install all backend dependencies
- ✅ Install all frontend dependencies
- ✅ Create necessary configuration files
- ✅ Test the setup

### Option 2: Manual Setup

If you prefer to set up manually:

```powershell
# 1. Create virtual environment
py -3.11 -m venv .venv

# 2. Activate virtual environment
.venv\Scripts\Activate.ps1

# 3. Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# 4. Install backend dependencies
cd backend
python -m pip install fastapi uvicorn python-multipart python-jose passlib sqlalchemy alembic aiosqlite redis pydantic-settings

# 5. Install frontend dependencies
cd ..
npm install

# 6. Create environment file
echo "DATABASE_URL=sqlite:///./crypto_ai.db" > .env
echo "SECRET_KEY=dev-secret-key-change-in-production" >> .env
echo "ALGORITHM=HS256" >> .env
echo "ACCESS_TOKEN_EXPIRE_MINUTES=30" >> .env
```

## 🎯 Running the Application

### Start Both Frontend and Backend

```powershell
# Using the automated script
npx tsx scripts/run-all.ts

# Or using the batch file
.\run-dev.bat
```

This will start:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

### Start Individual Services

**Backend only:**
```powershell
.venv\Scripts\Activate.ps1
cd backend
python main.py
```

**Frontend only:**
```powershell
npm run dev -- --port 3000
```

## 🔧 Troubleshooting

### Common Issues

1. **"Python 3.11 not found"**
   - Install Python 3.11 from python.org
   - Make sure "Add Python to PATH" is checked during installation

2. **"Virtual environment not found"**
   - Run `.\setup-dev.ps1` first

3. **"Port already in use"**
   - The script automatically uses port 3000 for frontend to avoid conflicts
   - If backend port 8000 is in use, kill the process: `taskkill /f /im python.exe`

4. **"Module not found" errors**
   - Make sure virtual environment is activated: `.venv\Scripts\Activate.ps1`
   - Reinstall dependencies: `pip install -r requirements.txt`

### Environment Variables

The `.env` file contains:
- `DATABASE_URL`: SQLite database path
- `SECRET_KEY`: JWT secret key (change in production)
- `ALGORITHM`: JWT algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## 📁 Project Structure

```
Crepto_Ai/
├── src/                    # React frontend
├── backend/               # Python FastAPI backend
├── scripts/               # Development scripts
├── .venv/                 # Python virtual environment
├── .env                   # Environment variables
├── setup-dev.ps1          # Setup script
├── run-dev.bat            # Quick start script
└── scripts/run-all.ts     # Development runner
```

## 🎉 Success!

Once setup is complete, you should see:
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ Both services logging to the console
- ✅ No dependency errors

## 📝 Next Steps

1. Open http://localhost:3000 in your browser
2. Check the API docs at http://localhost:8000/docs
3. Start developing! 🚀

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Make sure Python 3.11 is installed and in PATH
3. Verify Node.js and npm are working
4. Try running the setup script again: `.\setup-dev.ps1`
