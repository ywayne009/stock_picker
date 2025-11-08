# Python Environment Setup Guide

## 🎯 Goal: Consistent Python Environment Across Platforms

This guide ensures you can work on this project seamlessly on **WSL2**, **macOS**, and **Windows** with the same Python version and dependencies.

---

## 📋 Current Status

- **Current Python Version (WSL2):** 3.8.10
- **Required Python Version:** 3.9+ (for yfinance compatibility)
- **Target Python Version:** 3.11 (recommended for production)

---

## 🔑 Key Concepts

### What IS Shared Across Platforms (via Git):
✅ `requirements.txt` - List of Python packages and versions
✅ `.python-version` - Specifies required Python version
✅ `README.md` - Setup instructions
✅ All your `.py` source code
✅ Configuration files

### What is NOT Shared (in `.gitignore`):
❌ `venv/` or `.venv/` - Virtual environment (platform-specific binaries)
❌ `__pycache__/` - Compiled Python files
❌ `.env` - Environment variables with secrets
❌ Platform-specific build artifacts

---

## 🚀 Setup Process (Works on All Platforms)

### Step 1: Install Python 3.11

#### **On WSL2 (Ubuntu):**
```bash
# Update package list
sudo apt update

# Install software-properties-common (for add-apt-repository)
sudo apt install -y software-properties-common

# Add deadsnakes PPA (provides newer Python versions)
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.11 and venv
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

#### **On macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify installation
python3.11 --version
```

#### **On Windows (native, not WSL):**
1. Download Python 3.11 from https://www.python.org/downloads/
2. Run installer, check "Add Python to PATH"
3. Verify: `python --version` or `py -3.11 --version`

---

### Step 2: Create Virtual Environment (Platform-Specific, Not Committed)

#### **On WSL2 / macOS / Linux:**
```bash
cd /home/wayne/main/labs/stock_picker/backend

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Verify Python version inside venv
python --version  # Should show Python 3.11.x
```

#### **On Windows (CMD):**
```cmd
cd C:\path\to\stock_picker\backend

# Create virtual environment
py -3.11 -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Upgrade pip
python -m pip install --upgrade pip

# Verify
python --version
```

#### **On Windows (PowerShell):**
```powershell
cd C:\path\to\stock_picker\backend

# Create virtual environment
py -3.11 -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Upgrade pip
python -m pip install --upgrade pip
```

---

### Step 3: Install Dependencies (Same on All Platforms)

```bash
# Make sure venv is activated (you should see (venv) in your prompt)
pip install -r requirements.txt
```

This installs the exact same packages on all platforms from `requirements.txt`.

---

### Step 4: Update requirements.txt (When You Add New Packages)

```bash
# After installing new packages with pip install <package>
pip freeze > requirements.txt

# Commit the updated requirements.txt to git
git add requirements.txt
git commit -m "Update dependencies"
git push
```

---

## 📦 Creating `.python-version` File

To document the required Python version:

```bash
cd /home/wayne/main/labs/stock_picker
echo "3.11" > .python-version
git add .python-version
git commit -m "Specify Python 3.11 requirement"
```

Tools like `pyenv` can automatically use this file.

---

## 🔄 Workflow on Multiple Machines

### First Time Setup on New Machine:
1. Clone the repo: `git clone <repo-url>`
2. Install Python 3.11 (see Step 1 above)
3. Create virtual environment (see Step 2 above)
4. Install dependencies: `pip install -r requirements.txt`
5. Start coding!

### Daily Workflow:
```bash
# Pull latest changes
git pull

# Activate venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install any new dependencies (if requirements.txt changed)
pip install -r requirements.txt

# Work on code...

# Push changes
git add .
git commit -m "Your changes"
git push
```

### Switching Machines:
Your venv stays on each machine. When you switch:
1. Pull latest code: `git pull`
2. Activate venv: `source venv/bin/activate`
3. Update deps if needed: `pip install -r requirements.txt`

---

## 🛠️ Advanced: Using pyenv (Optional but Recommended)

`pyenv` lets you easily manage multiple Python versions.

### Install pyenv:

**On WSL2/Linux/macOS:**
```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

**On Windows:**
Use `pyenv-win`: https://github.com/pyenv-win/pyenv-win

### Using pyenv:
```bash
# Install Python 3.11
pyenv install 3.11.8

# Set as default for this project
cd /home/wayne/main/labs/stock_picker
pyenv local 3.11.8

# This creates .python-version file automatically
# Now python commands use 3.11.8 in this directory

# Create venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ✅ Verification Checklist

After setup on any platform:

```bash
# Activate venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Check Python version (should be 3.11+)
python --version

# Check packages are installed
pip list

# Verify key packages
python -c "import pandas; print(f'pandas {pandas.__version__}')"
python -c "import yfinance; print(f'yfinance OK')"
python -c "import plotly; print(f'plotly OK')"

# Run demo to test everything
python demo_strategy.py
```

---

## 🔧 Current Task: Upgrade WSL2 to Python 3.11

Let's do this now:

```bash
# 1. Install Python 3.11
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 2. Create NEW virtual environment with Python 3.11
cd /home/wayne/main/labs/stock_picker/backend
python3.11 -m venv venv

# 3. Activate new venv
source venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Test
python --version  # Should show 3.11.x
python demo_strategy.py
```

---

## 📝 Notes

1. **Never commit `venv/` to git** - It's already in `.gitignore`
2. **Always commit `requirements.txt`** - This is how dependencies are shared
3. **Document Python version** - In README.md or `.python-version`
4. **Each platform needs its own venv** - But they use the same requirements.txt
5. **Virtual environments are disposable** - You can delete and recreate anytime

---

## 🆘 Troubleshooting

### "pip not found" after creating venv
```bash
# Ensure you activated the venv
source venv/bin/activate

# Or upgrade pip
python -m pip install --upgrade pip
```

### Different package versions on different platforms
```bash
# Use exact versions in requirements.txt
pip freeze > requirements.txt

# Instead of:
pandas>=1.4.0

# Use:
pandas==1.4.3
```

### Virtual environment activation not working on Windows
```powershell
# PowerShell execution policy issue
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🎯 Summary

**What you commit to git:**
- `requirements.txt` (dependencies)
- `.python-version` (Python version spec)
- All `.py` source code
- Configuration files

**What stays local per machine:**
- `venv/` directory
- `.env` (secrets)
- `__pycache__/`

**Result:**
✅ Same Python version on all machines
✅ Same package versions on all machines
✅ Platform-specific virtual environments work independently
✅ Seamless switching between WSL2, macOS, Windows
