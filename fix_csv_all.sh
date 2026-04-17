#!/bin/bash
# Fix vscreen - Save ALL scores (not just passes=True)

# Backup
cp src/value_screener/cli.py src/value_screener/cli.py.bak.csv_all

# Replace df[df['passes'] == True] with df (save ALL)
sed -i "/df\\['passes'/,/to_csv.*index=False/c\\
df.to_csv(output_file, index=False)  # Save ALL scored stocks" src/value_screener/cli.py

echo "✅ CSV fix applied - now saves ALL scores!"
echo "🔄 Reinstall"
pip install -e .

echo "🧪 Test"
echo -e "ticker\nAAPL\nWSBF" > data/test_tickers.csv
vscreen --tickers_file data/test_tickers.csv --output output/test_all.csv
head output/test_all.csv

echo "🚀 NASDAQ rerun - will show gems!"
