# Consumer360 – Retail Analytics  
## Handoff & Operations Document

---

## 1. Project Overview

Consumer360 is a retail analytics project designed to analyze customer behavior, revenue performance, retention trends, and customer segmentation using RFM analysis.

The project uses historical retail transaction data and provides business insights through interactive Power BI dashboards.

---

## 2. Data Source

- Source: Online Retail Transaction Dataset (CSV)
- Nature of data: Static / historical
- Updates: Manual (new CSV can be added if required)

---

## 3. Technology Stack

- **Python** – Data cleaning, transformation, and ETL
- **PostgreSQL** – Data storage and analytics layer
- **Power BI** – Dashboarding and visualization

---

## 4. Data Pipeline Flow

CSV File
↓
Python ETL Script
↓
PostgreSQL Tables & Views
↓
Power BI Dashboards



---

## 5. How to Run / Refresh the Pipeline

1. Place or update the raw CSV file in the data directory.
2. Run the Python pipeline script:
run_consumer360_pipeline.py

3. The script will:
- Clean the data
- Refresh PostgreSQL tables
- Rebuild analytical views and RFM tables
4. Open Power BI Desktop.
5. Click **Refresh** to load updated data.

---

## 6. Key Database Objects

### Fact Table
- `fact_sales` – Transaction-level sales data

### Analytical Views
- `customer_360` – Customer-level aggregation (frequency, monetary, last purchase)

### Segmentation Tables
- `rfm_segments` – Final RFM scores and customer segments

---

## 7. Dashboards

### Page 1: Retail Sales Dashboard
- Revenue KPIs
- Monthly revenue trends
- Country-wise revenue
- Cohort-based retention analysis

### Page 2: RFM Customer Segmentation Dashboard
- Customer segmentation (Champions, Loyal, At Risk, Churn Risk)
- Revenue contribution by segment
- Customer-level drill-down table

---

## 8. Re-run Safety

- PostgreSQL tables are refreshed before reload
- Views are recreated
- Pipeline is idempotent (safe to re-run multiple times)

---

## 9. Intended Business Use

- Executive performance tracking
- Customer retention analysis
- Marketing and CRM targeting
- Revenue and geography insights
