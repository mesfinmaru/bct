-- PostgreSQL schema + indexes for the unified financial transaction table.
-- Run once against the target database, then load the data from the ETL pipeline.

DROP TABLE IF EXISTS bank_transactions CASCADE;

CREATE TABLE bank_transactions (
    id BIGSERIAL PRIMARY KEY,
    source_dataset VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    description VARCHAR(100) NOT NULL DEFAULT 'Other',
    deposits NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    withdrawals NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    balance NUMERIC(15, 2) NOT NULL DEFAULT 0.00,

    CONSTRAINT chk_amount_non_negative CHECK (deposits >= 0 AND withdrawals >= 0),
    CONSTRAINT chk_balance_realistic CHECK (balance >= 0)
);

-- Composite/Bitmap-friendly covering indexes for the most common BI queries.
CREATE INDEX idx_bank_tx_date_desc_source
    ON bank_transactions (transaction_date, description, source_dataset);

CREATE INDEX idx_bank_tx_source
    ON bank_transactions (source_dataset);

CREATE INDEX idx_bank_tx_date
    ON bank_transactions (transaction_date);

CREATE INDEX idx_bank_tx_description
    ON bank_transactions (description);
