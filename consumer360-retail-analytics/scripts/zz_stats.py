import pandas as pd
from pathlib import Path

raw_path = Path("consumer360-retail-analytics/data/raw/OnlineRetail.csv")
clean_path = Path("consumer360-retail-analytics/data/processed/clean_retail_data.csv")

raw = pd.read_csv(raw_path, encoding="ISO-8859-1")
clean = pd.read_csv(clean_path)

# Basic stats on raw
raw_rows = len(raw)
raw_missing_customer = raw["CustomerID"].isna().sum()
raw_negative_qty = (raw["Quantity"] <= 0).sum()
raw_nonpositive_price = (raw["UnitPrice"] <= 0).sum()
raw_cancelled = raw["InvoiceNo"].astype(str).str.startswith("C").sum()

# Clean stats
clean_rows = len(clean)
removed_pct = round(100 * (raw_rows - clean_rows) / raw_rows, 2)

# Columns present in cleaned
clean_cols = list(clean.columns)

print("raw_rows:", raw_rows)
print("clean_rows:", clean_rows)
print("removed_pct:", removed_pct)
print("raw_missing_customer:", raw_missing_customer)
print("raw_negative_or_zero_qty:", raw_negative_qty)
print("raw_nonpositive_price:", raw_nonpositive_price)
print("raw_cancelled_invoices:", raw_cancelled)
print("clean_columns:", clean_cols[:12])
print("has_SalesAmount:", "SalesAmount" in clean_cols)

# Date range
raw["InvoiceDate"] = pd.to_datetime(raw["InvoiceDate"], errors='coerce')
clean["InvoiceDate"] = pd.to_datetime(clean["InvoiceDate"], errors='coerce')
print("raw_date_range:", raw["InvoiceDate"].min(), raw["InvoiceDate"].max())
print("clean_date_range:", clean["InvoiceDate"].min(), clean["InvoiceDate"].max())
