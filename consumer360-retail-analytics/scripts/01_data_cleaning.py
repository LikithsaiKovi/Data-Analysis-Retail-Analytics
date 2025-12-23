import pandas as pd

# Step 1: Load raw data
df = pd.read_csv("data/raw/OnlineRetail.csv", encoding="ISO-8859-1")

print("Initial Shape:", df.shape)

# Step 2: Basic inspection
print(df.head())
print(df.isnull().sum())

# Step 3: Remove missing CustomerID
df = df.dropna(subset=["CustomerID"])

# Step 4: Remove cancelled orders (InvoiceNo starting with 'C')
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

# Step 5: Remove negative or zero quantities
df = df[df["Quantity"] > 0]

# Step 6: Remove zero or negative prices
df = df[df["UnitPrice"] > 0]

# Step 7: Convert InvoiceDate to datetime
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Step 8: Create Sales Amount
df["SalesAmount"] = df["Quantity"] * df["UnitPrice"]

print("Cleaned Shape:", df.shape)

# Step 9: Save cleaned data
df.to_csv("data/processed/clean_retail_data.csv", index=False)

print("✅ Data cleaning completed and saved.")
