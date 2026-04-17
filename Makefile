.PHONY: install run test clean

install:
	rm -rf .venv
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install edgartools pandas numpy yfinance alpha-vantage pytest
	. .venv/bin/activate && pip install -e .

run:
	. .venv/bin/activate && vscreen --tickers_file data/smallcaps.csv --output output/results.csv

test:
	. .venv/bin/activate && pytest -q tests/

quick-test:
	. .venv/bin/activate && python -m value_screener.cli --help

clean:
	rm -rf .venv .pytest_cache __pycache__ */__pycache__ output/*.csv
