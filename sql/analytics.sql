-- Core KPIs: order counts are distinct transaction IDs, never line counts.
SELECT SUM(revenue) revenue, SUM(profit) profit, SUM(quantity) units,
 SUM(revenue)/NULLIF(COUNT(DISTINCT transaction_id),0) average_order_value,
 100*SUM(profit)/NULLIF(SUM(revenue),0) margin_pct FROM fact_sales;

-- Calendar spine includes zero-sales months; lag 12 therefore means last year.
WITH monthly AS (
 SELECT d.year, d.month, SUM(COALESCE(f.revenue,0)) revenue, SUM(COALESCE(f.profit,0)) profit
 FROM dim_date d LEFT JOIN fact_sales f USING(date_id) GROUP BY d.year,d.month
), previous AS (
 SELECT *, LAG(revenue) OVER(ORDER BY year,month) prior_month,
 LAG(revenue,12) OVER(ORDER BY year,month) prior_year FROM monthly
) SELECT *, 100*(revenue/NULLIF(prior_month,0)-1) mom_pct,
 100*(revenue/NULLIF(prior_year,0)-1) yoy_pct FROM previous;

SELECT product_id, product_name, SUM(revenue) revenue, SUM(profit) profit,
 100*SUM(profit)/NULLIF(SUM(revenue),0) margin_pct,
 DENSE_RANK() OVER(ORDER BY SUM(revenue) DESC) revenue_rank,
 DENSE_RANK() OVER(ORDER BY SUM(profit) DESC) profit_rank
FROM sales_detail GROUP BY product_id,product_name ORDER BY revenue DESC;

SELECT category, SUM(revenue) revenue, SUM(profit) profit FROM sales_detail GROUP BY category;
SELECT region, city, SUM(revenue) revenue, SUM(profit) profit FROM sales_detail GROUP BY region,city;
WITH periods AS (
 SELECT region, DATE_FORMAT(date,'%Y-%m') month, SUM(revenue) revenue
 FROM sales_detail GROUP BY region,DATE_FORMAT(date,'%Y-%m')
) SELECT *, LAG(revenue) OVER(PARTITION BY region ORDER BY month) previous_observed_month_revenue FROM periods;
WITH periods AS (
 SELECT product_id, DATE_FORMAT(date,'%Y-%m') month, SUM(revenue) revenue
 FROM sales_detail GROUP BY product_id,DATE_FORMAT(date,'%Y-%m')
) SELECT *, revenue/NULLIF(LAG(revenue) OVER(PARTITION BY product_id ORDER BY month),0)-1 observed_period_growth FROM periods;

SELECT customer_id, SUM(revenue) revenue, COUNT(DISTINCT transaction_id) frequency,
 SUM(revenue)/COUNT(DISTINCT transaction_id) average_order_value FROM fact_sales GROUP BY customer_id;
WITH customers AS (SELECT customer_id, COUNT(DISTINCT transaction_id) orders FROM fact_sales GROUP BY customer_id)
SELECT 100*AVG(orders>1) repeat_purchase_pct FROM customers;
SELECT campaign, discount, COUNT(*) lines, SUM(quantity) units, SUM(revenue) revenue,
 SUM(profit) profit, 100*SUM(profit)/NULLIF(SUM(revenue),0) margin_pct,
 AVG(quantity) units_per_line FROM sales_detail GROUP BY campaign,discount;
