#!/bin/bash
# Script to install Python 3.9 and set up virtual environment
# This is simpler than 3.11 as 3.9 is available in Ubuntu 20.04 repos

set -e  # Exit on error

echo "=========================================="
echo "Python 3.9 Installation for Ubuntu 20.04"
echo "=========================================="
echo ""

echo "Step 1: Installing Python 3.9..."
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev

echo ""
echo "Step 2: Verifying Python 3.9 installation..."
python3.9 --version

echo ""
echo "=========================================="
echo "✅ Python 3.9 installed successfully!"
echo "=========================================="
echo ""
echo "Next: Setting up virtual environment automatically..."
echo ""

# Navigate to backend directory
cd /home/wayne/main/labs/stock_picker/backend

echo "Step 3: Removing old virtual environment (if exists)..."
rm -rf venv

echo ""
echo "Step 4: Creating new virtual environment with Python 3.9..."
python3.9 -m venv venv

echo ""
echo "Step 5: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 6: Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Step 7: Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Python version in venv:"
python --version
echo ""
echo "To activate the virtual environment in future sessions:"
echo "  cd /home/wayne/main/labs/stock_picker/backend"
echo "  source venv/bin/activate"
echo ""
echo "To test real data fetching:"
echo "  python demo_strategy.py"
echo ""
