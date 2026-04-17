#!/bin/bash
echo "⚡ USING YOUR DATA: data/nasdaq_tickers.csv (57K)"
mkdir -p output
python3 -c "
import subprocess,re,pandas as pd
p=subprocess.Popen(['vscreen','--tickers_file','data/nasdaq_tickers.csv','--output','/dev/null','--api_key','2R0GUY1RK2QJ9PQ8','--max_tickers','100'],stdout=subprocess.PIPE,text=True)
gems=[]
for line in iter(p.stdout.readline,''):
    print(line,end='')
    m=re.search(r'([A-Z]+): score=([0-9.]+)',line)
    if m: gems.append({'ticker':m.group(1),'value_score':float(m.group(2))})
p.wait()
df=pd.DataFrame(gems).sort_values('value_score',ascending=False)
df[df.value_score>30].to_csv('output/fast_gems.csv',index=False)
print('🏆 FAST GEMS:',df[df.value_score>30].head())
"
streamlit run dashboard.py --theme.base dark
