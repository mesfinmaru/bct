-- PostgreSQL Schema for Unified Bank Transactions Table
-- Drop table if re-running
DROP TABLE IF EXISTS bank_transactions CASCADE;

-- Create Unified Table for Both Datasets
CREATE TABLE bank_transactions (
    id SERIAL PRIMARY KEY,
    source_dataset VARCHAR(50) NOT NULL, -- Tracks which file the row came from
    transaction_date DATE NOT NULL,
    description VARCHAR(100),
    deposits NUMERIC(15, 2) DEFAULT 0.00,
    withdrawals NUMERIC(15, 2) DEFAULT 0.00,
    balance NUMERIC(15, 2) DEFAULT 0.00
);

-- Performance Indexes for Large Dataset Querying (>2M records)
CREATE INDEX idx_all_tx_date ON bank_transactions(transaction_date);
CREATE INDEX idx_all_tx_desc ON bank_transactions(description);
CREATE INDEX idx_all_tx_source ON bank_transactions(source_dataset);