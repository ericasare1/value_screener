import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os
import time
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🏆 Buffett/Lynch Value Screener")
st.markdown("**Real-time screening across ALL CSV files** 🎯")

# 🔥 AUTO-DETECT ALL screening CSVs (nasdaq_screen.csv, nyse_screen.csv, daily.csv, etc)
csv_files = glob.glob("*screen*.csv") + glob.glob("*_screen.csv") + glob.glob("*.csv")
latest = max(csv_files, key=os.path.getctime) if csv_files else None

if latest:
    st.success(f"✅ Loaded latest: `{latest}` | Shape: {pd.read_csv(latest).shape} | Updated: {datetime.fromtimestamp(os.path.getctime(latest))}")
    df = pd.read_csv(latest)
    st.write("**Columns:**", df.columns.tolist())
    
    # Find score column (flexible)
    score_col = None
    for col in ['value_score', 'score', 'Score', 'buffet', 'lynch']:
        if col in df.columns:
            score_col = col
            break
    
    if score_col:
        # Top metrics
        top_score = df[score_col].max()
        top_idx = df[score_col].idxmax()
        top_ticker = df.loc[top_idx, 'ticker'] if 'ticker' in df.columns else df.iloc[top_idx].name
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🔥 Top Score", f"{top_score:.1f}")
        col2.metric("🏆 Top Pick", top_ticker)
        col3.metric("📊 Total Stocks", f"{len(df):,}")
        
        # Top 5 table
        st.subheader("📈 Top Value Picks")
        top_df = df.nlargest(5, score_col)[['ticker', score_col, 'company_name', 'mcap_billions']].round(1)
        st.dataframe(top_df, use_container_width=True)
        
        # Portfolio ready (80+ scores)
        high_value = df[df[score_col] >= 80]
        if len(high_value) > 0:
            st.subheader("💎 Portfolio Ready (80+ scores)")
            st.dataframe(high_value.nlargest(10, score_col), use_container_width=True)
        
        # Charts
        st.subheader("📊 Value Score Distribution")
        fig_hist = px.histogram(df, x=score_col, nbins=50, title="Score Distribution")
        st.plotly_chart(fig_hist, use_container_width=True)
        
    else:
        st.error("❌ No score column found. Expected: 'value_score', 'score'")
        
else:
    st.warning("📥 No screening CSV found. Run: `python -m value_screener.cli -o screen.csv --tickers_file tickers.txt`")
    st.stop()

# Auto-refresh every 60 seconds
st.caption("🔄 Auto-refreshing every 60s...")
time.sleep(60)
st.rerun()
