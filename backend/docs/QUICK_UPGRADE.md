# Quick Python 3.11 Upgrade Guide

## 🚀 Run These Commands in Your WSL2 Terminal

### Option 1: Run the automated script
```bash
cd /home/wayne/main/labs/stock_picker/backend
bash UPGRADE_PYTHON.sh
```

### Option 2: Manual step-by-step (if you prefer control)

```bash
# 1. Install Python 3.11
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 2. Verify installation
python3.11 --version
# Should show: Python 3.11.x

# 3. Navigate to backend directory
cd /home/wayne/main/labs/stock_picker/backend

# 4. Remove old venv (if it exists)
rm -rf venv

# 5. Create NEW virtual environment with Python 3.11
python3.11 -m venv venv

# 6. Activate the new virtual environment
source venv/bin/activate

# 7. Upgrade pip
pip install --upgrade pip

# 8. Install all dependencies
pip install -r requirements.txt

# 9. Verify Python version in venv
python --version
# Should show: Python 3.11.x

# 10. Test real data fetching
python demo_strategy.py
```

## ✅ Expected Output

After running `python demo_strategy.py`, you should see:
```
1. Fetching real market data for MSFT...

   📈 Stock Information:
   Company: Microsoft Corporation
   Sector: Technology
   Industry: Software—Infrastructure
   Data Points: 600+ (depending on date range)
   Date Range: 2022-XX-XX to 2025-XX-XX
```

**No more "Error fetching real data" message!** 🎉

## 🔄 What This Does

- ✅ Installs Python 3.11 system-wide (alongside Python 3.8)
- ✅ Creates a new virtual environment using Python 3.11
- ✅ Installs all packages compatible with Python 3.11
- ✅ Fixes the yfinance/multitasking compatibility issue
- ✅ Enables real stock data fetching

## 📝 Important Notes

1. **Python 3.8 stays installed** - We're not removing it, just adding 3.11
2. **Virtual environment is local** - Not committed to git
3. **Same process on macOS** - When you switch machines, follow the same steps
4. **requirements.txt is shared** - This file is committed to git

## 🆘 If You Get Errors

### "add-apt-repository: command not found"
```bash
sudo apt install -y software-properties-common
```

### "Unable to locate package python3.11"
The PPA might not be added correctly. Try:
```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
```

### "venv creation failed"
```bash
sudo apt install -y python3.11-venv python3.11-dev
```

## 🎯 Time Estimate

- Installation: 2-3 minutes
- Virtual environment setup: 1 minute
- Dependency installation: 2-3 minutes
- **Total: ~5-7 minutes**

---

**Ready to go? Run the script or follow the manual steps above!**
