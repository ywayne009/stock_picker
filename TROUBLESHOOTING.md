# Troubleshooting Guide

Common issues and solutions for the stock picker project.

---

## 🐍 Python & Environment Issues

### "python: command not found"
**Solution:** Use `python3` or `python3.9` instead:
```bash
python3.9 -m venv venv
```

### "No module named 'plotly'" (or other packages)
**Solution:** Ensure virtual environment is activated:
```bash
source venv/bin/activate  # Mac/Linux/WSL
# or
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### "Python 3.9 not found" on Ubuntu 20.04
**Solution:** Install Python 3.9:
```bash
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev
```

### "'type' object is not subscriptable"
**Cause:** Python 3.8 incompatible with yfinance
**Solution:** Upgrade to Python 3.9+:
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Virtual environment creation fails
**Error:** `ensurepip is not available`
**Solution:**
```bash
sudo apt install python3.9-venv
```

---

## 🌐 Browser & Display Issues

### Charts don't open in browser (WSL2)
**Cause:** WSL2 can't directly open Windows browsers
**Status:** ✅ Fixed in latest version
**Verify Fix:**
```python
from app.services.visualization.strategy_charts import is_wsl
print(f"WSL detected: {is_wsl()}")  # Should be True
```

**Manual workaround:**
1. Charts save to `backend/output/charts/`
2. In Windows Explorer: `\\wsl.localhost\Ubuntu\home\wayne\main\labs\stock_picker\backend\output\charts\`
3. Double-click HTML files

### Charts don't open on Mac
**Check:** Ensure default browser is set
**Workaround:** Manually open HTML files from `backend/output/charts/`

---

## 📊 Data Fetching Issues

### "Error fetching real data"
**Possible Causes:**
1. **No internet connection**
   ```bash
   ping google.com  # Test connection
   ```

2. **yfinance rate limiting**
   - Wait a few minutes, try again
   - Use different stock symbol

3. **Invalid stock symbol**
   - Verify symbol exists: https://finance.yahoo.com
   - Try common symbols: AAPL, MSFT, GOOGL, TSLA

**Fallback:** Demo uses synthetic data automatically if real data fails

### "SSL certificate error"
**Solution:**
```bash
pip install --upgrade certifi
```

### "Too few data points"
**Cause:** Recent IPO or short history
**Solution:** Choose older stock or reduce `years_back`:
```python
# In demo_strategy.py
YEARS_BACK = 1  # Reduce from 2.5 to 1
```

---

## 🔐 Git & SSH Issues

### "Permission denied (publickey)"
**Solution:** Ensure SSH key is added:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh -T git@github.com  # Test connection
```

### "Authentication failed" (HTTPS)
**Solution:** Switch to SSH:
```bash
git remote set-url origin git@github.com:ywayne009/stock_picker.git
```

Or use GitHub Personal Access Token (not password):
1. Create token: github.com/settings/tokens
2. Use token as password when pushing

### "fatal: could not read Username"
**Cause:** HTTPS without credential helper
**Solution:** Set up SSH (see SETUP.md) or configure git credentials:
```bash
git config --global credential.helper cache
```

### SSH key already exists
**Check existing key:**
```bash
cat ~/.ssh/id_ed25519.pub
```
**Reuse it** or **generate new one** with different name:
```bash
ssh-keygen -t ed25519 -C "email@example.com" -f ~/.ssh/id_ed25519_new
```

---

## 📦 Package Issues

### "ERROR: Could not find a version that satisfies the requirement"
**Cause:** Package incompatible with Python version
**Solution:** Ensure Python 3.9+:
```bash
python --version  # Inside venv
```

### Plotly/kaleido installation fails
**macOS:**
```bash
brew install --cask chromedriver  # May help with kaleido
```

**Linux:**
```bash
sudo apt install -y chromium-browser
```

**Workaround:** Charts still generate as HTML (PNG/PDF export may not work)

