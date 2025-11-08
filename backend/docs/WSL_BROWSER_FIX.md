# WSL2 Browser Opening Fix

## Problem
When running the demo_strategy.py script in WSL2 (Windows Subsystem for Linux), the charts would not automatically open in a browser. This is because:

1. Python's `webbrowser` module tries to open Linux browsers (which don't exist in WSL2)
2. WSL2 Linux paths (`/home/user/...`) are not accessible to Windows browsers
3. Windows browsers need Windows-formatted paths

## Solution
Modified `backend/app/services/visualization/strategy_charts.py` to:

1. **Detect WSL environment** - Check `/proc/version` for "microsoft"
2. **Convert paths** - Use `wslpath -w` to convert Linux paths to Windows paths
3. **Open Windows browser** - Use `cmd.exe /c start` to open files in default Windows browser

## Changes Made

### Added Helper Functions (Lines 29-87)

```python
def is_wsl() -> bool:
    """Check if running in WSL (Windows Subsystem for Linux)."""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False

def open_browser_wsl(filepath: str) -> bool:
    """
    Open a file in the default Windows browser from WSL.

    Args:
        filepath: Path to the HTML file (Linux path)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert WSL path to Windows path
        result = subprocess.run(
            ['wslpath', '-w', filepath],
            capture_output=True,
            text=True,
            check=True
        )
        windows_path = result.stdout.strip()

        # Open in Windows default browser
        subprocess.run(
            ['cmd.exe', '/c', 'start', '', windows_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        print(f"Warning: Could not auto-open browser in WSL: {e}")
        print(f"Please manually open: {filepath}")
        return False

def open_in_browser(filepath: str) -> None:
    """
    Open HTML file in browser, with WSL2 support.

    Args:
        filepath: Path to the HTML file
    """
    abs_path = str(Path(filepath).absolute())

    if is_wsl():
        # WSL environment - use Windows browser
        open_browser_wsl(abs_path)
    else:
        # Normal Linux/Mac/Windows
        webbrowser.open('file://' + abs_path)
```

### Updated Browser Opening Call (Line 585)

**Before:**
```python
if auto_open:
    webbrowser.open('file://' + str(Path(output_path).absolute()))
```

**After:**
```python
if auto_open:
    open_in_browser(output_path)
```

## Testing

### Quick Test
Run the test script:
```bash
cd /home/wayne/main/labs/stock_picker/backend
python3 test_wsl_browser.py
```

This should:
1. Create a test HTML file
2. Detect WSL2 environment
3. Open the file in your Windows default browser

### Full Demo Test
Run the full demo:
```bash
python3 demo_strategy.py
```

This should:
1. Download AAPL data
2. Run the Moving Average Crossover strategy
3. Generate interactive charts
4. **Automatically open the dashboard in your Windows browser**

## How It Works

### Path Conversion Example
```
WSL Path:     /home/wayne/main/labs/stock_picker/backend/output/charts/dashboard.html
Windows Path: \\wsl.localhost\Ubuntu\home\wayne\main\labs\stock_picker\backend\output\charts\dashboard.html
```

### Browser Opening Command
```bash
# From WSL, this opens the file in Windows default browser:
cmd.exe /c start "" "\\wsl.localhost\Ubuntu\home\wayne\...\dashboard.html"
```

## Compatibility

✅ **WSL2** - Uses Windows browser (primary use case)
✅ **Native Linux** - Uses system browser via `webbrowser` module
✅ **macOS** - Uses system browser via `webbrowser` module
✅ **Windows (native Python)** - Uses system browser via `webbrowser` module

## Troubleshooting

### Browser doesn't open automatically

**Check 1: Verify WSL detection**
```bash
cat /proc/version
# Should contain "microsoft"
```

**Check 2: Test wslpath**
```bash
wslpath -w /home/wayne/test.html
# Should output Windows path
```

**Check 3: Test cmd.exe**
```bash
cmd.exe /c echo "Hello from WSL"
# Should print message
```

**Fallback: Manual opening**
If automatic opening fails, the script will print the file path. You can manually open it:
1. In Windows Explorer, navigate to: `\\wsl.localhost\Ubuntu\home\wayne\main\labs\stock_picker\backend\output\charts\`
2. Double-click the HTML file

### Permission issues
If you get permission errors:
```bash
# Ensure the output directory exists and is writable
mkdir -p output/charts
chmod 755 output/charts
```

## Notes

- The fix is backward compatible - works on all platforms
- No additional dependencies required (uses built-in tools)
- Graceful fallback if browser opening fails
- Charts are still saved to disk even if browser doesn't open

## Future Improvements

Possible enhancements:
1. Support for specific browser selection (Chrome, Firefox, Edge)
2. Cache Windows path conversion for performance
3. Add browser opening preferences (always/never/ask)
4. Support for WSL1 (currently optimized for WSL2)
