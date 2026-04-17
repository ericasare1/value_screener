#!/bin/bash
# BUFFETT_LYNCH_MASTER_v4.sh - DOWNLOADS + CLI + Dashboard
set -e

echo "🚀 Buffett/Lynch Master v4.0 - FULL SYSTEM"
cd "$(dirname "$0")"
mkdir -p data output

# ================================
# MENU 1: DOWNLOAD TICKERS
# ================================
echo "📥 [1/4] DOWNLOAD TICKERS:"
PS3="Choose ticker source (1-4): "
download_options=("Russell 2000 (200)" "NASDAQ Top 200" "NYSE Top 200" "Skip downloads")
select download_opt in "${download_options[@]}"; do
    case $REPLY in
        1) 
            echo "📥 Downloading Russell 2000..."
            curl -s "https://raw.githubusercontent.com/ikoniaris/Russell2000/master/russell_2000_components.csv" | \
            awk -F',' 'NR>1 {print $1}' | head -200 > data/russell2000.txt || \
            echo -e "PRA\nMCY\nTBBK\nPFG\nWD\nENVX\nJOBY" > data/russell2000.txt
            echo "✅ Russell: $(wc -l < data/russell2000.txt) tickers"
            ;;
        2) 
            echo "📥 Downloading NASDAQ..."
            curl -s "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt" | \
            awk -F'|' 'NR>0 && $1~/^[A-Z]+$/ {print $1}' | head -200 > data/nasdaq.txt
            echo "✅ NASDAQ: $(wc -l < data/nasdaq.txt) tickers"
            ;;
        3) 
            echo "📥 Downloading NYSE..."
            curl -s "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt" | \
            awk -F'|' 'NR>0 && $1~/^[A-Z]+$/ {print $1}' | head -200 > data/nyse.txt
            echo "✅ NYSE: $(wc -l < data/nyse.txt) tickers"
            ;;
        4) echo "⏭️ Skipping downloads" ;;
        *) echo "Invalid"; continue ;;
    esac
    break
done

# ================================
# MENU 2: RUN CLI OR DASHBOARD
# ================================
echo ""
echo "🔍 [2/4] RUN MODE:"
PS3="Choose mode (1-2): "
options=("🚀 YOUR CLI (PRA=87.5)" "📈 Dashboard Only")
select opt in "${options[@]}"; do
    case $REPLY in
        1) 
            echo "✅ [3/4] Running YOUR CLI..."
            python -m src.value_screener.cli --output "output/buffet_lynch_$(date +%Y%m%d_%H%M).csv"
            ;;
        2) echo "Skipping CLI → dashboard only" ;;
        *) echo "Invalid"; continue ;;
    esac
    break
done

# ================================
# DASHBOARD (ALWAYS)
# ================================
echo "🎨 [4/4] DASHBOARD: http://localhost:8501"
streamlit run dashboard.py --server.headless true &

echo "✅ PRODUCTION LIVE! 🎉"
echo "📊 Results: output/*.csv"
echo "🌐 GitHub: https://github.com/ericasare1/value_screener"
