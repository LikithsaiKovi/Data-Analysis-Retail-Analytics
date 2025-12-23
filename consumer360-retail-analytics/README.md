Retail Analytics — Customer Segmentation and RFM Analysis
=========================================================

End-to-end pipeline from raw online retail data to customer segments and market basket insights, loaded into PostgreSQL and ready for Power BI. This README is aligned to Schema_Review.md and the pgAdmin screenshots (consumer360 database, public schema).

Contents
- Data inputs and outputs
- Python workflow
- PostgreSQL schema (tables and views)
- How to run
- Power BI connection
- Validation queries

Data
- Raw: data/raw/OnlineRetail.csv (transactional, one row per item on an invoice).
- Cleaned: data/processed/clean_retail_data.csv.
- Outputs: outputs/customer_rfm_segments.csv, outputs/market_basket_rules.csv.

Python Workflow (scripts/)
1) 01_data_cleaning.py
- Drops rows with missing CustomerID.
- Removes cancelled invoices (InvoiceNo starts with C).
- Keeps only positive Quantity and UnitPrice; computes SalesAmount.
- Writes data/processed/clean_retail_data.csv.

2) 02_rfm_analysis.py
- Calculates Recency, Frequency, Monetary per CustomerID.
- Applies quantile scoring (1–5) to R, F, M; builds rfm_score and segment labels.
- Writes outputs/customer_rfm_segments.csv.

3) 03_market_basket.py
- Builds invoice-item matrix and runs Apriori to produce association rules (support, confidence, lift).
- Writes outputs/market_basket_rules.csv.

4) 04_load_to_postgres.py
- Creates star schema tables and optional backups.
- Loads dimensions, fact_sales, and creates analytical views customer_360, rfm_base, rfm_scores, rfm_segments.
- Update the connection string in this script before running.

PostgreSQL Schema (public)
- Tables (match pgAdmin):
  - dim_customer: customer_id (PK), country
  - dim_customer_backup: customer_id, country
  - dim_product: product_id (PK), product_name
  - dim_product_backup: product_id, product_name
  - fact_sales: invoice_no, customer_id (FK), product_id (FK), quantity, sales_amount, invoice_date, sale_id (PK)
- Views (match pgAdmin):
  - customer_360: customer_id, country, frequency, monetary, last_purchase_date
  - rfm_base: customer_id, country, recency, frequency, monetary
  - rfm_scores: customer_id, country, recency, frequency, monetary, r_score, f_score, m_score
  - rfm_segments: customer_id, country, recency, frequency, monetary, r_score, f_score, m_score, rfm_score, segment

Canonical View SQL (aligned to Schema_Review.md)
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

How to Run
```bash
# Clone
git clone https://github.com/LikithsaiKovi/Data-Analysis-Retail-Analytics.git
cd Data-Analysis-Retail-Analytics/consumer360-retail-analytics

# Virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install pandas numpy mlxtend sqlalchemy psycopg2-binary

# 1) Clean data
python scripts/01_data_cleaning.py

# 2) RFM metrics and segments
python scripts/02_rfm_analysis.py

# 3) Market basket analysis
python scripts/03_market_basket.py

# 4) Load to PostgreSQL (set connection string in the script first)
python scripts/04_load_to_postgres.py
```

Power BI Connection
- Get Data → PostgreSQL Database.
- Server: localhost (or your host). Database: consumer360.
- Load tables/views: dim_customer, dim_product, fact_sales, rfm_segments (and other views as needed).
- Build visuals: segment distribution, revenue by segment, recency/frequency/monetary trends, top product associations.

Validation Queries (pgAdmin)
```sql
-- Objects present
SELECT table_name FROM information_schema.tables WHERE table_schema='public';

-- Quick samples
SELECT * FROM dim_customer  LIMIT 5;
SELECT * FROM dim_product   LIMIT 5;
SELECT * FROM fact_sales    LIMIT 5;
SELECT * FROM customer_360  LIMIT 5;
SELECT * FROM rfm_segments  LIMIT 5;
```

Notes
- Schema_Review.md is the source of truth for columns and view logic; keep README synchronized with it.
- Use snake_case identifiers and single quotes for SQL string literals.
- If the schema already exists, drop and recreate views only; keep tables unless you intend to reload data.

