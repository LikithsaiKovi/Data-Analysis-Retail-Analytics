import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# Load cleaned data
df = pd.read_csv("data/processed/clean_retail_data.csv")

# Create basket
basket = (
    df.groupby(["InvoiceNo", "Description"])["Quantity"]
    .sum().unstack().fillna(0)
)

# Convert to binary (bool type for better performance)
basket = basket.map(lambda x: x > 0)

# Apriori
frequent_items = apriori(basket, min_support=0.02, use_colnames=True)

rules = association_rules(
    frequent_items,
    metric="lift",
    min_threshold=1
)

# Save rules
rules.sort_values("lift", ascending=False).to_csv(
    "outputs/market_basket_rules.csv",
    index=False
)

print("✅ Market Basket Analysis completed.")
