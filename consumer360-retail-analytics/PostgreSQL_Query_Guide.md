# PostgreSQL Query Execution Guide (consumer360)

Aligned to the consumer360 database (public schema) and Schema_Review.md. This guide uses the canonical tables and views: dim_customer, dim_product, fact_sales, and the four RFM views.

---

## Prerequisites
- PostgreSQL running and reachable.
- Database `consumer360` exists (or create it below).
- Python scripts 01–04 have been run to generate CSVs; `04_load_to_postgres.py` is configured and used to load the schema.
- pgAdmin or psql available.

---

## 1) Database and Schema Setup

Create the database (if not already present):
```sql
CREATE DATABASE consumer360;
```

Confirm connection:
```sql
SELECT current_database();
-- Expect: consumer360
```

All objects live in schema `public`.

---

## 2) Objects That Must Exist (public)

Tables (5):
- dim_customer (customer_id PK, country)
- dim_customer_backup (customer_id, country)
- dim_product (product_id PK, product_name)
- dim_product_backup (product_id, product_name)
- fact_sales (invoice_no, customer_id FK, product_id FK, quantity, sales_amount, invoice_date, sale_id PK)

Views (4):
- customer_360 (customer_id, country, frequency, monetary, last_purchase_date)
- rfm_base (customer_id, country, recency, frequency, monetary)
- rfm_scores (customer_id, country, recency, frequency, monetary, r_score, f_score, m_score)
- rfm_segments (customer_id, country, recency, frequency, monetary, r_score, f_score, m_score, rfm_score, segment)

---

## 3) Load Data (Python step)

Update the connection string in `scripts/04_load_to_postgres.py` to point to `consumer360`, then run:
```bash
python scripts/04_load_to_postgres.py
```
This script creates tables, loads fact and dimensions, and builds the four views using the canonical SQL below. If anything fails, fix the script/config and rerun before proceeding.

---

## 4) Validate Objects

List tables and views:
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

Quick samples:
```sql
SELECT * FROM dim_customer  LIMIT 5;
SELECT * FROM dim_product   LIMIT 5;
SELECT * FROM fact_sales    LIMIT 5;
SELECT * FROM customer_360  LIMIT 5;
SELECT * FROM rfm_segments  LIMIT 5;
```

---

## 5) Canonical View Definitions (must match Schema_Review.md)

```sql
CREATE OR REPLACE VIEW customer_360 AS
SELECT fs.customer_id,
       dc.country,
       COUNT(DISTINCT fs.invoice_no) AS frequency,
       SUM(fs.sales_amount)          AS monetary,
       MAX(fs.invoice_date)          AS last_purchase_date
FROM fact_sales fs
LEFT JOIN dim_customer dc ON dc.customer_id = fs.customer_id
GROUP BY fs.customer_id, dc.country;

CREATE OR REPLACE VIEW rfm_base AS
SELECT c.customer_id,
       c.country,
       EXTRACT(DAY FROM ((SELECT MAX(invoice_date) FROM fact_sales) + INTERVAL '1 day' - c.last_purchase_date)) AS recency,
       c.frequency,
       c.monetary
FROM customer_360 c;

CREATE OR REPLACE VIEW rfm_scores AS
SELECT customer_id,
       country,
       recency,
       frequency,
       monetary,
       NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,
       NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
       NTILE(5) OVER (ORDER BY monetary ASC)  AS m_score
FROM rfm_base;

CREATE OR REPLACE VIEW rfm_segments AS
SELECT customer_id,
       country,
       recency,
       frequency,
       monetary,
       r_score,
       f_score,
       m_score,
       (r_score::TEXT || f_score::TEXT || m_score::TEXT) AS rfm_score,
       CASE 
         WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
         WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
         WHEN r_score >= 4 AND f_score < 3 THEN 'Potential Loyalists'
         WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
         ELSE 'Churn Risk'
       END AS segment
FROM rfm_scores;
```

---

## 6) Core Checks and Diagnostics

Row counts:
```sql
SELECT 'dim_customer' AS table_name, COUNT(*) AS row_count FROM dim_customer
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'fact_sales', COUNT(*) FROM fact_sales;
```

Top customers by revenue (from fact_sales):
```sql
SELECT customer_id,
       COUNT(DISTINCT invoice_no) AS orders,
       SUM(sales_amount) AS revenue,
       SUM(quantity) AS units
FROM fact_sales
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 10;
```

Segment distribution:
```sql
SELECT segment, COUNT(*) AS customers
FROM rfm_segments
GROUP BY segment
ORDER BY customers DESC;
```

Revenue by segment (using aggregates from rfm_segments):
```sql
SELECT segment,
       COUNT(*) AS customers,
       SUM(monetary) AS total_monetary,
       AVG(monetary) AS avg_monetary
FROM rfm_segments
GROUP BY segment
ORDER BY total_monetary DESC;
```

Recency distribution snapshot:
```sql
SELECT NTILE(5) OVER (ORDER BY recency) AS recency_bucket,
       COUNT(*) AS customers
FROM rfm_segments;
```

---

## 7) Best Practices and Notes
- Use single quotes for string literals (e.g., WHERE segment = 'Champions').
- Keep identifiers snake_case to avoid quoted identifiers.
- Do not create or reference tables named transactions or customer_segments; the canonical fact is fact_sales and segments come from rfm_segments.
- If the schema already exists, recreate only the views when adjusting logic; avoid dropping tables unless reloading data.

---

## 8) Quick Trouble Checklist
- Missing columns or mismatched names? Re-run the canonical view definitions above.
- Missing country in views? Ensure the joins to dim_customer remain and views are recreated.
- Wrong database? SELECT current_database(); should return consumer360.
- Use Schema_Review.md as the authoritative reference; keep this guide and the README in sync with it.
