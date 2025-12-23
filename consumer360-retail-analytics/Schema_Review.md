# Consumer360 PostgreSQL Schema Review (Matches Screenshots)

Authoritative reference based on the provided pgAdmin screenshots. Use this as a checklist for reviewers and for validating the README examples.

---

## 1) Database, Schema, and Objects

- Database: `consumer360`
- Schema: `public`
- Tables (5):
  - `dim_customer`
  - `dim_customer_backup`
  - `dim_product`
  - `dim_product_backup`
  - `fact_sales`
- Views (4):
  - `customer_360`
  - `rfm_base`
  - `rfm_scores`
  - `rfm_segments`

---

## 2) Table Definitions (Columns Must Match Exactly)

### dim_customer
- `customer_id` VARCHAR (PK)
- `country` VARCHAR

### dim_customer_backup
- `customer_id` VARCHAR
- `country` VARCHAR

### dim_product
- `product_id` VARCHAR (PK)
- `product_name` TEXT

### dim_product_backup
- `product_id` VARCHAR
- `product_name` TEXT

### fact_sales
- `invoice_no` VARCHAR
- `customer_id` VARCHAR (FK -> dim_customer.customer_id)
- `product_id` VARCHAR (FK -> dim_product.product_id)
- `quantity` INTEGER
- `sales_amount` NUMERIC(12,2)
- `invoice_date` TIMESTAMP
- `sale_id` BIGSERIAL (PK)

Notes:
- Column order in pgAdmin shows `invoice_no ... sale_id`; any DDL should include all columns above.

---

## 3) View Columns (Must Match Exactly)

### customer_360
- `customer_id`
- `country`
- `frequency`
- `monetary`
- `last_purchase_date`

### rfm_base
- `customer_id`
- `country`
- `recency`
- `frequency`
- `monetary`

### rfm_scores
- `customer_id`
- `country`
- `recency`
- `frequency`
- `monetary`
- `r_score`
- `f_score`
- `m_score`

### rfm_segments
- `customer_id`
- `country`
- `recency`
- `frequency`
- `monetary`
- `r_score`
- `f_score`
- `m_score`
- `rfm_score`
- `segment`

---

## 4) Canonical SQL (Matches Screenshots)

### customer_360
```sql
CREATE OR REPLACE VIEW customer_360 AS
SELECT 
  fs.customer_id,
  dc.country,
  COUNT(DISTINCT fs.invoice_no) AS frequency,
  SUM(fs.sales_amount)          AS monetary,
  MAX(fs.invoice_date)          AS last_purchase_date
FROM fact_sales fs
LEFT JOIN dim_customer dc ON dc.customer_id = fs.customer_id
GROUP BY fs.customer_id, dc.country;
```

### rfm_base
```sql
CREATE OR REPLACE VIEW rfm_base AS
SELECT 
  c.customer_id,
  c.country,
  EXTRACT(DAY FROM ((SELECT MAX(invoice_date) FROM fact_sales) + INTERVAL '1 day' - c.last_purchase_date)) AS recency,
  c.frequency,
  c.monetary
FROM customer_360 c;
```

### rfm_scores
```sql
CREATE OR REPLACE VIEW rfm_scores AS
SELECT 
  customer_id,
  country,
  recency,
  frequency,
  monetary,
  NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,
  NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
  NTILE(5) OVER (ORDER BY monetary ASC)  AS m_score
FROM rfm_base;
```

### rfm_segments
```sql
CREATE OR REPLACE VIEW rfm_segments AS
SELECT 
  customer_id,
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

## 5) Common Mistakes to Avoid (Found and Fixed)

- Using `transactions` or `customer_segments` tables (do not exist in screenshots). Use `fact_sales` and RFM views instead.
- Missing `country` in views. All four views include `country`.
- Mixed case/quoted identifiers causing confusion. Use snake_case consistently as above.
- Using double quotes for string literals (e.g., WHERE segment="At Risk"). Use single quotes.

---

## 6) Verification Queries

```sql
-- Objects present
SELECT table_name FROM information_schema.tables WHERE table_schema='public';

-- Sample rows for each view
SELECT * FROM customer_360 LIMIT 5;
SELECT * FROM rfm_base LIMIT 5;
SELECT * FROM rfm_scores LIMIT 5;
SELECT * FROM rfm_segments LIMIT 5;
```

This document is the source of truth for reviewers to confirm the implemented schema matches the screenshots.
