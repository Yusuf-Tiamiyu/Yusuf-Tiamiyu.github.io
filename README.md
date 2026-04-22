# Yusuf Tiamiyu — Data Analyst Portfolio

**Data Analyst · Cerba Lancet Nigeria · Lagos**

Live portfolio: [yusuftiamiyu.github.io](https://yusuf-tiamiyu.github.io) *(update with your actual URL)*

---

## About

Two years of data analytics experience in healthcare and clinical research. Based in Lagos, working at one of West Africa's leading diagnostic laboratory networks — where the numbers aren't abstract, they affect patient care.

This portfolio covers SQL data cleaning and exploration, Excel dashboard design, and a full-stack Flask web application built for real clinical use.

---

## Projects

| # | Project | Tools | Domain |
|---|---------|-------|--------|
| 01 | [TAT Dashboard Web App](#01-tat-dashboard-web-app) | Python, Flask, MySQL, HTML/JS | Healthcare Analytics |
| 02 | [Lab Operations Dashboard](#02-lab-operations-dashboard) | Excel, SUMIFS, Dynamic Filtering | Lab Operations |
| 03 | [Inventory Reorder Tracker](#03-inventory-reorder-tracker) | Excel, Conditional Logic | Supply Chain |
| 04 | [COVID-19 Data Exploration](#04-covid-19-data-exploration) | MS SQL Server, CTEs, Window Functions | Public Health |
| 05 | [World Layoffs Data Cleaning](#05-world-layoffs-data-cleaning) | MySQL, ROW_NUMBER, STR_TO_DATE | Data Engineering |
| 06 | [World Layoffs EDA](#06-world-layoffs-eda) | MySQL, DENSE_RANK, Rolling Totals | Exploratory Analysis |
| 07 | [Sales Estimates (Advanced SQL)](#07-sales-estimates-with-recursive-sql) | MySQL, Recursive CTEs, LAG/LEAD | Advanced SQL |

---

## Project Details

### 01. TAT Dashboard Web App
**Tools:** Python · Flask · MySQL · HTML/CSS/JS · Railway

A full-stack web application tracking laboratory Turnaround Time (TAT) performance in real time. Built entirely from scratch — database schema, REST API endpoints, and frontend UI — and deployed for actual operational use at Cerba Lancet Nigeria.

Key technical work:
- Designed a MySQL schema to store test entry timestamps and TAT outcomes
- Built a Python/Flask REST API with a type-safety layer handling all MySQL types (Decimal, datetime, bytes) to prevent JSON serialisation errors
- Frontend dashboard with filterable weekly views, KPI cards, and department breakdowns
- Deployed on Railway; used by lab supervisors for daily operational decisions

*Note: Company-identifying details and specific metrics have been anonymised for public display.*

---

### 02. Lab Operations Dashboard
**Tools:** Excel · SUMIFS · AVERAGEIFS · COUNTIFS · Dynamic Filtering

An Excel-based multi-site dashboard tracking four core KPIs: Total Tests Run, Unique Requisition Numbers, TAT % vs 90% target, and Staff Adequacy. All KPIs update dynamically based on filter selections (Year / Month / Week / Site / Department).

Key design decisions:
- Separate DASHBOARD, DATA ENTRY, PIVOT DATA, and SELECTIONS sheets — managers see results without touching raw data
- Week-over-week directional comparisons (▲/▼/►) auto-calculate for every KPI
- PIVOT DATA sheet holds all-time org-wide totals so main dashboard formulas only compute filtered views — keeps calculation fast at scale

*Note: Anonymised for public display.*

---

### 03. Inventory Reorder Tracker
**Tools:** Excel · SUMIFS · COUNTIFS · INDEX/MATCH · MAXIFS

A laboratory inventory management system tracking 100+ lab supplies. Automatically flags items below reorder threshold (REORDER NOW / OK), projects months of stock remaining at current usage rate, and provides a monthly issuance summary by department.

Key formula work:
- Status auto-flags: `=IF(CurrentQty<=ReorderLevel, "REORDER NOW", "OK")`
- Months of stock: `=ROUND(CurrentQty/AvgMonthlyUsage, 1)`
- Monthly summary uses SUMIFS + COUNTIFS + INDEX/MATCH/MAXIFS to pull issuance data by period without any manual refresh

*Note: Anonymised for public display.*

---

### 04. COVID-19 Data Exploration
**Tools:** MS SQL Server · Joins · CTEs · Temp Tables · Window Functions · Views

SQL exploration of the global COVID-19 dataset (deaths + vaccinations). Analysis covers death rates by country over time, infection rates as % of population, continental death counts, and rolling vaccination coverage computed with window functions.

Skills demonstrated: Joins, CTEs, temp tables, aggregate functions, window functions (SUM OVER PARTITION BY), CONVERT for type casting, CREATE VIEW for downstream visualisation.

---

### 05. World Layoffs Data Cleaning
**Tools:** MySQL · ROW_NUMBER · STR_TO_DATE · TRIM · Self-Join · Staging Tables

A four-phase SQL data cleaning pipeline on the Kaggle world layoffs dataset:
1. **Deduplication** — ROW_NUMBER OVER PARTITION to flag and remove exact duplicates via staging table
2. **Standardisation** — Consolidated Crypto/CryptoCurrency/Crypto Currency variants, stripped trailing periods from country names, converted text dates to proper DATE type with STR_TO_DATE
3. **Null handling** — Self-join to populate missing industry values from other rows of the same company where possible
4. **Dead weight removal** — Dropped rows where both total_laid_off and percentage_laid_off were null (no analytical value)

---

### 06. World Layoffs EDA
**Tools:** MySQL · DENSE_RANK · Rolling Window Functions · GROUP BY · CTEs

Exploratory analysis of the cleaned layoffs dataset. Key analyses:
- Companies that laid off 100% of staff, ranked by funding raised (Quibi: ~$2B raised, zero staff remaining)
- Top 3 companies by total layoffs per year using nested CTEs and DENSE_RANK
- Layoffs by industry, location, country, and funding stage
- Rolling monthly total of all layoffs from dataset start to end

---

### 07. Sales Estimates with Recursive SQL
**Tools:** MySQL · Recursive CTEs · UNION / UNION ALL · LAG · LEAD · COALESCE · CAST

A structured demonstration of 12 advanced SQL concepts in sequence, building from basic table creation through to intelligent gap-filling with window functions. The problem: a sales table with missing dates. The solution: a recursive CTE to generate a complete date series, left-joined to actual sales, with COALESCE + LAG/LEAD to estimate missing values using neighbouring data points.

---

## Skills Summary

**SQL:** MySQL · MS SQL Server · CTEs · Window Functions · Recursive CTEs · Joins · Subqueries · Aggregate Functions · Views · Temp Tables · Data Cleaning

**Excel:** SUMIFS · AVERAGEIFS · COUNTIFS · INDEX/MATCH · MAXIFS · Conditional Formatting · Dynamic Filtering · Dashboard Design · Pivot Tables

**Python:** Flask · REST APIs · MySQL Connector · Pandas · JSON handling

**Domain:** Healthcare Analytics · Clinical Research · Laboratory Operations · Supply Chain · Turnaround Time Analysis · KPI Design

---

## Contact

- **Email:** yusuf.tiamiyu@email.com *(update)*
- **LinkedIn:** [linkedin.com/in/yusuftiamiyu](https://linkedin.com/in/yusuftiamiyu) *(update)*
- **Location:** Lagos, Nigeria

---

*Data at Cerba Lancet Nigeria projects have been anonymised to remove company-identifying details, patient data, and specific operational metrics before public posting.*
