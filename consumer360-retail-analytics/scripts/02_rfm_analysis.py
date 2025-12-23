import pandas as pd

# Load cleaned data
df = pd.read_csv("data/processed/clean_retail_data.csv")
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Snapshot date
snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

# RFM calculation
rfm = df.groupby("CustomerID").agg({
    "InvoiceDate": lambda x: (snapshot_date - x.max()).days,
    "InvoiceNo": "nunique",
    "SalesAmount": "sum"
}).reset_index()

rfm.columns = ["CustomerID", "Recency", "Frequency", "Monetary"]

# RFM scoring
rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=False, duplicates='drop')
rfm["F_Score"] = pd.qcut(rfm["Frequency"], 5, labels=False, duplicates='drop')
rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=False, duplicates='drop')

# Reverse R_Score (lower recency = better) and normalize all to 1-5 scale
rfm["R_Score"] = 5 - rfm["R_Score"]
rfm["F_Score"] = rfm["F_Score"] + 1
rfm["M_Score"] = rfm["M_Score"] + 1

rfm["RFM_Score"] = (
    rfm["R_Score"].astype(str) +
    rfm["F_Score"].astype(str) +
    rfm["M_Score"].astype(str)
)

# Segmentation
def segment(row):
    if row["RFM_Score"] >= "444":
        return "Champions"
    elif row["RFM_Score"] >= "333":
        return "Loyal Customers"
    elif row["RFM_Score"] >= "222":
        return "Potential Loyalists"
    else:
        return "Churn Risk"

rfm["Segment"] = rfm.apply(segment, axis=1)

# Save output
rfm.to_csv("outputs/customer_rfm_segments.csv", index=False)

print("✅ RFM Analysis completed.")
