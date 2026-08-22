CREATE INDEX idx_invoices_hash_sha256 ON invoices USING hash (hash_sha256);
CREATE INDEX idx_invoices_tracking_id ON invoices (tracking_id);
CREATE INDEX idx_invoices_status_created_at ON invoices (status, created_at) WHERE status IN ('PENDING', 'PROCESSING');
CREATE INDEX idx_invoice_items_invoice_id ON invoice_items (invoice_id);
CREATE INDEX idx_recycling_credits_material_status ON recycling_credits (material_family, status);