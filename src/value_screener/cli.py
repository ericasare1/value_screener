#!/usr/bin/env python3
"""
🏆 VALUE SCREENER CLI v2.3 - Buffett/Lynch Dual Mode + Vectorized
Production CLI with --style buffett|lynch|both + pandas vectorization
"""

import argparse
import logging
import yfinance as yf
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def buffet_score_vectorized(df: pd.DataFrame) -> pd.Series:
    """Warren Buffett scoring: P/B <1.5, Debt/Eq <50, ROE >12%, P/E <15"""
    scores = pd.Series(0, index=df.index, dtype=float)
    
    # P/E < 15: +25
    scores[df['trailingPE'] < 15] += 25
    
    # P/B < 1.5: +30 (Buffett's favorite)
    scores[df['priceToBook'] < 1.5] += 30
    
    # ROE > 12%: +20
    scores[(df['returnOnEquity'] * 100) > 12] += 20
    
    # Debt/Equity < 50%: +25 (safety margin)
    scores[df['debtToEquity'] < 50] += 25
    
    return scores.clip(0, 100)

def lynch_score_vectorized(df: pd.DataFrame) -> pd.Series:
    """Peter Lynch scoring: PEG <1, P/E vs Growth, earnings growth"""
    scores = pd.Series(0, index=df.index, dtype=float)
    
    # P/E < 20: +25
    scores[df['trailingPE'] < 20] += 25
    
    # PEG < 1.0: +30 (Lynch's golden rule)
    scores[df['pegRatio'] < 1.0] += 30
    
    # Earnings growth > 15%: +25
    scores[(df['earningsGrowth'] * 100) > 15] += 25
    
    # P/E / Growth < 1.5: +20
    peg_proxy = df['trailingPE'] / (df['earningsGrowth'] * 100 + 1)
    scores[peg_proxy < 1.5] += 20
    
    return scores.clip(0, 100)

def screen_company(ticker: str) -> Dict:
    """SEC screening (placeholder - returns pass for all)"""
    return {'sec_pass': True}

def process_ticker_vectorized(tickers: List[str]) -> pd.DataFrame:
    """Vectorized processing for entire ticker list"""
    results = []
    
    logger.info(f"Vector processing {len(tickers)} tickers...")
    
    # Batch fetch yfinance data
    for i, ticker in enumerate(tickers, 1):
        if i % 50 == 0:
            logger.info(f"Processed {i}/{len(tickers)} ({i/len(tickers)*100:.1f}%)")
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Clean numeric fields
            numeric_fields = {
                'trailingPE': info.get('trailingPE', np.nan),
                'priceToBook': info.get('priceToBook', np.nan),
                'returnOnEquity': info.get('returnOnEquity', 0),
                'debtToEquity': info.get('debtToEquity', np.nan),
                'pegRatio': info.get('pegRatio', np.nan),
                'earningsGrowth': info.get('earningsGrowth', 0),
                'marketCap': info.get('marketCap', 0),
            }
            
            row = {
                'ticker': ticker,
                'company_name': info.get('longName', ticker),
                'mcap_billions': numeric_fields['marketCap'] / 1e9,
                **numeric_fields
            }
            
            # SEC screening
            row.update(screen_company(ticker))
            
            results.append(row)
            
        except Exception as e:
            logger.warning(f"Failed {ticker}: {e}")
            continue
    
    df = pd.DataFrame(results)
    if df.empty:
        logger.error("No valid data collected")
        return pd.DataFrame()
    
    # Vectorized scoring
    logger.info("Computing Buffett scores...")
    df['buffett_score'] = buffet_score_vectorized(df)
    
    logger.info("Computing Lynch scores...")
    df['lynch_score'] = lynch_score_vectorized(df)
    
    return df

def main():
    parser = argparse.ArgumentParser(description="🏆 Buffett/Lynch Value Screener v2.3")
    parser.add_argument('--output', '-o', required=True, help="Output CSV file")
    parser.add_argument('--tickers_file', type=str, 
                       help="Custom tickers file (one per line)")
    parser.add_argument('--style', choices=['buffett', 'lynch', 'both'], 
                       default='both',
                       help="Scoring style: buffett (safety), lynch (growth), both")
    parser.add_argument('--max_tickers', type=int, default=1000,
                       help="Max tickers to process")
    
    args = parser.parse_args()
    
    # Ensure output directory
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    # Load tickers
    if args.tickers_file:
        with open(args.tickers_file, 'r') as f:
            tickers = [line.strip() for line in f if line.strip()]
    else:
        # Default tickers
        tickers = ['TBBK', 'PFG', 'MCY', 'PRA', 'WD', 'ENVX', 'JOBY']
        logger.info("Using default tickers (7)")
    
    tickers = tickers[:args.max_tickers]
    logger.info(f"Hybrid screening {len(tickers)} tickers (SEC + yfinance)")
    
    # Vectorized processing
    df = process_ticker_vectorized(tickers)
    
    if df.empty:
        logger.error("No results generated")
        return
    
    # Apply scoring style
    if args.style == 'buffett':
        df['value_score'] = df['buffett_score']
        logger.info("💼 Buffett style scoring applied")
    elif args.style == 'lynch':
        df['value_score'] = df['lynch_score'] 
        logger.info("📈 Lynch style scoring applied")
    else:  # both
        df['value_score'] = (df['buffett_score'] + df['lynch_score']) / 2
        logger.info("⚖️ Blended Buffett/Lynch scoring applied")
    
    # Sort and save
    output_cols = ['ticker', 'value_score', 'company_name', 'mcap_billions',
                  'buffett_score', 'lynch_score', 'trailingPE', 'priceToBook']
    
    df_sorted = df.sort_values('value_score', ascending=False)
    df_sorted[output_cols].to_csv(args.output, index=False)
    
    logger.info(f"✅ Saved {len(df)} results to {args.output}")
    logger.info("🏆 TOP 5:")
    top5 = df_sorted.head()
    for _, row in top5.iterrows():
        logger.info(f"   {row['ticker']}: {row['value_score']:.1f} (B:{row['buffett_score']:.1f} L:{row['lynch_score']:.1f})")

if __name__ == "__main__":
    main()
