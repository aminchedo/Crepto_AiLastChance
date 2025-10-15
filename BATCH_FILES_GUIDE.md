# 🚀 Batch Files Guide - Crepto_Ai

## 📋 Available Batch Files

### Main Launchers

#### 1. `start-app.bat` ⭐ **RECOMMENDED**
**One-click launcher for the complete Crepto_Ai application**

**Features:**
- ✅ Checks all dependencies
- ✅ Kills existing processes (prevents port conflicts)
- ✅ Starts backend server (Port 5000)
- ✅ Waits for backend to be ready
- ✅ Starts frontend server (Port 5173)
- ✅ Opens browser automatically
- ✅ Color-coded output
- ✅ Health checks

**Usage:**
```bash
# Just double-click or run:
start-app.bat
```

**What it does:**
1. Verifies Node.js and npm are installed
2. Cleans up any existing Node.js processes
3. Starts backend on port 5000
4. Waits until backend responds
5. Starts frontend on port 5173
6. Opens http://localhost:5173 in your browser

---

#### 2. `process-manager.bat` 🔧
**Interactive menu for managing servers**

**Features:**
- 🚀 Start both servers
- 🛑 Stop all servers
- 🔄 Restart backend only
- 🔄 Restart frontend only
- 🔄 Restart both servers
- 👀 View running processes
- 🏥 Health check
- 📊 View server logs
- 🔧 Install dependencies

**Usage:**
```bash
# Double-click or run:
process-manager.bat
```

**Menu Options:**
```
1. Start Both Servers
2. Stop All Servers
3. Restart Backend Only
4. Restart Frontend Only
5. Restart Both Servers
6. View Running Processes
7. Health Check
8. View Server Logs
9. Install Dependencies
0. Exit
```

---

#### 3. `check-dependencies.bat` ✅
**Comprehensive dependency and environment checker**

**Features:**
- Checks Node.js installation
- Checks npm installation
- Checks Git installation (optional)
- Verifies project dependencies
- Checks port availability (5000, 5173)
- Displays system information
- Shows memory status

**Usage:**
```bash
check-dependencies.bat
```

**Sample Output:**
```
✅ Node.js: v18.16.0
✅ npm: v9.5.1
✅ Git: git version 2.40.0
✅ Root node_modules: FOUND
✅ Backend node_modules: FOUND
✅ Port 5000 (Backend): AVAILABLE
✅ Port 5173 (Frontend): AVAILABLE

ALL CHECKS PASSED
```

---

#### 4. `start-production.bat` 🏭
**Production build and deployment launcher**

**Features:**
- Cleans previous builds
- Installs/verifies dependencies
- Builds frontend for production
- Optimizes bundle size
- Starts production server
- Sets NODE_ENV=production

**Usage:**
```bash
start-production.bat
```

**Process:**
1. Removes old dist/build folders
2. Checks dependencies (installs if missing)
3. Runs `npm run build`
4. Starts production server on port 3000
5. Opens browser to production URL

---

### Individual Launchers

#### 5. `start-backend-only.bat` ⚙️
**Starts only the backend server**

**Port:** 5000  
**URL:** http://localhost:5000

**Usage:**
```bash
start-backend-only.bat
```

**Use Cases:**
- Testing backend API independently
- Working on backend without frontend
- Running backend while frontend is on different machine

---

#### 6. `start-frontend-only.bat` 🎨
**Starts only the frontend server**

**Port:** 5173  
**URL:** http://localhost:5173

**Usage:**
```bash
start-frontend-only.bat
```

**Use Cases:**
- Working on frontend UI/UX
- Backend already running separately
- Testing frontend in isolation

⚠️ **Note:** Frontend expects backend on port 5000

---

## 📁 Templates Directory

Located in `templates/` - Sample batch files for other tech stacks:

### `start-vue-python.bat`
Template for Vue.js + Python FastAPI

**Ports:**
- Backend (FastAPI): 8000
- Frontend (Vue.js): 8080
- API Docs: http://localhost:8000/docs

### `start-angular-dotnet.bat`
Template for Angular + .NET Core

**Ports:**
- Backend (.NET): 7000
- Frontend (Angular): 4200
- Swagger UI: http://localhost:7000/swagger

### `start-nextjs.bat`
Template for Next.js Full Stack

**Port:** 3000 (Frontend + API routes)

---

## 🎯 Quick Start Guide

### First Time Setup
```bash
# 1. Check dependencies
check-dependencies.bat

# 2. If all checks pass, start the app
start-app.bat
```

### Daily Development Workflow
```bash
# Option 1: One-click start
start-app.bat

# Option 2: Use process manager
process-manager.bat
→ Choose option 1 (Start Both Servers)
```

### Troubleshooting
```bash
# 1. Run dependency checker
check-dependencies.bat

# 2. If issues found, use process manager
process-manager.bat
→ Choose option 2 (Stop All Servers)
→ Choose option 9 (Install Dependencies)
→ Choose option 1 (Start Both Servers)
```

---

## ⚙️ Configuration

### Ports (can be changed in batch files)

**Crepto_Ai Default Ports:**
- Backend: `5000`
- Frontend: `5173` (Vite default)
- Production: `3000`

