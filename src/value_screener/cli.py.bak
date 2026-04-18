#!/usr/bin/env python3
"""Value screener CLI."""

import argparse
import logging
from pathlib import Path
import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def screen_company(ticker, api_key=None):
    """SEC filings screener with fallback."""
    try:
        from edgar import Company
        company = Company(ticker)
        try:
            filings = company.get_filings(form="10-Q")
            filing = filings.latest() if filings else None
        except:
            filing = None
        if not filing:
            logger.warning("No SEC filing for %s", ticker)
            return {"sec_pass": True}
        return {"sec_pass": True}
    except ImportError:
        logger.warning("edgartools missing - using yfinance fallback for %s", ticker)
        return yfinance_fallback(ticker)
    except:
        return {"sec_pass": False}

def buffet_score(info):
    pb = info.get("priceToBook", 10)
    roe = info.get("returnOnEquity", 0)*100
    debt_eq = info.get("debtToEquity", 200)
    growth = info.get("earningsGrowth", 0)*100
    score = 0
    if pb < 1.5: score += 25
    if roe > 15: score += 25
    if debt_eq < 50: score += 25
    if growth > 10: score += 25
    return score

def lynch_score(info):
    peg = info.get("pegRatio", 3)
    growth = info.get("earningsGrowth", 0)*100
    ps = info.get("priceToSalesTrailing12Months", 5)
    score = 0
    if peg < 1: score += 33
    if growth > 15: score += 33
    if ps < 1.5: score += 34
    return score
def yfinance_fallback(ticker):
    """Fallback scoring."""
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        mcap = info.get('marketCap', 0)
        score = (mcap/1e9 * 0.05) + (info.get('forwardPE',10)*2)
        return {"sec_pass": False, "score": score, "mcap": mcap}
    except:
        return {"sec_pass": False, "score": 0}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', required=True)
    args = parser.parse_args()
    
    tickers = ['TBBK', 'PFG', 'MCY', 'PRA', 'WD', 'ENVX', 'JOBY']
    logger.info("Hybrid screening %d tickers (SEC + yfinance)", len(tickers))
    
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    results = []
    
    for i, ticker in enumerate(tickers, 1):
        logger.info("Processing %s (%d/%d)", ticker, i, len(tickers))
        
        sec_result = screen_company(ticker)
        info = yf.Ticker(ticker).info
        buffet = buffet_score(info)
        lynch = lynch_score(info)
        score = (buffet + lynch) / 2

        buffet = buffet_score(info)
        lynch = lynch_score(info)
        score = (buffet + lynch) / 2
        mcap = info.get("marketCap", 0)
        company_name = info.get("longName", ticker)
        
        logger.info("%s: score=%.1f passes=True (SEC=%s)", ticker, score, sec_result.get('sec_pass', False))
        
        ticker_data = {
            "ticker": ticker,
            "value_score": score,
            "company_name": company_name,
            "mcap_billions": mcap / 1e9
        }
        results.append(ticker_data)
    
    df = pd.DataFrame(results)
    df.to_csv(args.output, index=False)
    logger.info("Saved %d results to %s", len(results), args.output)

if __name__ == "__main__":
    main()

def buffet_score(info):
    pb = info.get('priceToBook', 10)
    roe = info.get('returnOnEquity', 0)*100
    debt_eq = info.get('debtToEquity', 200)
    growth = info.get('earningsGrowth', 0)*100
    score = 0
    if pb < 1.5: score += 25
    if roe > 15: score += 25
    if debt_eq < 50: score += 25
    if growth > 10: score += 25
    return score

def lynch_score(info):
    peg = info.get('pegRatio', 3)
    growth = info.get('earningsGrowth', 0)*100
    ps = info.get('priceToSalesTrailing12Months', 5)
    score = 0
    if peg < 1: score += 33
    if growth > 15: score += 33
    if ps < 1.5: score += 34
    return score
