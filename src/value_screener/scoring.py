import numpy as np
import pandas as pd

def score_company(metrics: dict, pe: float, peg: float, eps_growth: float) -> float:
    """Compute Buffett/Lynch composite score (0-100)."""
    score_terms = [
        min(metrics.get("roe", np.nan), 30) * 2.5 if pd.notna(metrics.get("roe")) else 0,
        max(50 - (metrics.get("debt_to_equity", np.nan) * 20 if pd.notna(metrics.get("debt_to_equity")) else 0), 0),
        min(eps_growth, 25),
        20 / max(peg, 0.5),
        metrics.get("moat_proxy", 0) * 15,
        metrics.get("consistent_earnings", 0) * 10,
    ]
    return float(np.nansum(score_terms))