**To change ports:**
Edit the batch file and modify these variables:
```batch
set BACKEND_PORT=5000
set FRONTEND_PORT=5173
```

---

## 🔍 Common Issues & Solutions

### Issue 1: "Port already in use"
**Solution:**
```bash
# Use process manager to stop all servers
process-manager.bat
→ Option 2 (Stop All Servers)

# Or manually kill processes
taskkill /f /im node.exe
```

### Issue 2: "Node.js not found"
**Solution:**
1. Install Node.js from https://nodejs.org/
2. Restart terminal/command prompt
3. Run `check-dependencies.bat` to verify

### Issue 3: "Dependencies missing"
**Solution:**
```bash
# Use process manager
process-manager.bat
→ Option 9 (Install Dependencies)

# Or manually
npm install
cd backend && npm install
```

### Issue 4: "Backend not responding"
**Solution:**
```bash
# Check backend logs in the backend server window
# Or restart backend only
process-manager.bat
→ Option 3 (Restart Backend Only)
```

### Issue 5: "Frontend won't load"
**Solution:**
```bash
# Restart frontend only
process-manager.bat
→ Option 4 (Restart Frontend Only)

# Clear browser cache
# Check console for errors (F12)
```

---

## 💡 Pro Tips

### 1. **Keep Process Manager Open**
Open `process-manager.bat` in a separate window for quick access to controls

### 2. **Check Health Before Starting**
```bash
check-dependencies.bat  # Verify everything is ready
start-app.bat          # Then start the app
```

### 3. **Use Individual Launchers for Development**
If working on just frontend or backend:
```bash
start-backend-only.bat  # In one window
start-frontend-only.bat # In another window
```

### 4. **Production Testing**
Before deploying:
```bash
start-production.bat  # Test production build locally
```

### 5. **Auto-Start on Windows Startup**
Create a shortcut to `start-app.bat` in:
```
C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

---

## 📊 Batch File Comparison

| Feature | start-app | process-manager | check-deps | production |
|---------|-----------|-----------------|------------|------------|
| Start Servers | ✅ | ✅ | ❌ | ✅ |
| Stop Servers | ❌ | ✅ | ❌ | ❌ |
| Restart | ❌ | ✅ | ❌ | ❌ |
| Health Check | ✅ | ✅ | ✅ | ✅ |
| Dependency Check | ✅ | ✅ | ✅ | ✅ |
| Production Build | ❌ | ❌ | ❌ | ✅ |
| Interactive Menu | ❌ | ✅ | ❌ | ❌ |
| Auto Browser Open | ✅ | ❌ | ❌ | ✅ |

---

## 🎨 Color Codes

Batch files use color-coded output:
- **Green (0A)** - Success, all systems go
- **Blue (0B)** - Backend server
- **Yellow (0E)** - Frontend server, warnings
- **Red (0C)** - Errors
- **Magenta (0D)** - Production, special features

---

## 🔒 Security Notes

### Development Mode
- Servers run on localhost only
- No external access by default
- CORS enabled for local development

### Production Mode
- Always review security settings
- Configure firewalls appropriately
- Use HTTPS in production
- Set proper CORS origins

---

## 📝 Customization

### Adding Custom Commands
Edit `process-manager.bat` and add new menu options:

```batch
echo   10. 🔧 Your Custom Command
...
if "%choice%"=="10" goto YOUR_CUSTOM_LABEL

:YOUR_CUSTOM_LABEL
echo Running your custom command...
:: Your code here
goto MENU
```

### Creating New Templates
Copy any template from `templates/` and modify:
1. Update port numbers
2. Change server start commands
3. Modify technology-specific checks

---

## 🆘 Getting Help

### In-App Help
- All batch files show usage instructions
- Process manager has built-in help
- Dependency checker provides fix suggestions

### Documentation
- See `UNIVERSAL_API_GUIDE.md` for API information
- See `START_TESTING_HERE.md` for testing
- See `IMPLEMENTATION_COMPLETE.md` for overview

### Quick Commands
```bash
# Show all running processes
process-manager.bat → Option 6

# Health check
process-manager.bat → Option 7

# View dependencies
check-dependencies.bat
```

---

## ✅ Checklist

**Before First Run:**
- [ ] Node.js installed
- [ ] npm available
- [ ] Dependencies installed (`npm install`)
- [ ] Ports 5000 and 5173 available
- [ ] Git installed (optional)

**Daily Use:**
- [ ] Run `check-dependencies.bat` (first time)
- [ ] Run `start-app.bat`
- [ ] Open browser to http://localhost:5173
- [ ] Test with `await qt()` in console

**Before Production:**
- [ ] Test with `start-production.bat`
- [ ] Verify build completes
- [ ] Test on production port
- [ ] Check all features work

---

## 🎉 Summary

**For Quick Start:**
```bash
start-app.bat  # That's it!
```

**For Management:**
```bash
process-manager.bat  # Interactive controls
```

**For Troubleshooting:**
```bash
check-dependencies.bat  # Diagnose issues
```

**For Production:**
```bash
start-production.bat  # Build & deploy
```

---

**Last Updated:** 2025-10-15  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
