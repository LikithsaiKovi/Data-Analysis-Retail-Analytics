# PostgreSQL Query Execution Guide

## Complete Step-by-Step PostgreSQL Workflow

This guide provides all PostgreSQL queries in the exact order they should be executed, including error resolutions and best practices.

---

## 📋 Prerequisites

Before starting, ensure:
- ✅ PostgreSQL is installed and running
- ✅ pgAdmin is installed (or use psql command line)
- ✅ All Python scripts (01-04) have been executed successfully
- ✅ You have PostgreSQL credentials ready

---

## 🗄️ STEP 1: Database Setup

### 1.1 Create Database

**Open pgAdmin or psql and run:**

```sql
-- Create the database
CREATE DATABASE retail_analytics;
```

**After creation, connect to this database for all subsequent queries.**

---

### 1.2 Verify Connection

```sql
-- Check current database
SELECT current_database();
```

**Expected Output:** `retail_analytics`

---

## 📊 STEP 2: Load Data (Using Python Script)

**🔴 CRITICAL: You MUST complete this step before proceeding to STEP 3 and beyond!**

### 2.1 Update Database Connection

First, open `scripts/04_load_to_postgres.py` and update the connection string:

```python
# Update these values with your PostgreSQL credentials
engine = create_engine('postgresql://username:password@localhost:5432/retail_analytics')

# Example:
# engine = create_engine('postgresql://postgres:mypassword@localhost:5432/retail_analytics')
```

### 2.2 Run the Python Script

**Make sure you're in the correct directory:**

```bash
# Navigate to project root
cd consumer360-retail-analytics

# Run the script
python scripts/04_load_to_postgres.py
```

**Expected Console Output:**
```
Loading transactions...
✅ Transactions loaded successfully: XXXXX rows
Loading customer segments...
✅ Customer segments loaded successfully: XXXX rows
Loading market basket rules...
✅ Market basket rules loaded successfully: XXX rows
```

**⚠️ If you see errors, check:**
- PostgreSQL is running
- Database connection credentials are correct
- You ran scripts 01, 02, and 03 first (to generate the CSV files)

This script will create and populate three tables:
- `transactions`
- `customer_segments`
- `market_basket_rules`

**❗ DO NOT proceed to STEP 3 until this completes successfully!**

---

## ✅ STEP 3: Verify Data Loading

**⚠️ STOP! Before running these queries:**

Make sure the Python script in STEP 2 completed successfully. If you get "relation does not exist" errors, go back to STEP 2.

### 3.1 Check All Tables

```sql
-- List all tables in the database
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

**Expected Output:**
```
table_name
-------------------------
transactions
customer_segments
market_basket_rules
```

**⚠️ If you DON'T see these 3 tables:**
- ❌ The Python script didn't run successfully
- ❌ Go back to STEP 2 and fix any errors
- ❌ Do NOT proceed to create views

---

### 3.2 Verify Row Counts

```sql
-- Count records in each table
SELECT 'transactions' AS table_name, COUNT(*) AS row_count FROM transactions
UNION ALL
SELECT 'customer_segments', COUNT(*) FROM customer_segments
UNION ALL
SELECT 'market_basket_rules', COUNT(*) FROM market_basket_rules;
```

**Expected Output:**
```
table_name           | row_count
---------------------|----------
transactions         | ~400000
customer_segments    | ~4000
market_basket_rules  | ~100
```

---

### 3.3 Preview Data

```sql
-- Preview transactions table
SELECT * FROM transactions LIMIT 5;

-- Preview customer segments
SELECT * FROM customer_segments LIMIT 5;

-- Preview market basket rules
SELECT * FROM market_basket_rules LIMIT 5;
```

---

## 📈 STEP 4: Create Analytical Views

**⚠️ PREREQUISITE CHECK:**

Before creating views, verify tables exist by running:

```sql
SELECT COUNT(*) FROM transactions;
SELECT COUNT(*) FROM customer_segments;
SELECT COUNT(*) FROM market_basket_rules;
```

**If you get "relation does not exist" error:**
- ❌ Tables are not loaded
- ❌ Go back to STEP 2 and run the Python script
- ❌ Verify script completes without errors

---

### 4.1 Create Customer 360 View

**Purpose:** Aggregate transaction data to customer level

```sql
CREATE OR REPLACE VIEW customer_360 AS
SELECT 
    "CustomerID",
    COUNT(DISTINCT "InvoiceNo") AS frequency,
    SUM("SalesAmount") AS monetary,
    MAX("InvoiceDate") AS last_purchase_date,
    MIN("InvoiceDate") AS first_purchase_date,
    COUNT(*) AS total_items_purchased
