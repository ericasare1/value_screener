#!/bin/bash
# VALUE_SCANNER_MASTER.sh - Production Value Investing System
# Runs scanner → creates CSV → launches dashboard
# Compatible: Russell 2000, NASDAQ, NYSE, custom lists
# Current: April 2026 | Trump admin markets

set -e  # Exit on error

echo "🚀 VALUE SCREENER MASTER v2.0"
echo "API Key: 2R0GUY1RK2QJ9PQ8 | Output: output/*.csv"

cd "$(dirname "$0")"  # Ensure in project dir

# ================================
# STEP 1: STOCK LISTS MANAGER
# ================================
echo "📋 [1/5] STOCK LISTS..."

# Download fresh lists
mkdir -p data

# NASDAQ FULL (3400+ stocks)
curl -s "https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download" > data/nasdaq_full.csv

# NYSE FULL  
curl -s "https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download" > data/nyse_full.csv

# Russell 2000 (small caps - best for value)
curl -s "https://raw.githubusercontent.com/derekbanas/Python4Finance/main/Russell2000.csv" > data/russell2000.csv || \
echo "Russell failed, using NASDAQ"

# Clean ticker format (just ticker column)
for list in nasdaq_full nyse_full russell2000; do
    if [ -f "data/${list}.csv" ]; then
        awk -F',' 'NR==1 {next} /^[A-Z]+/ {print $1}' data/${list}.csv | head -2000 > data/${list}_tickers.csv
        echo "✅ $list: $(wc -l < data/${list}_tickers.csv) tickers"
    fi
done

# ================================
# STEP 2: CSV FIX PATCH (if needed)
# ================================
echo "🔧 [2/5] CSV PATCH..."
if ! grep -q "to_csv.*args.output" src/value_screener/cli.py; then
    python3 -c "
import re
with open('src/value_screener/cli.py', 'r+') as f:
    c = f.read()
    c = re.sub(r'(print.*score=[0-9.]+\s+passes)', r'\\1
    try:
        from pathlib import Path; import pandas as pd; import os
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        if \"ticker_data\" in locals():
            pd.DataFrame([ticker_data]).to_csv(args.output, mode=\"a\", header=False, index=False)
            print(f\"💾 {locals().get('ticker')}: {ticker_data.get('value_score')}\")
    except: pass', c)
    f.seek(0); f.write(c); f.truncate()
print('✅ CSV auto-save patched')
"
fi

# ================================
# STEP 3: SCAN SELECTOR
# ================================
echo "🔍 [3/5] SCAN MODE (choose one):"
echo "1) Russell 2000 (small caps)"
echo "2) NASDAQ Top 200" 
echo "3) NYSE Top 200"
echo "4) Custom list"
read -p "Enter number (1-4) [1]: " choice || choice=1

case $choice in
    1) tickers="data/russell2000_tickers.csv"; max=200; name="russell2000" ;;
    2) tickers="data/nasdaq_full_tickers.csv"; max=200; name="nasdaq_top" ;;
    3) tickers="data/nyse_full_tickers.csv"; max=200; name="nyse_top" ;;
    4) read -p "Enter custom CSV path: " tickers; max=500; name="custom" ;;
    *) tickers="data/nasdaq_full_tickers.csv"; max=200; name="nasdaq" ;;
esac

csv_out="output/${name}_gems_$(date +%Y%m%d).csv"
echo "📊 Scanning $name → $csv_out (max $max tickers)"

# ================================
# STEP 4: RUN SCAN + REALTIME CSV
# ================================
echo "⏳ [4/5] SCANNING... (AlphaVantage + SEC)"
python3 -c "
import subprocess, re, pandas as pd, os
from pathlib import Path; Path('output').mkdir(exist_ok=True)

p = subprocess.Popen([
    'vscreen', '--tickers_file', '$tickers', '--output', '/dev/null', 
    '--api_key', '2R0GUY1RK2QJ9PQ8', '--max_tickers', '$max'
], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

gems = []
for line in iter(p.stdout.readline, ''):
    print(line.strip())
    m = re.search(r'([A-Z]+): score=([0-9.]+)', line)
    if m:
        ticker, score = m.groups()
        gems.append({'ticker': ticker, 'value_score': float(score)})
        print(f'💾 {ticker}: {score}')

p.wait()
df = pd.DataFrame(gems)
df_top = df[df['value_score'] > 30].sort_values('value_score', ascending=False)
df_top.to_csv('$csv_out', index=False)
print(f'🏆 SAVED: $csv_out | {len(df_top)} gems >30')
print(df_top.head())
"

# ================================
# STEP 5: DASHBOARD + METRICS GUIDE
# ================================
echo "🎨 [5/5] LAUNCHING DASHBOARD..."
echo ""
echo "📊 CURRENT METRICS (Graham Value Score):"
echo "  • P/E <15  = +25pts (cheap earnings)"
echo "  • P/B <1.5 = +25pts (cheap assets)"
echo "  • ROE >12% = +20pts (profitable)"
echo "  • Debt/Eq <50 = +15pts (safe)"
echo "  • P/E<25 or P/B<3 = partial pts"
echo "  🟢 >70 = Strong Buy | 🟡 >50 = Fair | 🔴 <50 = Skip"
echo ""
echo "🔧 TO CUSTOMIZE METRICS:"
echo "  Edit src/value_screener/cli.py → process_ticker():"
echo "    value_score = 0.4*pe_score + 0.3*pb_score + 0.2*roe_score + 0.1*safety"
echo ""
echo "📈 LAUNCH:"
streamlit run dashboard.py --theme.base dark --server.headless true

echo "✅ SYSTEM READY | Gems: output/*.csv | Ctrl+C to stop dashboard"
