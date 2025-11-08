#!/bin/bash
# Script to upgrade Python from 3.8 to 3.11 in WSL2
# Run this script with: bash UPGRADE_PYTHON.sh

set -e  # Exit on error

echo "=========================================="
echo "Python 3.11 Installation Script"
echo "=========================================="
echo ""

echo "Step 1: Installing software-properties-common..."
sudo apt update
sudo apt install -y software-properties-common

echo ""
echo "Step 2: Adding deadsnakes PPA (provides Python 3.11)..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update

echo ""
echo "Step 3: Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev

echo ""
echo "Step 4: Verifying Python 3.11 installation..."
python3.11 --version

echo ""
echo "=========================================="
echo "✅ Python 3.11 installed successfully!"
echo "=========================================="
echo ""
echo "Next steps (run these manually):"
echo "1. cd /home/wayne/main/labs/stock_picker/backend"
echo "2. python3.11 -m venv venv"
echo "3. source venv/bin/activate"
echo "4. pip install --upgrade pip"
echo "5. pip install -r requirements.txt"
echo "6. python demo_strategy.py"
echo ""