FROM transactions
GROUP BY "CustomerID";
```

**Verify the view:**

```sql
SELECT * FROM customer_360 LIMIT 10;
```

---

### 4.2 Create RFM Base View

**Purpose:** Calculate RFM metrics with snapshot date logic

```sql
CREATE OR REPLACE VIEW rfm_base AS
SELECT 
    "CustomerID",
    EXTRACT(DAY FROM ((SELECT MAX("InvoiceDate") FROM transactions) + INTERVAL '1 day') - last_purchase_date) AS recency,
    frequency,
    monetary
FROM customer_360;
```

**Verify the view:**

```sql
SELECT * FROM rfm_base LIMIT 10;
```

---

### 4.3 Create RFM Scores View

**Purpose:** Score customers on 1-5 scale using NTILE

```sql
CREATE OR REPLACE VIEW rfm_scores AS
SELECT 
    "CustomerID",
    recency,
    frequency,
    monetary,
    NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
FROM rfm_base;
```

**Verify the view:**

```sql
SELECT * FROM rfm_scores 
ORDER BY r_score DESC, f_score DESC, m_score DESC
LIMIT 10;
```

---

### 4.4 Create RFM Segments View

**Purpose:** Classify customers into business segments

```sql
CREATE OR REPLACE VIEW rfm_segments_view AS
SELECT 
    "CustomerID",
    r_score,
    f_score,
    m_score,
    recency,
    frequency,
    monetary,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score < 3 THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        ELSE 'Churn Risk'
    END AS segment
FROM rfm_scores;
```

**Verify the view:**

```sql
SELECT segment, COUNT(*) AS customer_count
FROM rfm_segments_view
GROUP BY segment
ORDER BY customer_count DESC;
```

---

## 🔍 STEP 5: Analytical Queries

### 5.1 Customer Segmentation Analysis

**Query 1: Count customers by segment**

```sql
SELECT 
    segment, 
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM customer_segments
GROUP BY segment
ORDER BY customer_count DESC;
```

---

**Query 2: Revenue by segment**

```sql
SELECT 
    cs.segment,
    COUNT(DISTINCT cs."CustomerID") AS customer_count,
    ROUND(SUM(t."SalesAmount")::NUMERIC, 2) AS total_revenue,
    ROUND(AVG(t."SalesAmount")::NUMERIC, 2) AS avg_transaction_value
FROM customer_segments cs
JOIN transactions t ON cs."CustomerID" = t."CustomerID"
GROUP BY cs.segment
ORDER BY total_revenue DESC;
```

---

**Query 3: Champions analysis**

```sql
SELECT 
    "CustomerID",
    "Recency" AS days_since_purchase,
    "Frequency" AS total_purchases,
    ROUND("Monetary"::NUMERIC, 2) AS total_spent
FROM customer_segments
WHERE "Segment" = 'Champions'
ORDER BY "Monetary" DESC
LIMIT 20;
```

⚠️ **IMPORTANT: Use single quotes for string values!**

**Common Error:**
```sql
-- ❌ WRONG - This will fail
WHERE segment = "Champions"

-- ✅ CORRECT - Use single quotes
WHERE "Segment" = 'Champions'
```

---

**Query 4: At Risk customers**

```sql
SELECT 
    "CustomerID",
    "Recency" AS days_since_purchase,
    "Frequency" AS total_purchases,
    ROUND("Monetary"::NUMERIC, 2) AS total_spent
FROM customer_segments
WHERE "Segment" = 'At Risk'
ORDER BY "Recency" DESC
LIMIT 20;
```

---

**Query 5: Churn Risk customers**

```sql
SELECT 
    "CustomerID",
    "Recency" AS days_since_purchase,
    "Frequency" AS total_purchases,
    ROUND("Monetary"::NUMERIC, 2) AS total_spent
FROM customer_segments
WHERE "Segment" = 'Churn Risk'
ORDER BY "Recency" DESC;
```

---

### 5.2 Transaction Analysis

**Query 6: Top 10 customers by revenue**

```sql
SELECT 
    "CustomerID",
    COUNT(DISTINCT "InvoiceNo") AS total_orders,
    SUM("Quantity") AS total_items,
    ROUND(SUM("SalesAmount")::NUMERIC, 2) AS total_revenue
