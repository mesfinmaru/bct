# High-Volume Financial Transcations ETL Pipeline & Big Data Analytics

Modular and memory-efficient Python ETL (Extract, Transform, Load) pipeline designed to ingest, clean, validate, and load millions of financial banking ledger records into an optimized PostgreSQL relational database warehouse.

---

## 1. Project Overview & Business Scenario

### Business Problem
Modern financial institutions and auditing firms process millions of daily transactions containing mixed formats, missing values, and varying schema structures. Manual analysis or unoptimized scripts frequently lead to out-of-memory errors and data corruption. 

### Business Solution & Objectives
This project simply implements a robust, chunked data pipeline to ingest two massive banking transaction datasets (>1 million records each, exceeding 2 million total rows). The system standardizes raw ledger data, handles missing values, casts precise numeric data types, and loads them into a centralized PostgreSQL database equipped with indexing for high-performance business intelligence queries and anomaly detection.

---

## 2. System Architecture & Pipeline Workflow

The pipeline follows a strict **Extract $\rightarrow$ Transform $\rightarrow$ Load (ETL)** architectural pattern designed for scalability and low memory overhead:

```text
 [ Raw Datasets (>2M Rows) ] 
            │
            ▼ (Chunked Stream via Pandas: 50,000 rows/batch)
   [ Extraction Layer ] ──► (src/extract.py)
            │
            ▼
   [ Transformation Layer ] ──► (src/transform.py)
        • Drop exact duplicates
        • Standardize column headers
        • Handle null descriptions ('Other')
        • Parse and format transaction dates
        • Coerce numeric errors & fill defaults (0.00)
        • Append audit source tags
            │
            ▼
   [ Loading Layer (Batch to PostgreSQL) ] ──► (src/load.py & SQLAlchemy)
            │
            ▼
   [ Unified PostgreSQL Warehouse (`bank_transactions`) ]
            │
            ▼
   [ Performance Indexes & Verification Queries ]

3. Step-by-Step Setup & Execution Instructions
Step 1: Environment Setup
Ensure Python is installed, open your terminal inside the project root directory, and activate your virtual environment:

Bash
# Windows PowerShell
.venv\Scripts\Activate

Step 2: Install Dependencies
Install all required packages specified in requirements.txt:

Bash
pip install -r requirements.txt

Step 3: Configure Database Credentials
Create a .env file in the root directory and copy from .env.example template and fill with your existing credentials.

Step 4: Create Database Table & Indexes
Make sure installed postgreSQL in your device, Open pgAdmin 4, create a database named etl_db, open the Query Tool, and execute the SQL script stored in database/schema.sql.

Step 5: Place Your Datasets
Place your two raw CSV data files inside the data/raw/ directory and name them dataset_one.csv and dataset_two.csv (or update file references in src/pipeline.py).

Step 6: Run the ETL Pipeline
Execute the pipeline orchestration script:

Bash
python src/pipeline.py
