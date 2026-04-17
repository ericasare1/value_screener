import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import numpy as np
import os
from pathlib import Path

st.set_page_config(layout="wide", page_title="Value Gems Dashboard 🚀")

@st.cache_data(ttl=600)
def load_csvs():
    files = ['output/nasdaq_gems.csv', 'output/top_gems.csv', 'output/aame_final.csv']
    dfs = []
    for f in files:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f)
                if 'value_score' in df.columns:
                    dfs.append(df)
            except: pass
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True).drop_duplicates('ticker')
        for col in ['value_score', 'pe', 'pb', 'roe']:
            if col in combined.columns:
                combined[col] = pd.to_numeric(combined[col], errors='coerce')
        return combined.sort_values('value_score', ascending=False).dropna(subset=['value_score'])
    return pd.DataFrame({'ticker':[], 'value_score':[]})

def portfolio_value(portfolio):
    total = 0
    for ticker, shares in portfolio.items():
        try:
            price = yf.Ticker(ticker).info.get('regularMarketPrice', 0)
            total += shares * price
        except: pass
    return total

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

st.title("💎 Value Gems Dashboard")
st.markdown("**Live SEC + yfinance scores** (AAME=55.6, AAT=47.2+)")

df = load_csvs()
st.metric("Total Gems", len(df))

if len(df) > 0:
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Top Score", f"{df['value_score'].max():.1f}")
    with col2: st.metric("Gems >50", len(df[df['value_score'] > 50]))
    with col3: st.metric("Avg Score", f"{df['value_score'].mean():.1f}")

    min_score = st.slider("Min Score", 0, 100, 30)
    filtered = df[df['value_score'] >= min_score].head(50)
    
    st.subheader(f"🏆 Top {len(filtered)} Gems")


    st.markdown("**Quick Stats:** 🟢 >70=Strong Buy | 🟡 >50=Fair | 🔴 <50=Overvalued")

    st.dataframe(filtered[['ticker', 'value_score']], use_container_width=True)
    st.markdown("**Quick Stats:** 🟢 >70=Strong Buy | 🟡 >50=Fair | 🔴 <50=Overvalued")


    # STOCK CHARTS
    st.subheader("📈 Live Stock Charts")
    tickers = filtered['ticker'].head(10).tolist()
    selected = st.multiselect("Select tickers:", tickers, default=["AAME"])
    
    for ticker in selected:
        col1, col2 = st.columns([1,3])
        with col1:
            try:
                stock = yf.Ticker(ticker)
                price = stock.info.get('regularMarketPrice', 'N/A')
                st.metric(ticker, f"${price:.2f}" if price != 'N/A' else 'N/A')
            except:
                st.metric(ticker, "No data")
        with col2:
            try:
                hist = stock.history(period="1mo")
                if not hist.empty:
                    fig = px.line(hist.reset_index(), x='Date', y='Close', 
                                title=f"{ticker} Price")
                    st.plotly_chart(fig, use_container_width=True)
            except:
                st.write("No chart")


else:
    st.info("Run scanner → output/*.csv → refresh!")

# === CLEAN UNIVERSAL ANALYZER (BOTTOM) ===
st.markdown("---")
st.subheader("🔍 Universal Stock Analyzer + Graham Score")
manual_ticker = st.text_input("ANY ticker (AAPL, TSLA, AAME):", value="AAPL").upper()

if st.button("💎 ANALYZE", key="analyze") and manual_ticker:
    try:
        with st.spinner(f"Loading {manual_ticker}..."):
            stock = yf.Ticker(manual_ticker)
            info = stock.info
            
            # SAFE METRICS
            price = info.get("regularMarketPrice", info.get("regularMarketPreviousClose", 0)) or 0
            pe = info.get("trailingPE", 999)
            pb = info.get("priceToBook", 999)
            roe = (info.get("returnOnEquity", 0) or 0) * 100
            debt_eq = info.get("debtToEquity", 999)
            
            # GRAHAM SCORE
            score = 0
            if pe < 15: score += 25
            elif pe < 25: score += 15
            if pb < 1.5: score += 25
            elif pb < 3: score += 15
            if roe > 12: score += 20
            if debt_eq < 50: score += 15
            
            col1, col2, col3 = st.columns(3)
            col1.metric("**Price**", f"${price:.2f}", "live")
            col2.metric("**Graham Score**", f"{score}/100", "value metrics")
            col3.metric("**Target Upside**", f"{max((15/pe)*100-100,0):+.0f}%", "if PE=15")
            
            # METRICS DISPLAY
            st.metric("P/E", f"{pe:.1f}", "<15=optimal")
            st.metric("P/B", f"{pb:.1f}", "<1.5=optimal")
            st.metric("ROE", f"{roe:.1f}%")
            st.metric("Debt/Eq", f"{debt_eq:.0f}", "<50=safe")
            
            # RATING
            if score > 70:
                st.success(f"🟢 **STRONG BUY** {score}/100 | {manual_ticker}")
            elif score > 50:
                st.warning(f"🟡 **Fair** {score}/100 | {manual_ticker}")
            else:
                st.error(f"🔴 **Overvalued** {score}/100 | {manual_ticker}")
            
            # CHART
            col1, col2 = st.columns([1,4])
            hist = stock.history(period="6mo")
            if not hist.empty:
                fig = px.line(hist.reset_index(), x="Date", y="Close", 
                            title=f"{manual_ticker} 6mo | Score: {score}/100")
                fig.add_hline(y=price*0.85, line_dash="dash", 
                            line_color="green", annotation_text="Buy Zone")
                fig.update_layout(height=350, showlegend=False)
                with col2:
                    st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed: {str(e)[:100]}")