FROM transactions
GROUP BY "CustomerID"
ORDER BY total_revenue DESC
LIMIT 10;
```

---

**Query 7: Monthly sales trend**

```sql
SELECT 
    TO_CHAR("InvoiceDate", 'YYYY-MM') AS month,
    COUNT(DISTINCT "InvoiceNo") AS total_orders,
    COUNT(DISTINCT "CustomerID") AS unique_customers,
    ROUND(SUM("SalesAmount")::NUMERIC, 2) AS monthly_revenue
FROM transactions
GROUP BY TO_CHAR("InvoiceDate", 'YYYY-MM')
ORDER BY month;
```

---

**Query 8: Top 10 products by revenue**

```sql
SELECT 
    "Description",
    COUNT(DISTINCT "InvoiceNo") AS times_purchased,
    SUM("Quantity") AS total_quantity_sold,
    ROUND(SUM("SalesAmount")::NUMERIC, 2) AS total_revenue
FROM transactions
WHERE "Description" IS NOT NULL
GROUP BY "Description"
ORDER BY total_revenue DESC
LIMIT 10;
```

---

**Query 9: Country-wise analysis**

```sql
SELECT 
    "Country",
    COUNT(DISTINCT "CustomerID") AS total_customers,
    COUNT(DISTINCT "InvoiceNo") AS total_orders,
    ROUND(SUM("SalesAmount")::NUMERIC, 2) AS total_revenue
FROM transactions
GROUP BY "Country"
ORDER BY total_revenue DESC
LIMIT 10;
```

---

### 5.3 Market Basket Analysis

**Query 10: Top 10 product associations**

```sql
SELECT 
    antecedents,
    consequents,
    ROUND(support::NUMERIC, 4) AS support,
    ROUND(confidence::NUMERIC, 4) AS confidence,
    ROUND(lift::NUMERIC, 2) AS lift
FROM market_basket_rules
ORDER BY lift DESC
LIMIT 10;
```

---

**Query 11: High confidence rules**

```sql
SELECT 
    antecedents AS "If Customer Buys",
    consequents AS "They Also Buy",
    ROUND(confidence::NUMERIC * 100, 2) AS "Confidence %",
    ROUND(lift::NUMERIC, 2) AS lift
FROM market_basket_rules
WHERE confidence > 0.5
ORDER BY confidence DESC
LIMIT 15;
```

---

### 5.4 Customer Behavior Analysis

**Query 12: Customer purchase frequency distribution**

```sql
SELECT 
    purchase_count,
    COUNT(*) AS num_customers
FROM (
    SELECT 
        "CustomerID",
        COUNT(DISTINCT "InvoiceNo") AS purchase_count
    FROM transactions
    GROUP BY "CustomerID"
) AS freq_dist
GROUP BY purchase_count
ORDER BY purchase_count;
```

---

**Query 13: Average order value by segment**

```sql
SELECT 
    cs."Segment",
    COUNT(DISTINCT t."InvoiceNo") AS total_orders,
    ROUND(AVG(order_value)::NUMERIC, 2) AS avg_order_value
FROM customer_segments cs
JOIN (
    SELECT 
        "CustomerID",
        "InvoiceNo",
        SUM("SalesAmount") AS order_value
    FROM transactions
    GROUP BY "CustomerID", "InvoiceNo"
) t ON cs."CustomerID" = t."CustomerID"
GROUP BY cs."Segment"
ORDER BY avg_order_value DESC;
```

---

**Query 14: Customer retention (repeat customers)**

```sql
SELECT 
    CASE 
        WHEN purchase_count = 1 THEN 'One-time'
        WHEN purchase_count BETWEEN 2 AND 5 THEN 'Occasional'
        WHEN purchase_count BETWEEN 6 AND 10 THEN 'Regular'
        ELSE 'Frequent'
    END AS customer_type,
    COUNT(*) AS num_customers,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM (
    SELECT 
        "CustomerID",
        COUNT(DISTINCT "InvoiceNo") AS purchase_count
    FROM transactions
    GROUP BY "CustomerID"
) AS customer_freq
GROUP BY customer_type
ORDER BY num_customers DESC;
```

---

## 🚨 Common Errors & Solutions

### Error 1: Relation "transactions" Does Not Exist

**Error Message:**
```
ERROR:  relation "transactions" does not exist
LINE 9: FROM transactions
```

**Cause:** You're trying to create views or run queries BEFORE loading data into PostgreSQL.

**Solution:**
1. ✅ **First**, run the Python script to load data:
   ```bash
   python scripts/04_load_to_postgres.py
   ```

2. ✅ **Then**, verify tables exist:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

3. ✅ **Only then** create views and run analytical queries

**Root Cause:** 
- You skipped STEP 2 (Python data loading)
- The Python script failed but you didn't notice
- You're connected to the wrong database

**Quick Check:**
```sql
-- Should return 3 tables
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public';
```

---

### Error 2: Column Does Not Exist

**Error Message:**
```
ERROR:  column "At Risk" does not exist
LINE 3: WHERE segment="At Risk";
```

**Cause:** Using double quotes for string values

**Solution:**
```sql
-- ❌ WRONG
WHERE segment = "At Risk"

