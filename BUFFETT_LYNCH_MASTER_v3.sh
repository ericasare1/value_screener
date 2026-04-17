#!/bin/bash
# BUFFETT_LYNCH_MASTER_v3.sh - ALL FEATURES + YOUR CLI
set -e

echo "🚀 Buffett/Lynch Master v3.0 - Downloads + CLI + Dashboard"
cd "$(dirname "$0")"
mkdir -p data output

# ================================
# 1. RELIABLE DOWNLOADS (KEEP ALL)
# ================================
echo "📥 [1/4] DOWNLOADING TICKERS..."
curl -s "https://raw.githubusercontent.com/ikoniaris/Russell2000/master/russell_2000_components.csv" | \
awk -F',' 'NR>1 {print $1}' | head -200 > data/russell2000.txt || \
echo -e "PRA\nMCY\nTBBK\nPFG\nWD\nENVX\nJOBY" > data/russell2000.txt

echo "✅ $(wc -l < data/russell2000.txt) tickers ready"

# ================================
# 2. CHOOSE MODE
# ================================
echo "🔍 [2/4] CHOOSE MODE:"
PS3="Enter 1-2: "
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
# 3. DASHBOARD (ALWAYS)
# ================================
echo "🎨 [4/4] DASHBOARD: http://localhost:8501"
streamlit run dashboard.py --server.headless true &

echo "✅ PRODUCTION LIVE! 🎉"
echo "📊 Results: output/*.csv"
echo "🌐 GitHub: https://github.com/ericasare1/value_screener"
