import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

def get_small_cap_tickers(tickers_file: str) -> list:
    """Load tickers from CSV or return samples."""
    path = Path(tickers_file)
    if path.exists():
        df = pd.read_csv(path)
        if "ticker" not in df.columns:
            logger.error("CSV missing 'ticker' column")
            return []
        tickers = (
            df["ticker"]
            .dropna()
            .astype(str)
            .str.upper()
            .str.strip()
            .unique()
            .tolist()
        )
        logger.info(f"Loaded {len(tickers)} tickers from {tickers_file}")
        return tickers
    logger.warning(f"No {tickers_file}; using sample tickers")
    return ["ENVX", "JOBY", "RKLB", "ACHR", "SLDP"]

def get_growth_estimate(ticker: str, api_key: str) -> float:
    """Get EPS growth from Alpha Vantage (fallback 0)."""
    if not api_key:
        return 0.0
    try:
        from alpha_vantage.fundamentaldata import FundamentalData
        fd = FundamentalData(key=api_key, output_format="pandas")
        earnings, _ = fd.get_earnings(ticker)
        if not earnings.empty and len(earnings) >= 4:
            growth = earnings["reportedEPS"].pct_change().tail(4).mean() * 100
            return float(growth)
    except Exception:
        pass
    return 0.0
