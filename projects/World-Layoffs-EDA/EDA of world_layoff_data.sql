

SELECT *
FROM layoffs_staging2
WHERE company = 'Amazon'
;

SELECT MAX(total_laid_off)
FROM layoffs_staging2;

SELECT *
FROM layoffs_staging2
WHERE total_laid_off = 12000;
-- Looking at Percentage to see how big these layoffs were
SELECT MAX(percentage_laid_off)
FROM layoffs_staging2;

-- Which companies had 1 which is basically 100 percent of they company laid off

SELECT *
FROM layoffs_staging2
WHERE percentage_laid_off = 1
ORDER BY total_laid_off desc;

-- if we order by funds_raised_millions we can see how big some of these companies were
SELECT *
FROM layoffs_staging2
WHERE percentage_laid_off = 1
ORDER BY funds_raised_millions desc;

-- BritishVolt looks like an EV company, Quibi! I recognize that company - wow raised like 2 billion dollars and went under - ouch

-- SOMEWHAT TOUGHER AND MOSTLY USING GROUP BY--------------------------------------------------------------------------------------------------

-- Companies with the biggest single Layoff
SELECT company, total_laid_off
FROM layoffs_staging2
GROUP BY company, total_laid_off
ORDER BY total_laid_off desc;
-- now that's just on a single day

-- Companies with the most Total Layoffs
SELECT company, SUM(total_laid_off)
FROM layoffs_staging2
GROUP BY company
ORDER BY 2 desc
LIMIT 5
;

-- Layoffs by location & country
SELECT location, SUM(total_laid_off)
FROM layoffs_staging2
GROUP BY location
ORDER BY 2 desc
LIMIT 5
;

SELECT country, SUM(total_laid_off)
FROM layoffs_staging2
GROUP BY country
ORDER BY 2 desc
LIMIT 5
;

-- this it total in the past 3 years or in the dataset

-- total laid off per year
SELECT YEAR(`date`), SUM(total_laid_off) total_laid_off
FROM layoff_staging
WHERE YEAR(`date`) IS NOT NULL
GROUP BY YEAR(`date`)
ORDER BY 1
;
-- laid off per industry
SELECT industry, SUM(total_laid_off)
FROM layoff_staging
GROUP BY industry
ORDER BY 2 desc
;                 

-- stage of layoff
SELECT stage, SUM(total_laid_off)
FROM layoff_staging
GROUP BY stage
ORDER BY 2 desc
;


-- TOUGHER QUERIES------------------------------------------------------------------------------------------------------------------------------------

-- Earlier we looked at Companies with the most Layoffs. Now let's look at that per year. It's a little more difficult.
-- I want to look at For each year, which companies had the top 3 highest layoffs?”


WITH Company_Year AS 
(
  SELECT company, YEAR(`date`) AS years, SUM(total_laid_off) AS total_laid_off
  FROM layoffs_staging2
  GROUP BY company, YEAR(`date`)
)
, Company_Year_Rank AS (
  SELECT company, years, total_laid_off, DENSE_RANK() OVER (PARTITION BY years ORDER BY total_laid_off DESC) AS ranking
  FROM Company_Year
)
SELECT company, years, total_laid_off, ranking
FROM Company_Year_Rank
WHERE ranking <= 3
AND years IS NOT NULL
ORDER BY years ASC;


  SELECT company, YEAR(date) AS years, SUM(total_laid_off) AS total_laid_off
  FROM layoffs_staging2
  GROUP BY company, YEAR(date);

-- Rolling Total of Layoffs Per Year + Month
SELECT SUBSTRING(`date`,1,7) as dates, SUM(total_laid_off) AS total_laid_off
FROM layoffs_staging2
GROUP BY dates
ORDER BY dates ASC;
-- now use it in a CTE so we can query off of it
WITH DATE_CTE AS 
(
SELECT SUBSTRING(date,1,7) as dates, SUM(total_laid_off) AS total_laid_off
FROM layoffs_staging2
WHERE SUBSTRING(date,1,7)  IS NOT NULL
GROUP BY dates
ORDER BY dates ASC
)
SELECT dates, SUM(total_laid_off) OVER (ORDER BY dates ASC) as rolling_total_layoffs
FROM DATE_CTE
ORDER BY dates ASC;