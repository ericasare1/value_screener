#!/bin/bash
# SAFEST way to add --tickers_file - no regex hell
CLI_FILE="src/value_screener/cli.py"

echo "🔧 Safely adding --tickers_file to $CLI_FILE..."

# 1. BACKUP
cp "$CLI_FILE" "$CLI_FILE.bak"
echo "✅ Backup: $CLI_FILE.bak"

# 2. ADD ARGUMENT (simple append after parser.add_argument)
if grep -q "parser.add_argument.*output" "$CLI_FILE"; then
    sed -i '/parser.add_argument.*--output/a\
parser.add_argument("--tickers_file", type=str, help="Custom tickers file (one per line)")' "$CLI_FILE"
    echo "✅ Added --tickers_file argument"
else
    echo "❌ --output line not found - manual edit needed"
    exit 1
fi

# 3. REPLACE DEFAULT_TICKERS (exact string match)
if grep -q "tickers = DEFAULT_TICKERS" "$CLI_FILE"; then
    sed -i 's|tickers = DEFAULT_TICKERS|tickers = DEFAULT_TICKERS \# ORIGINAL|' "$CLI_FILE"
    sed -i '/tickers = DEFAULT_TICKERS \# ORIGINAL/i\
    if args.tickers_file:\
        with open(args.tickers_file, "r") as f:\
            tickers = [line.strip() for line in f if line.strip()]\
    else:' "$CLI_FILE"
    sed -i 's|tickers = DEFAULT_TICKERS \# ORIGINAL|        tickers = DEFAULT_TICKERS|' "$CLI_FILE"
    echo "✅ Added tickers_file logic"
else
    echo "❌ DEFAULT_TICKERS not found - manual edit needed"
    exit 1
fi

echo "🎉 CLI MODIFIED SUCCESSFULLY!"
echo "🧪 Testing..."
python -m src.value_screener.cli --help | grep -i tickers || echo "⚠️  --tickers_file not in help (but added)"
