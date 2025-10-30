# Stock Picking Tool

AI-powered stock picking and backtesting platform for professional traders.

## Features

- Historical and real-time market data integration
- Flexible trading strategy framework
- Comprehensive backtesting engine with realistic simulation
- AI-powered strategy generation using GPT-4
- Advanced optimization algorithms
- Interactive performance dashboards
- Detailed reporting and visualizations

## Tech Stack

**Backend:**
- Python 3.11+ with FastAPI
- PostgreSQL + TimescaleDB
- Redis for caching
- OpenAI API for AI features

**Frontend:**
- Next.js with React
- TypeScript
- TailwindCSS
- TradingView Charts

## Getting Started

### Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Docker** (Optional, for services only) - [Install Docker](https://docs.docker.com/get-docker/)

### Option 1: Automated Setup with Virtual Environment (Recommended)

This setup uses Docker only for databases (PostgreSQL/Redis) while running your code locally in a virtual environment.

```bash
# One-command setup
./setup.sh

# This will:
# 1. Start PostgreSQL and Redis in Docker
# 2. Create Python virtual environment and install dependencies
# 3. Set up frontend with npm
# 4. Create .env file from template

# After setup, start backend:
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload

# In a new terminal, start frontend:
cd frontend
npm run dev
```

**Windows Users:**
```bash
# Run backend setup
cd backend
setup.bat

# Run frontend setup
cd frontend
npm install

# Start services manually
docker-compose -f docker-compose.services.yml up -d
```

### Option 2: Manual Virtual Environment Setup

**Step 1: Start Database Services**
```bash
# Start only PostgreSQL and Redis
docker-compose -f docker-compose.services.yml up -d

# Check services are running
docker ps
```

**Step 2: Setup Backend with Virtual Environment**
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload
```

**Step 3: Setup Frontend**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Option 3: Full Docker Setup

Run everything in Docker containers (backend, frontend, and services).

```bash
# Start all services
docker-compose up -d

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:3000
```

### Access the Application

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
- **PostgreSQL:** localhost:5432 (user: stockpicker, password: devpassword)
- **Redis:** localhost:6379

### Environment Variables

Copy `.env.example` to `.env` and update with your API keys:

```bash
cp .env.example .env
```

Required API keys:
- `OPENAI_API_KEY` - For AI strategy generation
- `POLYGON_API_KEY` or `ALPACA_API_KEY` - For market data

## Project Structure

```
stock_picker/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Configuration
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── utils/    # Utilities
│   └── tests/        # Backend tests
├── frontend/         # Next.js frontend
│   └── src/
│       ├── app/      # Next.js pages
│       ├── components/
│       ├── services/ # API clients
│       └── types/    # TypeScript types
└── docs/            # Documentation

```

## Development Workflow

### Running with Virtual Environment

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Docker Services:**
```bash
# Start services
docker-compose -f docker-compose.services.yml up -d

# View logs
docker-compose -f docker-compose.services.yml logs -f

# Stop services
docker-compose -f docker-compose.services.yml down
```

### Running Tests

```bash
# Backend tests
cd backend
source venv/bin/activate
pytest

# With coverage
pytest --cov=app tests/

# Frontend tests (once configured)
cd frontend
npm test
```

### Database Migrations

```bash
cd backend
source venv/bin/activate

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Common Commands

```bash
# Format Python code
cd backend
black app/ tests/

# Lint Python code
pylint app/

# Lint Frontend
cd frontend
npm run lint

# Build for production
docker-compose build
```

## Documentation

- [CLAUDE.md](./CLAUDE.md) - Development guidance and architecture details
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) - System architecture overview
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## Troubleshooting

### Virtual Environment Issues

**"Command not found: uvicorn"**
- Make sure virtual environment is activated: `source venv/bin/activate`

**"Module not found"**
- Reinstall dependencies: `pip install -r requirements.txt`

### Docker Issues

**"Port already in use"**
- Check if services are already running: `docker ps`
- Stop conflicting services or change ports in docker-compose.services.yml

**"Cannot connect to database"**
- Ensure services are running: `docker-compose -f docker-compose.services.yml ps`
- Check DATABASE_URL in .env matches docker-compose settings

### Frontend Issues

**"Module not found" in frontend**
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

## License

MIT