### ta-lib installation fails
**Status:** Commented out in requirements.txt (not needed)
**Reason:** Requires C library installation
**Alternative:** Using pandas-based indicators (already implemented)

---

## 🖥️ Platform-Specific Issues

### WSL2: "wslpath: command not found"
**Rare, but possible**
**Solution:**
```bash
sudo apt install wslu
```

### macOS: "command not found: python3.9"
**Solution:** Specify brew version:
```bash
/usr/local/opt/python@3.9/bin/python3.9 -m venv venv
```

Or create alias:
```bash
echo 'alias python3.9=/usr/local/opt/python@3.9/bin/python3.9' >> ~/.zshrc
source ~/.zshrc
```

### Windows: PowerShell script execution disabled
**Error:** `cannot be loaded because running scripts is disabled`
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🎯 Demo Script Issues

### demo_strategy.py runs but no charts
**Check:**
1. Look for HTML files: `ls backend/output/charts/`
2. Check console for errors
3. Verify `auto_open=True` in code

**Manual open:**
```bash
cd backend/output/charts
open ma_20_50_dashboard.html  # Mac
xdg-open ma_20_50_dashboard.html  # Linux
start ma_20_50_dashboard.html  # Windows
```

### "No signals generated"
**Cause:** Strategy parameters don't match data
**Solution:** Try different parameters or stock:
```python
# In demo_strategy.py
STOCK_SYMBOL = 'AAPL'  # Try different stock
YEARS_BACK = 5  # More data = more signals
```

### Performance metrics show "N/A"
**Cause:** Insufficient data or no trades executed
**Check:** Ensure buy/sell signals were generated

---

## 🔧 Development Issues

### Import errors after code changes
**Solution:** Restart Python, ensure venv is activated
```bash
deactivate  # Exit venv
source venv/bin/activate  # Re-enter
python demo_strategy.py
```

### Changes not reflected
**Check:**
1. Saved file? (Ctrl+S / Cmd+S)
2. Right file? (Check file path)
3. Cached imports? (Restart Python)

### Git merge conflicts
**Prevention:** Always `git pull` before making changes
**Resolution:**
```bash
git status  # See conflicted files
# Edit files, remove conflict markers (<<<<, ====, >>>>)
git add <resolved-file>
git commit -m "Resolve merge conflict"
```

---

## 💡 Performance Issues

### Slow data fetching
**Cause:** Downloading large datasets
**Solutions:**
- Reduce `years_back`
- Use cached data (already implemented)
- Use sample data: `backend/data/AAPL.csv`

### Charts take long to generate
**Normal:** Large datasets (5MB+ HTML files)
**Optimization:** Reduce data points or chart complexity

### High memory usage
**Cause:** Large pandas DataFrames
**Monitor:**
```bash
# Before running
free -h  # Linux/WSL
top      # Check memory during execution
```

---

## 🆘 Getting Help

### Check Documentation
1. `SETUP.md` - Setup instructions
2. `SESSION_NOTES.md` - Project history
3. `backend/STRATEGY_DEMO_GUIDE.md` - Strategy guide
4. `CLAUDE.md` - Development guidelines

### Debug Mode
Add to script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Imports
```bash
python -c "
import pandas as pd
import yfinance as yf
import plotly
print('All imports OK')
"
```

### Check Versions
```bash
python --version
pip list | grep -E "(pandas|plotly|yfinance)"
```

### Clean Start
```bash
# Remove and recreate venv
rm -rf venv
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| No browser opening (WSL2) | Already fixed, update code |
| Module not found | `source venv/bin/activate && pip install -r requirements.txt` |
| Data fetch fails | Check internet, try different symbol |
| Python 3.9 not found | `sudo apt install python3.9 python3.9-venv` |
| Git authentication fails | Set up SSH (see SETUP.md) |
| Charts in wrong place | Check `backend/output/charts/` |
| Slow performance | Reduce `years_back` in demo |

---

**Last Updated:** 2025-11-08
**Need more help?** Check SESSION_NOTES.md for recent changes
