
-- 1. Total orders by status
SELECT status, COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY status;

-- 2. Completed revenue
SELECT ROUND(SUM(order_amount), 2) AS completed_revenue
FROM orders
WHERE status = 'completed';

-- 3. Revenue by product category
SELECT p.category,
       ROUND(SUM(o.order_amount), 2) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY p.category
ORDER BY revenue DESC;

-- 4. Top 10 customers by completed spending
SELECT c.customer_id,
       ROUND(SUM(o.order_amount), 2) AS total_spending
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.customer_id
ORDER BY total_spending DESC
LIMIT 10;

-- 5. Average delivery time by product category
SELECT p.category,
       ROUND(AVG(o.delivery_minutes), 2) AS avg_delivery_minutes
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY p.category
ORDER BY p.category;

-- 6. Monthly completed revenue
SELECT strftime('%Y-%m', order_ts) AS order_month,
       ROUND(SUM(order_amount), 2) AS monthly_revenue
FROM orders
WHERE status = 'completed'
GROUP BY order_month
ORDER BY order_month;

-- 7. Customer order frequency
SELECT customer_id,
       COUNT(*) AS completed_orders
FROM orders
WHERE status = 'completed'
GROUP BY customer_id
ORDER BY completed_orders DESC, customer_id
LIMIT 10;
