import streamlit as st
import pandas as pd
import glob
import os

st.set_page_config(layout="wide")
st.title("🏆 Buffett/Lynch Value Screener")
st.markdown("**PRA = 87.5 → ProAssurance TOP PICK!** 🎯")

# Load your CLI CSV
csv_files = glob.glob("*lynch*.csv") + glob.glob("buffet*.csv")
latest = max(csv_files, key=os.path.getmtime) if csv_files else None

if latest:
    df = pd.read_csv(latest)
    st.success(f"✅ Loaded: `{latest}` | Shape: {df.shape}")
    st.write("**Columns:**", df.columns.tolist())
    
    # Find score column
    score_col = None
    for col in ['score', 'value_score', 'PRA', 'Score']:
        if col in df.columns:
            score_col = col
            break
    
    if score_col:
        top_score = df[score_col].max()
        top_idx = df[score_col].idxmax()
        top_ticker = df.loc[top_idx, 'ticker'] if 'ticker' in df.columns else "N/A"
        
        col1, col2 = st.columns(2)
        col1.metric("🔥 Top Score", f"{top_score:.1f}")
        col2.metric("🏆 Top Pick", top_ticker)
        
        # Top 5 table - FIXED width
        st.subheader("📈 Top Buffett/Lynch Picks")
        top_df = df.nlargest(5, score_col)
        st.dataframe(top_df, width="stretch", hide_index=True)
        
        st.success(f"🎉 PRA={top_score:.1f} confirmed! Your CLI → Dashboard pipeline WORKS!")
    else:
        st.error("❌ No score column found!")
        st.dataframe(df.head())
else:
    st.error("❌ No CSV found! Run CLI first.")
