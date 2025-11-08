"""
Quick test script to verify WSL browser opening works.
"""
from app.services.visualization.strategy_charts import is_wsl, open_in_browser
from pathlib import Path

# Create a simple test HTML file
test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>WSL Browser Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }
        .box {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 2.5em; margin-bottom: 20px; }
        p { font-size: 1.2em; line-height: 1.6; }
        .success { color: #4ade80; font-weight: bold; font-size: 1.5em; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🎉 Success!</h1>
        <p class="success">WSL2 Browser Opening Works!</p>
        <p>If you can see this page, the fix is working correctly.</p>
        <p>Your Python scripts can now automatically open HTML files in Windows browsers from WSL2.</p>
        <hr style="margin: 30px 0; opacity: 0.3;">
        <p><strong>Environment:</strong> WSL2 → Windows Browser</p>
        <p><strong>Status:</strong> ✅ Operational</p>
    </div>
</body>
</html>
"""

# Create output directory if it doesn't exist
output_dir = Path('output/charts')
output_dir.mkdir(parents=True, exist_ok=True)

# Write test HTML
test_file = output_dir / 'wsl_test.html'
with open(test_file, 'w') as f:
    f.write(test_html)

print("=" * 60)
print("WSL Browser Opening Test")
print("=" * 60)
print(f"\n✓ Test HTML file created: {test_file}")
print(f"✓ WSL detected: {is_wsl()}")
print(f"\nAttempting to open in Windows browser...")
print("-" * 60)

try:
    open_in_browser(str(test_file))
    print("\n✅ Browser command executed successfully!")
    print(f"\nIf the browser didn't open automatically, you can manually open:")
    print(f"   {test_file.absolute()}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"\nPlease manually open: {test_file.absolute()}")

print("\n" + "=" * 60)
