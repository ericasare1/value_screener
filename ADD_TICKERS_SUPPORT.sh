#!/bin/bash
# Add --tickers_file support to src/value_screener/cli.py
cd "$(dirname "$0")"

echo "🔧 Adding --tickers_file support to CLI..."

# 1. ADD argument parser line (after --output)
sed -i '/--output.*required=True/i\\
parser.add_argument("--tickers_file", type=str, help="Custom tickers file (one per line)")' \
  src/value_screener/cli.py

# 2. REPLACE DEFAULT_TICKERS loading (find tickers = DEFAULT_TICKERS)
sed -i 's|tickers = DEFAULT_TICKERS|if args.tickers_file:\n        with open(args.tickers_file, "r") as f:\n            tickers = [line.strip() for line in f if line.strip()]\n    else:\n        tickers = DEFAULT_TICKERS|' \
  src/value_screener/cli.py

echo "✅ --tickers_file SUPPORT ADDED!"
echo "Test: python -m src.value_screener.cli --tickers_file data/russell2000.txt --output test.csv"
echo "Help: python -m src.value_screener.cli --help"
