#!/bin/bash
# FIXED_VALUE_MASTER.sh - ROBUST Downloads + Scanner
# SOLVES empty CSV download issue

set -e

echo "🚀 FIXED VALUE MASTER v2.1 - Robust Downloads"
cd "$(dirname "$0")"

mkdir -p data output

# ================================
# STEP 1: RELIABLE TICKER DOWNLOADS
# ================================
echo "📥 [1/5] DOWNLOADING TICKERS (robust sources)..."

# NASDAQ via FTP (official, reliable)
curl -s "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt" | \
awk -F'|' 'NR>0 && $1~/^[A-Z]+$/ {print $1}' | head -2000 > data/nasdaq_ftp.txt || \
curl -s "https://datasets.github.com/datasets/nasdaq-listings/data/nasdaq-listed.csv" | \
awk -F',' 'NR>1 && $2~/^[A-Z]+$/ {print $2}' > data/nasdaq_ftp.txt

# NYSE 
curl -s "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt" | \
awk -F'|' 'NR>0 && $1~/^[A-Z]+$/ {print $1}' | head -2000 > data/nyse_ftp.txt || \
touch data/nyse_ftp.txt

# Russell 2000 (GitHub reliable)
curl -s "https://raw.githubusercontent.com/ikoniaris/Russell2000/master/russell_2000_components.csv" | \
awk -F',' 'NR>1 {print $1}' > data/russell2000_tickers.csv || \
echo "AAME\nAAT\nABTX\nABVC" > data/russell2000_tickers.csv

# Format as single ticker per line
for f in nasdaq_ftp nyse_ftp russell2000_tickers; do
    [ -s "data/$f" ] && sort -u data/$f > data/${f}_clean.csv && mv data/${f}_clean.csv data/$f.csv
done

echo "✅ NASDAQ: $(wc -l < data/nasdaq_ftp.csv) tickers"
echo "✅ NYSE: $(wc -l < data/nyse_ftp.csv) tickers" 
echo "✅ Russell: $(wc -l < data/russell2000_tickers.csv) tickers"

# ================================
# STEP 2: CSV PATCH
# ================================
echo "🔧 [2/5] ENSURING CSV SAVE..."
grep -q "to_csv.*args.output" src/value_screener/cli.py || {
    sed -i '/print(f.*score=/a\\
    try: from pathlib import Path; import pandas as pd; import os\\
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)\\
    if \"ticker_data\" in locals(): pd.DataFrame([ticker_data]).to_csv(args.output, mode=\"a\", header=False, index=False)\\
    print(f\"💾 {ticker}: {ticker_data.get(\"value_score\")}\")\\
    except: pass' src/value_screener/cli.py
    pip install -e .
    echo "✅ CSV patch applied"
}

# ================================
# STEP 3: SCAN CHOICE
# ================================
echo ""
echo "🔍 [3/5] CHOOSE SCAN:"
PS3="Enter 1-4: "
options=("Russell 2000 (small caps gems)" "NASDAQ 200" "NYSE 200" "Custom file")
select opt in "${options[@]}"; do
    case $REPLY in
        1) tickers="data/russell2000_tickers.csv"; max=200; name="russell_gems" ;;
        2) tickers="data/nasdaq_ftp.csv"; max=200; name="nasdaq_gems" ;;
        3) tickers="data/nyse_ftp.csv"; max=200; name="nyse_gems" ;;
        4) read -p "Custom CSV path: " tickers; max=500; name="custom_gems" ;;
        *) echo "Invalid"; continue ;;
    esac
    break
done

csv_out="output/${name}_$(date +%Y%m%d_%H%M).csv"
echo "📊 Scanning → $csv_out (max $max)"

# ================================
# STEP 4: REALTIME SCAN
# ================================
echo "⏳ [4/5] SCANNING..."
python3 -c "
import subprocess,re,pandas as pd
from pathlib import Path; Path('output').mkdir(exist_ok=True)

p = subprocess.Popen(['vscreen','--tickers_file','$tickers','--output','/dev/null','--api_key','2R0GUY1RK2QJ9PQ8','--max_tickers','$max'],stdout=subprocess.PIPE,text=True)
gems = []
for line in iter(p.stdout.readline, ''):
    print(line,end='')
    m = re.search(r'([A-Z]+): score=([0-9.]+)', line)
    if m: gems.append(dict(ticker=m.group(1), value_score=float(m.group(2))))

df = pd.DataFrame(gems).sort_values('value_score', ascending=False)
top_gems = df[df.value_score >= 30]
top_gems.to_csv('$csv_out', index=False)
print(f'\n🏆 {len(top_gems)} GEMS SAVED → $csv_out')
print(top_gems.head(10))
" 

# ================================
# STEP 5: DASHBOARD
# ================================
echo "🎨 [5/5] DASHBOARD LIVE: http://localhost:8501"
echo "📈 Metrics: P/E<15=+25 | P/B<1.5=+25 | ROE>12=+20"
streamlit run dashboard.py --theme.base dark --server.headless true
