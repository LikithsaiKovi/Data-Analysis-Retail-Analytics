# 🛍️ Retail Analytics - Customer Segmentation & RFM Analysis

A complete data analytics project that analyzes online retail data to understand customer behavior, segment customers, and discover product relationships.

---

## 📊 What This Project Does

This project takes raw retail transaction data and:
1. **Cleans the data** - Removes errors, duplicates, and invalid records
2. **Segments customers** - Groups customers based on their purchasing behavior using RFM analysis
3. **Finds product relationships** - Discovers which products are often bought together
4. **Stores results in PostgreSQL** - Saves all findings in a database for easy access

---

## 🗂️ Project Structure

```
consumer360-retail-analytics/
├── data/
│   ├── raw/
│   │   └── OnlineRetail.csv          # Original retail transaction data
│   └── processed/
│       └── clean_retail_data.csv     # Cleaned and ready-to-use data
├── outputs/
│   ├── customer_rfm_segments.csv     # Customer segments and RFM scores
│   └── market_basket_rules.csv       # Product association rules
├── scripts/
│   ├── 01_data_cleaning.py           # Step 1: Clean raw data
│   ├── 02_rfm_analysis.py            # Step 2: Customer segmentation
│   ├── 03_market_basket.py           # Step 3: Market basket analysis
│   └── 04_load_to_postgres.py        # Step 4: Load to PostgreSQL
└── README.md
```

---

## 🚀 Step-by-Step Process

### **Step 1: Data Cleaning** (`01_data_cleaning.py`)

**What it does:**
- Loads the raw retail data from CSV file
- Removes records with missing customer information
- Removes cancelled orders (Invoice numbers starting with 'C')
- Removes invalid transactions (negative quantities or prices)
- Converts dates to proper format
- Creates a new column for total sales amount (Quantity × Price)

**Input:** `data/raw/OnlineRetail.csv`  
**Output:** `data/processed/clean_retail_data.csv`

**Why:** Raw data always has errors. We need clean data for accurate analysis.

---

### **Step 2: RFM Analysis** (`02_rfm_analysis.py`)

**What it does:**
RFM stands for:
- **R**ecency: How recently did the customer make a purchase?
- **F**requency: How often do they buy?
- **M**onetary: How much money do they spend?

The script:
1. Calculates these 3 metrics for each customer
2. Scores each metric on a scale of 1-5 (5 being the best)
3. Creates customer segments:
   - **Champions** (555-544): Best customers - buy often, recently, and spend a lot
   - **Loyal Customers** (444-333): Regular customers who keep coming back
   - **Potential Loyalists** (333-222): Good customers with growth potential
   - **Churn Risk** (<222): Customers who might stop buying

**Input:** `data/processed/clean_retail_data.csv`  
**Output:** `outputs/customer_rfm_segments.csv`

**Why:** Helps you understand which customers are valuable and which need attention.

---

### **Step 3: Market Basket Analysis** (`03_market_basket.py`)

**What it does:**
- Finds patterns in what products are bought together
- Uses the Apriori algorithm to discover associations
- Calculates metrics like:
  - **Support**: How often items appear together
  - **Confidence**: How likely item B is bought when item A is bought
  - **Lift**: How much more likely items are bought together vs. separately

**Input:** `data/processed/clean_retail_data.csv`  
**Output:** `outputs/market_basket_rules.csv`

**Why:** Helps with product placement, bundling, and cross-selling strategies.

---

### **Step 4: Load to PostgreSQL** (`04_load_to_postgres.py`)

**What it does:**
- Connects to your PostgreSQL database
- Creates three tables:
  - `transactions`: All cleaned transaction records
  - `customer_segments`: Customer RFM scores and segments
  - `market_basket_rules`: Product association rules
- Loads all the data into these tables

**Input:** All CSV files from previous steps  
**Output:** Data stored in PostgreSQL database

**Why:** A database makes it easy to query, filter, and analyze data using SQL. You can also connect it to visualization tools like Power BI or Tableau.

---

## 💻 How to Run the Project

### **Prerequisites**
1. Python 3.8 or higher
2. PostgreSQL database installed and running
3. Required Python packages (install using pip)

### **Installation**

```bash
# 1. Clone the repository
git clone https://github.com/LikithsaiKovi/Data-Analysis-Retail-Analytics.git
cd Data-Analysis-Retail-Analytics

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# 4. Install required packages
pip install pandas numpy mlxtend sqlalchemy psycopg2-binary
```

### **Running the Scripts**

Run the scripts in order:

```bash
# Step 1: Clean the data
python scripts/01_data_cleaning.py

# Step 2: Perform RFM analysis
python scripts/02_rfm_analysis.py

# Step 3: Market basket analysis
python scripts/03_market_basket.py

# Step 4: Load everything to PostgreSQL
python scripts/04_load_to_postgres.py
```

**Note:** Before running Step 4, make sure to:
- Update the database connection details in `04_load_to_postgres.py`
- Ensure PostgreSQL is running

---

## 📈 Key Insights You'll Get

1. **Customer Segments**: Know which customers are your champions and which are at risk of leaving
2. **Purchase Patterns**: Understand what products are frequently bought together
3. **Revenue Analysis**: See which customers contribute most to your revenue
4. **Marketing Strategy**: Target different customer segments with personalized campaigns

---

## 🛠️ Technologies Used

- **Python**: Main programming language
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **mlxtend**: Market basket analysis (Apriori algorithm)
- **SQLAlchemy**: Database connections
- **PostgreSQL**: Data storage and SQL queries

---

## 📝 Database Schema

### **transactions** table
- CustomerID
- InvoiceNo
- InvoiceDate
- StockCode
- Description
- Quantity
- UnitPrice
- SalesAmount
- Country

### **customer_segments** table
- CustomerID
- Recency (days since last purchase)
- Frequency (number of purchases)
- Monetary (total spending)
- R_Score, F_Score, M_Score
- RFM_Score (combined)
- Segment (Champions, Loyal, etc.)

### **market_basket_rules** table
- antecedents (products that trigger the rule)
- consequents (products bought together)
- support
- confidence
- lift

---

## 🎯 Use Cases

- **E-commerce**: Understand online shopping behavior
- **Retail Stores**: Optimize product placement
- **Marketing Teams**: Create targeted campaigns
- **Sales Teams**: Identify upselling opportunities
- **Business Analytics**: Make data-driven decisions

---

## 📧 Contact

**Likith Sai Kovi**  
GitHub: [@LikithsaiKovi](https://github.com/LikithsaiKovi)

---

## 📄 License

This project is open source and available for educational purposes.
