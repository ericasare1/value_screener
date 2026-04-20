"""
🏆 BUFFETT/LYNCH VALUE SCREENER v2.2 - LIVE PRICES
Production dashboard with real-time stock prices + auto CSV detection
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import glob
import os
import time
from datetime import datetime

st.set_page_config(layout="wide", page_title="Value Screener v2.2")
st.title("🏆 Buffett/Lynch Value Screener v2.2")
st.markdown("**🔥 LIVE prices + scores | Auto-detects ALL CSVs | 30s refresh**")

# ================================
# AUTO-DETECT LATEST CSV
# ================================
@st.cache_data(ttl=60)
def load_latest_csv():
    csv_files = glob.glob("*screen*.csv") + glob.glob("*_screen.csv") + glob.glob("*.csv")
    if not csv_files:
        return None, "No screening CSV found"
    latest = max(csv_files, key=os.path.getctime)
    df = pd.read_csv(latest)
    return df, latest

df, csv_file = load_latest_csv()
if df is None:
    st.error("📥 Run `./VALUE_SCANNER_MASTER.sh` first!")
    st.stop()

st.success(f"✅ Loaded: `{csv_file}` | {len(df):,} stocks | Updated: {datetime.fromtimestamp(os.path.getctime(csv_file))}")
st.info(f"**Columns**: {list(df.columns)}")

# ================================
# FIND SCORE COLUMN
# ================================
score_col = None
for col in ['value_score', 'score', 'Score', 'buffet', 'lynch']:
    if col in df.columns:
        score_col = col
        break

if not score_col:
    st.error("❌ No score column found!")
    st.stop()

# ================================
# TOP METRICS
# ================================
top_score = df[score_col].max()
top_idx = df[score_col].idxmax()
top_ticker = df.loc[top_idx, 'ticker'] if 'ticker' in df.columns else "N/A"

col1, col2, col3 = st.columns(3)
col1.metric("🔥 Highest Score", f"{top_score:.1f}")
col2.metric("🏆 Top Pick", top_ticker)
col3.metric("📊 Total Screened", f"{len(df):,}")

# ================================
# LIVE STOCK PRICES
# ================================
@st.cache_data(ttl=30)  # Refresh every 30s
def get_live_prices(tickers):
    prices = {}
    for ticker in tickers[:8]:  # Limit API calls
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1d")
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                change_pct = ((current - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100
                prices[ticker] = {
                    'price': current,
                    'change': change_pct,
                    'volume': info.get('volume', 0),
                    'mcap': info.get('marketCap', 0) / 1e9
                }
        except:
            prices[ticker] = {'price': 0, 'change': 0, 'volume': 0, 'mcap': 0}
    return prices

# 🔥 LIVE PRICES SECTION
st.subheader("💹 LIVE PRICES - Top 5 Picks")
top_df = df.nlargest(5, score_col)[['ticker', score_col]]
top_tickers = top_df['ticker'].tolist()

if st.button("🔄 Refresh Prices", key="refresh_prices"):
    st.cache_data.clear()

live_prices = get_live_prices(top_tickers)

cols = st.columns(5)
for i, ticker in enumerate(top_tickers):
    data = live_prices[ticker]
    color = "🟢" if data['change'] > 0 else "🔴"
    cols[i].metric(
        f"**{ticker}**\n({top_df[score_col].iloc[i]:.1f})",
        f"${data['price']:.2f}" if data['price'] else "N/A",
        f"{data['change']:+.1f}%" if data['change'] else "N/A",
        delta_color="normal"
    )

# ================================
# TOP 5 VALUE PICKS TABLE
# ================================
st.subheader("📈 Top Value Picks")
display_cols = ['ticker', score_col, 'company_name', 'mcap_billions']
available_cols = [col for col in display_cols if col in df.columns]
top_table = df.nlargest(10, score_col)[available_cols].round(2)
st.dataframe(top_table, use_container_width=True, hide_index=True)

# ================================
# PORTFOLIO READY (80+)
# ================================
high_value = df[df[score_col] >= 80].nlargest(20, score_col)
if len(high_value) > 0:
    st.subheader("💎 PORTFOLIO READY - 80+ Scores")
    st.dataframe(high_value[available_cols].round(2), use_container_width=True, hide_index=True)

# ================================
# CHARTS
# ================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Score Distribution")
    fig_hist = px.histogram(df, x=score_col, nbins=50, title="Value Score Distribution")
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("🏆 Top 20 Picks")
    top20 = df.nlargest(20, score_col)
    fig_bar = px.bar(top20, x='ticker', y=score_col, 
                     title="Top Scores", color=score_col)
    st.plotly_chart(fig_bar, use_container_width=True)

# ================================
# STATUS & REFRESH
# ================================
st.markdown("---")
st.caption(f"🔄 Auto-refresh: 60s | Prices: 30s | Screener: `{csv_file}` | **ARLP/PRA battling for #1!** 💪")

# Auto-refresh
time.sleep(60)
st.rerun()
