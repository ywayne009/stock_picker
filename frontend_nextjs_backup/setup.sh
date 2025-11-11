#!/bin/bash

echo "🚀 Setting up Stock Picker Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check Node version
node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
required_version=18

if [ "$node_version" -lt "$required_version" ]; then
    echo "⚠️  Warning: Node.js $node_version detected. Node.js 18+ is recommended."
fi

# Install dependencies
echo "📥 Installing dependencies..."
npm install

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local..."
    cat > .env.local << 'ENVEOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
ENVEOF
    echo "✅ .env.local created"
else
    echo "✅ .env.local already exists"
fi

echo ""
echo "✨ Frontend setup complete!"
echo ""
echo "To start the development server, run:"
echo "  npm run dev"
echo ""
echo "The app will be available at:"
echo "  http://localhost:3000"
echo ""
