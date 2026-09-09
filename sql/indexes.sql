CREATE INDEX idx_sales_date_product ON fact_sales(date_id, product_id);
CREATE INDEX idx_sales_location_date ON fact_sales(location_id, date_id);
CREATE INDEX idx_sales_customer_order ON fact_sales(customer_id, transaction_id);
CREATE INDEX idx_product_category ON dim_product(category);
