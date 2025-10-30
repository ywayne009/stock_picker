#!/bin/bash

echo "════════════════════════════════════════════════"
echo "  Stock Picking Tool - Development Setup"
echo "════════════════════════════════════════════════"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. You'll need to install PostgreSQL and Redis manually."
    SKIP_DOCKER=true
else
    SKIP_DOCKER=false
fi

# Step 1: Start Docker services
if [ "$SKIP_DOCKER" = false ]; then
    echo "🐳 Starting Docker services (PostgreSQL & Redis)..."
    docker-compose -f docker-compose.services.yml up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 5
    
    # Check if services are healthy
    if docker ps | grep -q "stock_picker_db"; then
        echo "✅ PostgreSQL is running"
    else
        echo "❌ PostgreSQL failed to start"
    fi
    
    if docker ps | grep -q "stock_picker_redis"; then
        echo "✅ Redis is running"
    else
        echo "❌ Redis failed to start"
    fi
    echo ""
fi

# Step 2: Setup Backend
echo "🔧 Setting up Backend..."
cd backend
bash setup.sh
cd ..
echo ""

# Step 3: Setup Frontend
echo "🎨 Setting up Frontend..."
cd frontend
bash setup.sh
cd ..
echo ""

# Step 4: Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env created - please update with your API keys"
else
    echo "✅ .env already exists"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "  ✨ Setup Complete!"
echo "════════════════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Update your .env file with API keys:"
echo "   - OPENAI_API_KEY"
echo "   - POLYGON_API_KEY (or other data provider)"
echo ""
echo "2. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Access the application:"
echo "   Backend API: http://localhost:8000"
echo "   Frontend:    http://localhost:3000"
echo "   API Docs:    http://localhost:8000/docs"
echo ""

if [ "$SKIP_DOCKER" = false ]; then
    echo "🐳 Docker Services:"
    echo "   PostgreSQL: localhost:5432"
    echo "   Redis:      localhost:6379"
    echo ""
    echo "   To stop services: docker-compose -f docker-compose.services.yml down"
    echo ""
fi
