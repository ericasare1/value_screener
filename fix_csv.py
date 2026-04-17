import re
with open('src/value_screener/cli.py', 'r+') as f:
    content = f.read()
    # Insert save after score print
    pattern = r'(print\([^)]*score=[0-9.]+\s+passes[^)]*\))'
    replacement = r'''\1
        # AUTO CSV SAVE
        try:
            from pathlib import Path
            import pandas as pd
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            if "ticker_data" in locals() and ticker_data:
                df = pd.DataFrame([ticker_data])
                mode = "w" if not os.path.exists(args.output) else "a"
                header = not os.path.exists(args.output)
                df.to_csv(args.output, index=False, mode=mode, header=header)
                print(f"💾 SAVED {locals().get('ticker', 'N/A')}: score={ticker_data.get('value_score', 'N/A')}->{args.output}")
        except Exception as e:
            print(f"Save error: {e}")'''
    
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    f.seek(0)
    f.write(content)
    f.truncate()
print("✅ CSV SAVE FIXED!")
