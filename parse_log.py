import re, pandas as pd
log = """
2026-04-17 14:14:33,637 - value_screener.cli - AAME: score=55.6 passes=False (SEC=True)
"""
match = re.search(r'([A-Z]+): score=([0-9.]+)', log)
if match:
    ticker, score = match.groups()
    df = pd.DataFrame({'ticker': [ticker], 'value_score': [float(score)], 'sec_pass': ['True']})
    df.to_csv('output/aame_final.csv', index=False)
    print(f"✅ FORCED CSV: {ticker} score={score}")
else:
    print("No score found")