-- ✅ CORRECT
WHERE "Segment" = 'At Risk'
```

**Remember:**
- Double quotes (`"`) = Column/table names (identifiers)
- Single quotes (`'`) = String values (literals)

---

### Error 3: Column Name Case Sensitivity

**Error Message:**
```
ERROR: column "customerid" does not exist
```

**Cause:** PostgreSQL is case-sensitive when using quotes

**Solution:**
```sql
-- If column was created as "CustomerID"
SELECT "CustomerID" FROM transactions;

-- Not: customerid or Customerid
```

---

### Error 4: Ambiguous Column Name

**Error Message:**
```
ERROR: column reference "CustomerID" is ambiguous
```

**Cause:** Column exists in multiple joined tables

**Solution:**
```sql
-- ❌ WRONG
SELECT CustomerID, segment
FROM customer_segments cs
JOIN transactions t ON cs.CustomerID = t.CustomerID;

-- ✅ CORRECT - Use table aliases
SELECT cs."CustomerID", cs."Segment"
FROM customer_segments cs
JOIN transactions t ON cs."CustomerID" = t."CustomerID";
```

---

### Error 5: View Already Exists

**Error Message:**
```
ERROR: relation "customer_360" already exists
```

**Solution:** Use `CREATE OR REPLACE VIEW` instead of `CREATE VIEW`

```sql
CREATE OR REPLACE VIEW customer_360 AS
SELECT ...;
```

---

## 📊 STEP 6: Export Data for Power BI

### Option 1: Direct Connection (Recommended)

Power BI can directly connect to PostgreSQL:
1. Open Power BI Desktop
2. Get Data → PostgreSQL Database
3. Enter: `Server: localhost`, `Database: retail_analytics`
4. Select tables: `transactions`, `customer_segments`, `market_basket_rules`

---

### Option 2: Export to CSV (Alternative)

```sql
-- Export customer segments
COPY customer_segments TO 'C:/temp/customer_segments_export.csv' 
WITH (FORMAT CSV, HEADER);

-- Export transaction summary
COPY (
    SELECT * FROM transactions LIMIT 10000
) TO 'C:/temp/transactions_sample.csv'
WITH (FORMAT CSV, HEADER);
```

---

## 🎯 Complete Execution Checklist

Use this checklist to ensure all steps are completed:

- [ ] **Step 1:** Database created (`retail_analytics`)
- [ ] **Step 2:** Python script executed (`04_load_to_postgres.py`)
- [ ] **Step 3:** All tables verified (3 tables present)
- [ ] **Step 4:** All views created (4 views: customer_360, rfm_base, rfm_scores, rfm_segments_view)
- [ ] **Step 5:** Analytical queries tested (at least 5 queries)
- [ ] **Step 6:** Power BI connected successfully

---

## 📖 Query Summary Table

| Step | Query Purpose | Key Output |
|------|--------------|------------|
| 3.1 | List tables | 3 tables: transactions, customer_segments, market_basket_rules |
| 3.2 | Count rows | ~400K transactions, ~4K customers, ~100 rules |
| 4.1 | Customer 360 view | Aggregated customer metrics |
| 4.2 | RFM base view | Recency, Frequency, Monetary values |
| 4.3 | RFM scores view | 1-5 scoring for each metric |
| 4.4 | RFM segments view | Customer segment classification |
| 5.1 | Segment distribution | Count and % by segment |
| 5.2 | Revenue by segment | Total and avg revenue per segment |
| 5.3 | Champions analysis | Top 20 champions |
| 5.10 | Product associations | Top 10 market basket rules |

---

## 🎓 Key Takeaways

1. **Always use single quotes** for string values in WHERE clauses
2. **Use double quotes** for column names (if they contain spaces or are case-sensitive)
3. **Create views** for reusable analytical queries
4. **Use NTILE()** for consistent scoring across customers
5. **Test queries incrementally** - verify each step before proceeding
6. **Document your queries** - add comments explaining business logic

---

**✅ Once all queries execute successfully, your PostgreSQL database is ready for Power BI visualization!**
