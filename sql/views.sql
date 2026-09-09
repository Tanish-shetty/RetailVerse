CREATE OR REPLACE VIEW sales_detail AS
SELECT f.*, d.date, p.product_name, p.brand, p.category,
 l.store, l.city, l.state, l.region, m.campaign
FROM fact_sales f JOIN dim_date d USING(date_id)
JOIN dim_customer c USING(customer_id) JOIN dim_product p USING(product_id)
JOIN dim_location l USING(location_id) JOIN dim_promotion m USING(promotion_id);
