import pandas as pd
from sqlalchemy import create_engine

# Load cleaned data
df = pd.read_csv("data/processed/clean_retail_data.csv")

# PostgreSQL connection
engine = create_engine(
    "postgresql+psycopg2://postgres:7232@localhost:5432/consumer360"
)

# =========================
# Create Dimension Tables
# =========================

df_customers = df[["CustomerID", "Country"]].drop_duplicates()
df_customers.columns = ["customer_id", "country"]

df_products = df[["StockCode", "Description"]].drop_duplicates()
df_products.columns = ["product_id", "product_name"]

# =========================
# Load to PostgreSQL
# =========================

df_customers.to_sql("dim_customer", engine, if_exists="replace", index=False)
df_products.to_sql("dim_product", engine, if_exists="replace", index=False)

# Fact table
df_facts = df[[
    "InvoiceNo",
    "CustomerID",
    "StockCode",
    "Quantity",
    "SalesAmount",
    "InvoiceDate"
]]

df_facts.columns = [
    "invoice_no",
    "customer_id",
    "product_id",
    "quantity",
    "sales_amount",
    "invoice_date"
]

df_facts.to_sql("fact_sales", engine, if_exists="replace", index=False)

print("✅ Data successfully loaded into PostgreSQL")
