import logging
import pandas as pd
import numpy as np
from edgar import Company

logger = logging.getLogger(__name__)

def compute_value_metrics(company, filing=None):
    """SEC XBRL ROE extraction with full error handling"""
    try:
        if filing is None:
            filing = company.get_filings(form="10-Q").latest()
        xbrl = filing.xbrl()
        if xbrl is None:
            return None
            
        is_df = xbrl.statements.income_statement().to_dataframe()
        bs_df = xbrl.statements.balance_sheet().to_dataframe()
        
        # Robust period detection
        periods = []
        for col in is_df.columns:
            if isinstance(col, str) and '20' in col:
                periods.append(col)
        if not periods:
            logger.debug("No valid periods")
            return None
        latest_period = periods[-1]
        
        logger.debug(f"Using period: {latest_period}")
        
        # Safe NetIncome extraction
        net_candidates = is_df[is_df.concept.str.contains('NetIncome', na=False)]
        if net_candidates.empty:
            logger.debug("No NetIncome found")
            return None
        net_value = pd.to_numeric(net_candidates[latest_period], errors='coerce').dropna()
        if net_value.empty:
            logger.debug("No valid NetIncome values")
            return None
        net_income = float(net_value.iloc[-1])
        
        # Safe Equity extraction
        equity_candidates = bs_df[bs_df.concept.str.contains('StockholdersEquity', na=False)]
        if equity_candidates.empty:
            logger.debug("No StockholdersEquity found")
            return None
        equity_value = pd.to_numeric(equity_candidates[latest_period], errors='coerce').dropna()
        if equity_value.empty:
            logger.debug("No valid Equity values")
            return None
        equity = float(equity_value.iloc[-1])
        
        if equity == 0:
            logger.debug("Equity = 0")
            return None
            
        roe_pct = (net_income / equity * 100)
        logger.info(f"SEC XBRL ROE: {roe_pct:.1f}% net={net_income/1e9:.1f}B equity={equity/1e9:.1f}B")
        return {'roe_pct': roe_pct, 'source': 'SEC_XBRL'}
        
    except Exception as e:
        logger.debug(f"SEC skipped: {e}")
        return None
