# Stock Picker - Setup Guide

Complete setup instructions for development across WSL2, macOS, and Windows.

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+ required
- Git installed
- GitHub account

### Initial Setup

```bash
# 1. Clone repository
git clone git@github.com:ywayne009/stock_picker.git
cd stock_picker

# 2. Set up Python environment
cd backend
python3.9 -m venv venv
source venv/bin/activate  # Mac/Linux/WSL
# or: venv\Scripts\activate  # Windows CMD

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Run demo
python demo_strategy.py
```

**Expected:** Browser opens with interactive charts, real MSFT stock data displayed.

---

## 📋 Platform-Specific Setup

### WSL2 (Ubuntu)

```bash
# Install Python 3.9
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev

# Create virtual environment
cd /home/wayne/main/labs/stock_picker/backend
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**WSL Browser Fix:** Charts automatically open in Windows browsers (already configured).

### macOS

```bash
# Install Python 3.9 via Homebrew
brew install python@3.9

# Create virtual environment
cd ~/path/to/stock_picker/backend
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (Native)

```cmd
# Download Python 3.9+ from python.org
# Ensure "Add to PATH" is checked during installation

cd C:\path\to\stock_picker\backend
py -3.9 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔐 Git & SSH Setup

### Configure Git

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@gmail.com"
```

### Set Up SSH (Recommended)

```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "your.email@gmail.com"
# Press ENTER for all prompts

# 2. Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. Copy public key
cat ~/.ssh/id_ed25519.pub
# Copy the output

# 4. Add to GitHub
# Go to: github.com/settings/keys
# Click "New SSH key", paste key, save

# 5. Test connection
ssh -T git@github.com
# Should say: "Hi username! You've successfully authenticated"
```

**Result:** No password needed for `git push/pull` operations.

---

## 🔄 Daily Workflow

### Start of Day

```bash
cd stock_picker
git pull                          # Get latest changes
cd backend
source venv/bin/activate          # Activate Python env
python demo_strategy.py           # Test everything works
```

### During Development

```bash
# Make changes to code...
python demo_strategy.py           # Test your changes
python -m pytest tests/           # Run tests (when available)
```

### End of Day

```bash
git status                        # See what changed
git add .                         # Stage changes
git commit -m "Description"       # Commit
git push                          # Push to GitHub
```

---

## 🌍 Cross-Platform Notes

### What Syncs via Git
✅ All `.py` source code
✅ `requirements.txt` (dependencies)
✅ `.python-version` (Python 3.9)
✅ Documentation files

### What Stays Local (`.gitignore`)
❌ `venv/` directory (platform-specific)
❌ `__pycache__/`
❌ `.env` files
❌ `backend/output/charts/` (generated files)

### Moving Between Machines

**On Machine 1 (WSL2):**
```bash
git push
```

**On Machine 2 (Mac):**
```bash
git pull
# Set up venv if first time (see platform setup above)
source venv/bin/activate
python demo_strategy.py  # Same code, works identically
```

---

## 📦 Project Structure

```
stock_picker/
├── .python-version          # Python 3.9 requirement
├── README.md                # Project overview
├── SETUP.md                 # This file
├── CLAUDE.md                # AI assistant guidelines
├── backend/
│   ├── requirements.txt     # Python dependencies
│   ├── venv/               # Virtual environment (not in git)
│   ├── demo_strategy.py    # Demo script
│   ├── app/
│   │   ├── services/
│   │   │   ├── strategy/   # Trading strategies
│   │   │   ├── data/       # Market data fetching
│   │   │   └── visualization/  # Chart generation
│   ├── data/               # Sample data (AAPL.csv)
│   └── output/charts/      # Generated charts (not in git)
└── frontend/               # React frontend (Phase 2)
```

---

## 🧪 Testing Your Setup

```bash
cd backend
source venv/bin/activate

# Quick verification
python -c "
import sys
import pandas as pd
import yfinance as yf
import plotly
print(f'✓ Python {sys.version.split()[0]}')
print(f'✓ pandas {pd.__version__}')
print(f'✓ yfinance {yf.__version__}')
print(f'✓ plotly {plotly.__version__}')
print('✓ All imports successful!')
"

# Full test
python demo_strategy.py
# Should fetch real MSFT data and open charts in browser
```

---

## ⚙️ Configuration

### Environment Variables

Create `backend/.env` (optional, for future features):
```bash
# API keys (not needed for basic demo)
OPENAI_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
ALPACA_API_KEY=your_key_here
```

### Customize Demo

Edit `backend/demo_strategy.py`:
```python
STOCK_SYMBOL = 'AAPL'  # Change to any ticker: GOOGL, TSLA, SPY
YEARS_BACK = 2.5       # Amount of historical data
```

---

## 🎯 Next Steps

1. **Explore the demo:** Run `python demo_strategy.py` and review the generated charts
2. **Read strategy guide:** `backend/STRATEGY_DEMO_GUIDE.md` for parameter tuning
3. **Check project status:** Review `SESSION_NOTES.md` for recent changes
4. **Start Phase 2:** See `PHASE2_DECISIONS.md` for frontend development plan

---

## 📚 Additional Resources

- **GitHub Repository:** https://github.com/ywayne009/stock_picker
- **Session History:** See `SESSION_NOTES.md`
- **Troubleshooting:** See `TROUBLESHOOTING.md`
- **Development Plan:** See `stock_picking_tool_development_plan0.md`

---

**Updated:** 2025-11-08
