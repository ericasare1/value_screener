#!/usr/bin/env python3
# Safely add --tickers_file to cli.py - NO sed errors
import re

cli_file = "src/value_screener/cli.py"

# Backup original
import shutil
shutil.copy2(cli_file, cli_file + ".bak")

with open(cli_file, 'r') as f:
    content = f.read()

# 1. ADD argument (after --output line)
output_line = r'parser\.add_argument\("--output"'
if re.search(output_line, content):
    new_arg = '\n    parser.add_argument("--tickers_file", type=str, help="Custom tickers file")\n'
    content = re.sub(output_line, output_line + new_arg, content, 1)
    print("✅ Added --tickers_file argument")
else:
    print("❌ --output line not found")
    exit(1)

# 2. REPLACE tickers loading
default_match = r'tickers\s*=\s*DEFAULT_TICKERS'
if re.search(default_match, content):
    new_code = '''if args.tickers_file:
    with open(args.tickers_file, 'r') as f:
        tickers = [line.strip() for line in f if line.strip()]
else:
    tickers = DEFAULT_TICKERS'''
    content = re.sub(default_match, new_code, content, 1)
    print("✅ Added tickers_file logic")
else:
    print("❌ DEFAULT_TICKERS line not found")
    exit(1)

# Write & test
with open(cli_file, 'w') as f:
    f.write(content)

print("🎉 CLI MODIFIED! Testing...")
import subprocess
result = subprocess.run(['python', '-m', 'src.value_screener.cli', '--help'], 
                       capture_output=True, text=True)
if '--tickers_file' in result.stdout:
    print("✅ SUCCESS! --tickers_file works!")
else:
    print("❌ Test failed")
