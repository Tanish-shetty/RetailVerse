-- MySQL 8.0.16+. Run against a dedicated retailiq database.
CREATE TABLE IF NOT EXISTS dim_customer (customer_id VARCHAR(64) PRIMARY KEY);
CREATE TABLE IF NOT EXISTS dim_product (
 product_id VARCHAR(64) PRIMARY KEY, product_name VARCHAR(255) NOT NULL,
 brand VARCHAR(128) NOT NULL, category VARCHAR(128) NOT NULL);
CREATE TABLE IF NOT EXISTS dim_location (
 location_id VARCHAR(64) PRIMARY KEY, store VARCHAR(128) NOT NULL,
 city VARCHAR(128) NOT NULL, state VARCHAR(128) NOT NULL, region VARCHAR(64) NOT NULL);
CREATE TABLE IF NOT EXISTS dim_promotion (
 promotion_id VARCHAR(64) PRIMARY KEY, campaign VARCHAR(128) NOT NULL);
CREATE TABLE IF NOT EXISTS dim_date (
 date_id INTEGER PRIMARY KEY, date DATE NOT NULL UNIQUE, day INTEGER NOT NULL,
 week INTEGER NOT NULL, month INTEGER NOT NULL, quarter INTEGER NOT NULL, year INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS fact_sales (
 line_id VARCHAR(64) PRIMARY KEY, transaction_id VARCHAR(64) NOT NULL,
 date_id INTEGER NOT NULL, customer_id VARCHAR(64) NOT NULL,
 product_id VARCHAR(64) NOT NULL, location_id VARCHAR(64) NOT NULL,
 promotion_id VARCHAR(64) NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0),
 unit_price DECIMAL(14,2) NOT NULL CHECK(unit_price >= 0),
 unit_cost DECIMAL(14,2) NOT NULL CHECK(unit_cost >= 0),
 discount DECIMAL(5,4) NOT NULL CHECK(discount BETWEEN 0 AND 1),
 revenue DECIMAL(16,2) NOT NULL, cost DECIMAL(16,2) NOT NULL, profit DECIMAL(16,2) NOT NULL,
 source VARCHAR(64) NOT NULL,
 FOREIGN KEY(date_id) REFERENCES dim_date(date_id),
 FOREIGN KEY(customer_id) REFERENCES dim_customer(customer_id),
 FOREIGN KEY(product_id) REFERENCES dim_product(product_id),
 FOREIGN KEY(location_id) REFERENCES dim_location(location_id),
 FOREIGN KEY(promotion_id) REFERENCES dim_promotion(promotion_id));
