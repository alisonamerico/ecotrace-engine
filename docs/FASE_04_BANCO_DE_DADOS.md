# FASE 04 — Banco de Dados

## 1. DDL PostgreSQL Completo

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE invoice_status AS ENUM ('PENDING', 'PROCESSING', 'APPROVED', 'REJECTED', 'FRAUD_SUSPECT');
CREATE TYPE credit_status AS ENUM ('AVAILABLE', 'RESERVED', 'COMPENSATED', 'CANCELLED');

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tracking_id UUID NOT NULL UNIQUE,
    access_key VARCHAR(44) NOT NULL,
    hash_sha256 VARCHAR(64) NOT NULL UNIQUE,
    issuer_cnpj VARCHAR(14) NOT NULL,
    recipient_cnpj VARCHAR(14) NOT NULL,
    status invoice_status NOT NULL DEFAULT 'PENDING',
    sefaz_status VARCHAR(50) NULL,
    rejection_reason TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_access_key_length CHECK (CHAR_LENGTH(access_key) = 44),
    CONSTRAINT chk_hash_sha256_length CHECK (CHAR_LENGTH(hash_sha256) = 64)
);

CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    item_number INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    ncm_code VARCHAR(8) NOT NULL,
    gross_weight_kg NUMERIC(12, 3) NOT NULL DEFAULT 0.000,
    is_eligible BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE recycling_credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL UNIQUE REFERENCES invoices(id) ON DELETE RESTRICT,
    credit_code VARCHAR(50) NOT NULL UNIQUE,
    material_family VARCHAR(50) NOT NULL,
    total_weight_kg NUMERIC(12, 3) NOT NULL,
    status credit_status NOT NULL DEFAULT 'AVAILABLE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);