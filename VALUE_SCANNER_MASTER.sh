#!/bin/bash
# VALUE_SCANNER_MASTER.sh v2.1 - FIXED
set -e

echo "🚀 VALUE SCREENER MASTER v2.1 - NASDAQ/NYSE/Russell"

mkdir -p data output

# ================================
# 1. DOWNLOAD TICKERS (FIXED URLs)
# ================================
echo "📋 Downloading tickers..."

# NASDAQ via FTP (bulletproof)
curl -s "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt" | \
awk -F'|' 'NR>0 && $1~/^[A-Z]{1,5}$/ {print $1}' | head -1000 > data/nasdaq_tickers.txt

# NYSE via FTP  
curl -s "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt" | \
awk -F'|' 'NR>0 && $1~/^[A-Z]{1,5}$/ {print $1}' | head -1000 > data/nyse_tickers.txt

echo "✅ NASDAQ: $(wc -l < data/nasdaq_tickers.txt) tickers"
echo "✅ NYSE: $(wc -l < data/nyse_tickers.txt) tickers"

# ================================
# 2. SCAN SELECTOR
# ================================
echo "🔍 Choose scan (1-3): 1=NASDAQ 2=NYSE 3=Both"
read -p "Choice [1]: " choice || choice=1

case $choice in
    1) tickers="data/nasdaq_tickers.txt"; name="nasdaq" ;;
    2) tickers="data/nyse_tickers.txt"; name="nyse" ;;
    3) tickers="data/nasdaq_tickers.txt"; name="nasdaq_nyse" ;;
    *) tickers="data/nasdaq_tickers.txt"; name="nasdaq" ;;
esac

csv_out="output/${name}_screen_$(date +%Y%m%d_%H%M).csv"
echo "📊 Scanning → $csv_out"

# ================================
# 3. RUN YOUR WORKING SCREENER
# ================================
echo "⏳ Scanning $(head -5 "$tickers")..."
python -m value_screener.cli -o "$csv_out" --tickers_file "$tickers"

echo "✅ SAVED: $csv_out ($(wc -l < "$csv_out") rows)"

# ================================
# 4. TOP GEMS
# ================================
echo "🏆 TOP 5 VALUE PICKS:"
grep ",[6-9][0-9]\." "$csv_out" | sort -t, -k2 -nr | head -5

# ================================
# 5. LAUNCH DASHBOARD
# ================================
echo "🎨 Launching live dashboard..."
streamlit run dashboard.py --theme.base dark

echo "✅ PRODUCTION SYSTEM LIVE!"
echo "📊 Gems saved: $csv_out"
echo "🌐 Dashboard: http://localhost:8501"
