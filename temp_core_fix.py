from edgar import Company
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def compute_value_metrics(company, filing=None):
    try:
        if filing is None:
            filing = company.get_filings(form="10-Q").latest()
        xbrl = filing.xbrl()
        if xbrl is None:
            return None
            
        is_df = xbrl.statements.income_statement().to_dataframe()
        bs_df = xbrl.statements.balance_sheet().to_dataframe()
        
        periods = [col for col in is_df.columns if '20' in str(col)]
        if not periods:
            return None
        latest_period = periods[-1]
        
        net_row = is_df[is_df.concept.str.contains('NetIncome', na=False)]
        equity_row = bs_df[bs_df.concept.str.contains('StockholdersEquity', na=False)]
        
        if not net_row.empty and not equity_row.empty:
            roe_pct = (float(net_row[latest_period].iloc[0]) / float(equity_row[latest_period].iloc[0]) * 100)
            return {'roe_pct': roe_pct, 'source': 'SEC_XBRL'}
    except Exception as e:
        logger.warning(f'SEC XBRL failed: {e}')
    return None
