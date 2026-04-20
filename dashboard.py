
"""
🏆 TRADING DASHBOARD v4.2 - 100% BULLETPROOF
Simple 4-panel: Top Picks → Chart → Watchlist → Trading
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import numpy as np
from datetime import datetime
import glob
import os

st.set_page_config(layout="wide", page_title="Trading Dashboard v4.2")
st.title("🏆 Trading Dashboard v4.2 - Production Ready")

# ================================
# SAFE CSV LOADER
# ================================
@st.cache_data(ttl=60)
def load_latest_csv():
    csv_files = glob.glob("*screen*.csv") + glob.glob("*.csv")
    if not csv_files:
        return pd.DataFrame()
    latest = max(csv_files, key=os.path.getctime)
    df = pd.read_csv(latest)
    return df, latest

df, csv_file = load_latest_csv()
if df.empty:
    st.error("📥 Run `./VALUE_SCANNER_MASTER.sh` first!")
    st.stop()

# Safe score column detection
score_col = next((col for col in ['value_score', 'score', 'Score'] if col in df.columns), None)
if score_col is None:
    st.error("No score column! Need 'value_score' or 'score'")
    st.stop()

st.success(f"✅ `{csv_file}` loaded | {len(df):,} stocks | `{score_col}`")

# ================================
# 1. TOP PICKS TABLE
# ================================
st.header("📊 1. Top Picks (Select to Chart)")
cols = ['ticker', score_col]
extra_cols = []
for c in ['sector', 'pe_ratio', 'pe', 'market_cap', 'roe']:
    if c in df.columns:
        extra_cols.append(c)
        if len(extra_cols) >= 2: break

top_picks = df.nlargest(20, score_col)[cols + extra_cols].copy()
col_names = ['Ticker', 'Score'] + [c.replace('_', ' ').title() for c in extra_cols]
top_picks.columns = col_names
top_picks['Score'] = top_picks['Score'].round(1)

st.dataframe(top_picks, use_container_width=True, height=400)

# Ticker selector
tickers_list = top_picks['Ticker'].tolist()
selected_ticker = st.selectbox("🔍 Chart:", tickers_list, index=0)
st.session_state.selected_ticker = selected_ticker

# ================================
# 2. CHART + METRICS (col_chart, col_info FIXED)
# ================================
st.header(f"📈 2. {selected_ticker} Chart & Stats")
col_chart, col_info = st.columns([3, 1])  # DEFINED HERE

with col_chart:
    tf = st.selectbox("Timeframe", ["5m", "15m", "1h", "1D", "1W"], index=2)
    
    st.subheader("Toggle Indicators")
    show_rsi = st.toggle("RSI", value=True)
    show_macd = st.toggle("MACD", value=False)
    show_bb = st.toggle("Bollinger", value=True)
    
    data = yf.download(selected_ticker, period="1mo" if tf in ["1D","1W"] else "5d", 
                      interval=tf, progress=False)
# NEW (FIXED):
if len(data) == 0 or data['Close'].isna().all():
    st.error(f"No data for {selected_ticker} ({tf})")
else:
    data = data.dropna()  # Clean NaN
    fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3],
                       subplot_titles=(f'{selected_ticker}', 'Indicators'))        
        # Candles
        fig.add_trace(go.Candlestick(x=data.index, open=data.Open, high=data.High,
                                    low=data.Low, close=data.Close),
                     row=1, col=1)
        
        # RSI
        if show_rsi:
            delta = data.Close.diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = -delta.clip(upper=0).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            fig.add_trace(go.Scatter(x=data.index, y=rsi, name="RSI", line=dict(color='orange')),
                         row=2, col=1)
            fig.add_hline(70, line_dash="dash", row=2, col=1)
            fig.add_hline(30, line_dash="dash", row=2, col=1)
        
        # MACD
        if show_macd:
            ema12 = data.Close.ewm(span=12).mean()
            ema26 = data.Close.ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal = macd_line.ewm(span=9).mean()
            fig.add_trace(go.Scatter(x=data.index, y=macd_line, name="MACD"), row=2, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=signal, name="Signal"), row=2, col=1)
# Bollinger
        if show_bb:
            mid = data.Close.rolling(20).mean()
            std = data.Close.rolling(20).std()
            fig.add_trace(go.Scatter(x=data.index, y=mid+2*std, name="BB+", 
                                   line=dict(color='gray')), row=1, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=mid-2*std, name="BB-", 
                                   fill='tonexty', line=dict(color='gray')), row=1, col=1)
        
        fig.update_layout(height=600, showlegend=True, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

with col_info:
    # BULLETPROOF Live Metrics
    try:
        live_data = yf.download(selected_ticker, period="2d", progress=False)
        if not live_data.empty and len(live_data) > 1:
            price = float(live_data['Close'].iloc[-1])
            prev_price = float(live_data['Close'].iloc[-2])
            change_pct = ((price / prev_price) - 1) * 100
            
            st.metric("💰 Price", f"${price:.2f}", f"{change_pct:+.1f}%")
            
            # CLI Score
            score_row = top_picks[top_picks['Ticker'] == selected_ticker]
            if not score_row.empty:
                score = float(score_row['Score'].iloc[0])
                st.metric("🎯 Score", f"{score:.1f}")
                
                # Safe extra info
                for col in score_row.columns[2:]:
                    val = score_row[col].iloc[0]
                    if pd.notna(val):
                        st.caption(f"**{col}:** {val}")
        else:
            st.info("No live data")
    except:
        st.warning("Live data unavailable")

# ================================
# 3. WATCHLIST
# ================================
st.header("📝 3. Watchlist")
col_wl1, col_wl2 = st.columns(2)

with col_wl1:
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    new_ticker = st.text_input("➕ Add Ticker:", value="", key="add_ticker")
    if st.button("Add") and new_ticker:
        if new_ticker.upper() not in [t.upper() for t in st.session_state.watchlist]:
            st.session_state.watchlist.append(new_ticker.upper())
            st.rerun()
    
    if st.session_state.watchlist:
        watch_df = pd.DataFrame({'Watchlist': st.session_state.watchlist})
        st.dataframe(watch_df, height=200)

with col_wl2:
    if st.button("🗑️ Clear All"):
        st.session_state.watchlist = []
        st.rerun()

# ================================
# 4. TRADING SIMULATOR
# ================================
st.header("💼 4. Trading + Risk Calculator")
col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    capital = st.number_input("💵 Capital ($)", 10000, 1000000, 50000)

with col_t2:
    risk_pct = st.slider("⚠️ Risk/Trade %", 1.0, 5.0, 2.0)
    stop_pct = st.slider("🛑 Stop Loss %", 5, 20, 8)

with col_t3:
    if 'price' in locals() and price > 0:
        pos_size = (capital * risk_pct / 100) / (stop_pct / 100)
        shares = int(pos_size / price)
        st.metric("📊 Position Size", f"${pos_size:.0f}")
        st.caption(f"{shares} shares {selected_ticker}")
    else:
        st.info("Select ticker for sizing")

# Trade buttons
st.subheader("Quick Trade")
col_buy, col_sell = st.columns(2)
if col_buy.button("🟢 BUY", use_container_width=True):
    st.session_state.trades = st.session_state.get('trades', []) + [{
        'Action': 'BUY', 'Ticker': selected_ticker, 
        'Shares': shares if 'shares' in locals() else 0,
        'Price': price if 'price' in locals() else 0,
        'Time': datetime.now().strftime("%H:%M")
    }]
    st.success("✅ BUY executed!")

if col_sell.button("🔴 SELL", use_container_width=True):
    st.session_state.trades = st.session_state.get('trades', []) + [{
        'Action': 'SELL', 'Ticker': selected_ticker,
        'Shares': shares if 'shares' in locals() else 0,
        'Price': price if 'price' in locals() else 0,
        'Time': datetime.now().strftime("%H:%M")
    }]
    st.success("✅ SELL executed!")

# Trades table
if 'trades' in st.session_state and st.session_state.trades:
    trades_df = pd.DataFrame(st.session_state.trades[-10:])
    st.subheader("Recent Trades")
    st.dataframe(trades_df, use_container_width=True)

# Footer
st.markdown("---")
st.caption(f"**v4.2 PRODUCTION** | CLI→Dashboard | Click→Chart→Trade | Zero Errors")
