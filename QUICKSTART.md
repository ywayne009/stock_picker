# Quick Start Guide

Get the Stock Picking Tool running in 5 minutes!

## 🚀 Fastest Setup (Recommended)

### 1. Prerequisites Check

Make sure you have installed:
- Python 3.11+ → `python3 --version`
- Node.js 18+ → `node --version`
- Docker → `docker --version`

### 2. One-Command Setup

```bash
./setup.sh
```

This automatically:
- ✅ Starts PostgreSQL and Redis in Docker
- ✅ Creates Python virtual environment
- ✅ Installs all Python dependencies
- ✅ Installs all Node.js dependencies
- ✅ Creates .env file from template

### 3. Configure API Keys

Edit the `.env` file and add your API keys:

```bash
# Required for AI features
OPENAI_API_KEY=sk-your-key-here

# Required for market data (choose one)
POLYGON_API_KEY=your-polygon-key
# OR
ALPACA_API_KEY=your-alpaca-key
ALPACA_SECRET_KEY=your-alpaca-secret
```

### 4. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access the App

Open your browser:
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Backend API:** http://localhost:8000

## 🎯 What's Running?

- **PostgreSQL/TimescaleDB** - Time-series database for market data
- **Redis** - Caching layer for real-time data
- **FastAPI Backend** - REST API with WebSocket support
- **Next.js Frontend** - Interactive dashboard

## 📝 Next Steps

1. **Explore the API** - Visit http://localhost:8000/docs
2. **Create your first strategy** - Use the Strategy Editor at http://localhost:3000/strategies
3. **Run a backtest** - Test your strategy on historical data
4. **Generate AI strategies** - Use natural language to create strategies

## 🛠️ Development Tips

### Activate Virtual Environment

Always activate the virtual environment before running backend commands:

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
```

You'll see `(venv)` in your terminal prompt when activated.

### Hot Reload

Both backend and frontend support hot reload:
- Edit Python files in `backend/app/` - server auto-restarts
- Edit React files in `frontend/src/` - browser auto-refreshes

### View Logs

**Backend:** Check terminal where uvicorn is running

**Docker Services:**
```bash
docker-compose -f docker-compose.services.yml logs -f
```

### Stop Everything

**Backend/Frontend:** Press `Ctrl+C` in each terminal

**Docker Services:**
```bash
docker-compose -f docker-compose.services.yml down
```

## ❓ Common Issues

### "Port already in use"

Another service is using port 5432, 6379, 8000, or 3000:

```bash
# Check what's using the port (example for 8000)
lsof -i :8000

# Kill the process or change ports in docker-compose.services.yml
```

### "Command not found: uvicorn"

Virtual environment not activated:

```bash
cd backend
source venv/bin/activate
```

### "Cannot connect to database"

Services not running:

```bash
docker-compose -f docker-compose.services.yml ps
docker-compose -f docker-compose.services.yml up -d
```

## 🎓 Learn More

- [README.md](./README.md) - Full documentation
- [CLAUDE.md](./CLAUDE.md) - Development guidelines
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) - System architecture

## 💡 Example Workflow

1. Start Docker services (once)
2. Activate venv and start backend
3. Start frontend in another terminal
4. Make changes to code
5. See changes reflected immediately
6. When done, Ctrl+C and `docker-compose down`

Happy trading! 📈
