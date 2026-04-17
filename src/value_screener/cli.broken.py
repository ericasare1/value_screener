#!/usr/bin/env python3
"""Complete SEC filings screener - single-threaded for reliability."""

import argparse
import logging
import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

def screen_company(ticker, api_key=None):
    """SEC filings screener with fallback."""
    try:
        from edgar import Company
    except ImportError:
        logger.warning("edgartools missing - using yfinance fallback for %s", ticker)
        return yfinance_fallback(ticker)
    
    try:
