/*
Description: Create 2 tables and demo 12 advanced SQL concepts
*/
-- Create Schema "sales estimate"

-- create a sales table
CREATE TABLE sales 
(dt DATE, num_sales INT);

-- insert sales data into the table
INSERT INTO sales (dt, num_sales)
VALUES
    ('2025-01-01', 61),
    ('2025-01-02', 72),
    ('2025-01-04', 84),
    ('2025-01-05', 95),
    ('2025-01-07', 77);
    
-- create a final sales table
CREATE TABLE final_sales (
    dt DATE,
    num_sales INT
);

-- insert final sales data into the table
INSERT INTO final_sales (dt, num_sales)
VALUES
    ('2025-01-01', 61),
    ('2025-01-02', 72),
    ('2025-01-03', 78),
    ('2025-01-04', 84),
    ('2025-01-05', 95),
    ('2025-01-06', 86),
    ('2025-01-07', 77);

-- 1. view the table (note the missing dates)
SELECT * FROM sales;

-- 2. preview the final results
SELECT * FROM final_sales;
    
-- 3. generate a series of dates [UNION, UNION ALL]
SELECT '2025-01-01' AS dt
UNION
SELECT '2025-01-02'
UNION
SELECT '2025-01-03';

-- 4. join with our original table [Subquery, Left Join, Inner Join]
SELECT	sq.dt, sales.num_sales
FROM

(SELECT '2025-01-01' AS dt
UNION ALL
SELECT '2025-01-02'
UNION ALL
SELECT '2025-01-03'
UNION ALL
SELECT '2025-01-04'
UNION ALL
SELECT '2025-01-05'
UNION ALL
SELECT '2025-01-06'
UNION ALL
SELECT '2025-01-07') AS sq

LEFT JOIN sales 
	ON sq.dt = sales.dt;

-- 5. rewrite subquery as a CTE [CTE]
WITH cte AS (
			SELECT '2025-01-01' AS dt
			UNION ALL
			SELECT '2025-01-02'
			UNION ALL
			SELECT '2025-01-03'
			UNION ALL
			SELECT '2025-01-04'
			UNION ALL
			SELECT '2025-01-05'
			UNION ALL
			SELECT '2025-01-06'
			UNION ALL
			SELECT '2025-01-07'
)

SELECT cte.dt, sales.num_sales
FROM cte
LEFT JOIN sales 
	ON cte.dt = sales.dt;

-- 6. rewrite CTE as a recursive CTE [Recursive CTE, Date Expression, CAST Function]
WITH RECURSIVE cte AS ( SELECT CAST('2025-01-01' AS DATE) AS dt
						UNION ALL
						SELECT dt + INTERVAL 1 DAY
                        FROM cte
                        WHERE dt < CAST('2025-01-07' AS DATE)
)

SELECT	cte.dt, sales.num_sales
FROM cte
LEFT JOIN sales 
	ON cte.dt = sales.dt;

-- 7. fill in null values [NULL Function, Numeric Function]
WITH RECURSIVE cte AS ( SELECT CAST('2025-01-01' AS DATE) AS dt
						UNION ALL
						SELECT dt + INTERVAL 1 DAY
                        FROM cte
                        WHERE dt < CAST('2025-01-07' AS DATE)
)

SELECT	cte.dt, sales.num_sales,
        COALESCE(sales.num_sales, ROUND(
									(SELECT AVG(sales.num_sales)
                                    FROM sales)
										)
				) AS sales_estimate
FROM cte 
LEFT JOIN sales 
	ON cte.dt = sales.dt;

-- 8. introduce window functions [Window Functions]
SELECT	dt, num_sales,
		ROW_NUMBER() OVER() AS row_num,
        LAG(num_sales) OVER() AS prior_row,
        LEAD(num_sales) OVER() AS next_row
FROM	sales;

-- 9. add on two window functions [Final Query]
WITH RECURSIVE cte AS ( SELECT CAST('2025-01-01' AS DATE) AS dt
						UNION ALL
						SELECT dt + INTERVAL 1 DAY
                        FROM cte
                        WHERE dt < CAST('2025-01-07' AS DATE)
)

SELECT	cte.dt,
        COALESCE(sales.num_sales, ROUND(
									(LAG(sales.num_sales) OVER() + LEAD(sales.num_sales) OVER())/2)
				) AS sales_estimate
FROM cte 
LEFT JOIN sales 
	ON cte.dt = sales.dt;
