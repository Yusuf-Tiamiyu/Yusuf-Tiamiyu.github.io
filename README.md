# Yusuf Tiamiyu — Data Analyst Portfolio

**Data Analyst · Cerba Lancet Nigeria · Lagos**

Live site: [yusuf-tiamiyu.github.io](https://yusuf-tiamiyu.github.io)

---

Two years doing data analytics in healthcare, specifically at one of West Africa's larger diagnostic lab networks. The numbers here aren't abstract — they connect to patient care, clinician decisions, and whether results reach doctors in time or don't.

This portfolio covers everything from a full five-stage data pipeline I built and deployed in production, to SQL data cleaning and exploration projects, Excel dashboards used in live operational settings, and a Tableau analysis. The work ranges from "I automated something that was costing people a full day every week" to "I wanted to understand this dataset properly, so here's what I found."

---

## Projects

| # | Project | Tools | Domain |
|---|---------|-------|--------|
| 01 | [TAT Dashboard — Full Pipeline](#01-tat-dashboard--full-pipeline) | Excel · Python · Pandas · Flask · MySQL · HTML/JS | Healthcare Analytics |
| 02 | [Lab Operations Dashboard](#02-lab-operations-dashboard) | Excel · SUMIFS · Dynamic Filtering | Lab Operations |
| 03 | [Inventory Reorder Tracker](#03-inventory-reorder-tracker) | Excel · Conditional Logic | Supply Chain |
| 04 | [COVID-19 Data Exploration](#04-covid-19-data-exploration) | MS SQL Server · CTEs · Window Functions | Public Health |
| 05 | [World Layoffs Data Cleaning](#05-world-layoffs-data-cleaning) | MySQL · ROW_NUMBER · STR_TO_DATE | Data Engineering |
| 06 | [World Layoffs EDA](#06-world-layoffs-eda) | MySQL · DENSE_RANK · Rolling Totals | Exploratory Analysis |
| 07 | [Sales Estimates — Advanced SQL](#07-sales-estimates--advanced-sql) | MySQL · Recursive CTEs · LAG/LEAD | Advanced SQL |
| 08 | [Bike Sales Dashboard](#08-bike-sales-dashboard) | Excel · Pivot Tables · Nested IF | Sales Analytics |
| 09 | [2016 Seattle Airbnb Analysis](#09-2016-seattle-airbnb-analysis) | Tableau · Data Joining · Geospatial | Property Analytics |

---

## Project Details

### 01. TAT Dashboard — Full Pipeline
**Tools:** Excel · Python · Pandas · Flask · MySQL · HTML/CSS/JS · Railway  
**Status:** Deployed and in daily clinical use  
*Data anonymised for public display*

TAT is Turnaround Time — the gap between when a lab sample is logged and when a verified result is ready for the requesting doctor. When I joined, the organisation's average TAT compliance was hovering between 50 and 55 percent across nine sites. Some sites were sitting at 40. The process for tracking it: download data from the LIS at the end of the week, manually organise it in Excel, email it around. By the time anyone read it, the problems it described were already five days old.

This project replaced that with a five-stage pipeline:

**Stage 1 — LIS Export and Excel Prep.** The Lab Information System exports a flat text file. I open it in Excel, use Text to Columns to separate the fields, then join the date and time columns (EntDate + EntTime, TestVerDate + TestVerTime) and convert them from the LIS text format to proper Excel datetimes using a formula: `=DATE(2000+MID(D2,7,2),MID(D2,4,2),LEFT(D2,2))+TIME(MID(D2,10,2),RIGHT(D2,2),0)`. Then deduplication, remove blanks, and the raw data is ready.

**Stage 2 — Reference_Times Sheet.** The original process had someone manually review the test name column to remove irrelevant entries and standardise naming. I replaced that with a master reference table I built and maintain: every valid test name, its standard TAT in hours, and its department. That last column — department — was something the organisation wasn't tracking at all before. Once it existed, failures could be traced to Chemistry or Haematology or Serology specifically, not just "Site X had a bad week."

**Stage 3 — Python Automation.** With the Reference_Times sheet as input, a Pandas script handles everything that was previously manual: filtering to known tests, VLOOKUP-style dict lookups for department and standard TAT, vectorised TAT calculation, Pass/Fail flagging, site name mapping from PerfSite codes, and a colour-coded Excel output with fail severity grading. What used to take a full working day now runs in about two minutes.

**Stage 4 — MySQL and Flask.** The Python script solved the speed problem but didn't solve the history problem. I designed a MySQL schema to store every record from every weekly upload, then built a Flask REST API with 13 endpoints covering weekly and monthly views, daily trend breakdowns, shift analysis, department drill-downs, and a failed requisition log. The frontend is plain HTML, CSS, and JavaScript. One thing I had to solve early: MySQL returns Decimal and datetime objects that Python's JSON encoder doesn't understand. I wrote a type-safety layer that converts every value before it touches `jsonify()`.

**Stage 5 — Deployed.** After approval from senior management, deployed on Railway. Lab supervisors check it during daily operational calls. The question shifted from "how did last week go" to "what is happening right now and where."

---

### 02. Lab Operations Dashboard
**Tools:** Excel · SUMIFS · AVERAGEIFS · COUNTIFS · Dynamic Filtering  
*Anonymised for public display*

An Excel dashboard for lab managers to track four core KPIs across all sites: total tests run, unique patient requisition numbers, TAT percentage against the 90% target, and staff adequacy. All four update instantly when you change any of the five filters (year, month, week, site, department).

Design choices: four sheets kept completely separate — DASHBOARD (what managers see), DATA ENTRY (where weekly records go), PIVOT DATA (all-time totals in the background), and SELECTIONS (the filter control). Every KPI card has an automatic week-over-week directional comparison. No manual calculations anywhere in the manager-facing view.

---

### 03. Inventory Reorder Tracker
**Tools:** Excel · SUMIFS · COUNTIFS · INDEX/MATCH · MAXIFS  
*Anonymised for public display*

A system for tracking 100+ lab supplies. The core logic: management policy requires a two-month stock buffer, so the reorder alert fires automatically when current quantity drops to the reorder level. The status column calculates itself — no manual input, no checking every row. There's also a months-of-stock-remaining projection and a monthly issuance log by department pulled via SUMIFS.

Before this, procurement was reactive — orders went out after stockout, not before. The system gave enough visibility to order in advance.

---

### 04. COVID-19 Data Exploration
**Tools:** MS SQL Server · Joins · CTEs · Temp Tables · Window Functions · Views

SQL exploration of the global COVID-19 dataset (deaths and vaccinations). The analysis covers death rates by country over time, infection rates as a percentage of population, continental death counts, and rolling vaccination totals computed with window functions. I also created a View so the results could be consumed downstream in Tableau without rerunning the query.

The finding I kept coming back to: countries with relatively low case counts sometimes had death rates that exceeded large, well-reported nations. The per-capita view tells a different story from the absolute totals.

---

### 05. World Layoffs Data Cleaning
**Tools:** MySQL · ROW_NUMBER · STR_TO_DATE · TRIM · Self-Join · Staging Tables

A four-phase cleaning pipeline on the Kaggle world layoffs dataset. I ran everything in a staging table so the raw data was never touched.

1. **Deduplication** — ROW_NUMBER OVER PARTITION to flag duplicates. MySQL doesn't let you DELETE directly from a CTE, so I copied to a second staging table with the row_num column included, deleted from there.
2. **Standardisation** — Three different spellings of "Crypto", trailing periods on country names, date fields stored as text in mm/dd/yyyy format. Fixed all of it.
3. **Null handling** — Self-join to populate missing industry values from other rows of the same company. This worked for almost everyone. Bally's had no other row to pull from and stayed null.
4. **Dead weight removal** — Rows where both total_laid_off and percentage_laid_off were null have no analytical value. Dropped.

---

### 06. World Layoffs EDA
**Tools:** MySQL · DENSE_RANK · Rolling Window Functions · GROUP BY · CTEs

Exploratory analysis built directly on the cleaned dataset from Project 05. I started with the extremes: companies that laid off 100% of their workforce, ordered by funding raised. Quibi raised roughly $2 billion and went to zero.

The harder analysis: top 3 companies by total layoffs per year. That requires two nested CTEs and DENSE_RANK. Then rolling monthly totals using SUM OVER ORDER BY to show cumulative momentum rather than just period-by-period numbers.

2022 was the worst year by a significant margin. The acceleration in the rolling total from mid-2022 is something you completely miss looking at monthly figures in isolation.

---

### 07. Sales Estimates — Advanced SQL
**Tools:** MySQL · Recursive CTEs · UNION / UNION ALL · LAG · LEAD · COALESCE · CAST

Started from a real frustration: generating a complete date series with UNION ALL means one line per date. For a full year that's 365 lines. I started reading about recursive CTEs, which let you define an anchor row and have the query call itself, adding one day per iteration until a termination condition fires.

The full project chains 12 SQL concepts in sequence, building from table creation through to intelligent gap-filling. The problem: a sales table with missing dates. The solution: recursive CTE generates the complete date range, left-joined to actual sales, with COALESCE + LAG/LEAD to fill gaps using neighbouring data points rather than a global average.

For the two missing dates in the sample dataset, the global average gives the same estimate for both. The LAG/LEAD approach gives different estimates for each, accounting for the trend visible in the surrounding data.

---

### 08. Bike Sales Dashboard
**Tools:** Excel · Pivot Tables · Nested IF · Slicers · COUNTIF · AVERAGEIF

Started from a tutorial dataset by Alex Freeberg. His version demonstrated the mechanics. I wanted to see what more careful analysis of the same data would surface.

After cleaning (26 duplicates removed, full word replacements for abbreviated columns, nested IF for age brackets), I built five purchase-rate analyses: by age bracket, by region, by commute distance, by gender, and by marital status.

The finding worth noting: the commute distance chart is not a straight line. Purchase rate dips at 1-2 miles, peaks at 2-5 miles (58.6%), then drops sharply. The 2-5 mile range is where a bike is genuinely useful for daily commuting. The gender analysis showed men and women buying at nearly identical rates, but male buyers average $4,350 more in income — so women are making this purchase at a meaningfully lower income level.

---

### 09. 2016 Seattle Airbnb Analysis
**Tools:** Tableau · Data Joining · Calendar Analysis · Geospatial Visualisation  
[View on Tableau Public](https://public.tableau.com/app/profile/yusuf.tiamiyu/viz/2016AirbnbDatasetSummary/Dashboard1)

Started from another Alex Freeberg tutorial, built my own version framed around a single question: if you were about to list a property on Airbnb in Seattle, what would the data tell you?

The dataset has 3,818 listings and over a million calendar rows. I joined Listings and Calendar in Tableau Public, excluded Reviews (not relevant to the question), and built a dashboard covering bedroom demand, pricing by location, monthly revenue seasonality, and room type split.

The most useful single finding: 1-bedroom listings dominate supply at 70% of all properties, but the jump from 1 to 2 bedrooms nearly doubles the average nightly rate from $96 to $174. The geographic pricing map shows central Seattle commanding a 70% premium over the dataset average. July is peak pricing. December is peak total revenue.

---

## Skills

**SQL:** MySQL · MS SQL Server · CTEs · Recursive CTEs · Window Functions · Joins · Subqueries · Aggregate Functions · Views · Staging Tables · Data Cleaning

**Excel:** SUMIFS · AVERAGEIFS · COUNTIFS · INDEX/MATCH · MAXIFS · Nested IF · Pivot Tables · Slicers · Dynamic Filtering · Dashboard Design · Conditional Formatting

**Python:** Flask · Pandas · REST APIs · MySQL Connector · NumPy · JSON handling · openpyxl

**BI Tools:** Tableau · Tableau Public · Dashboard Design · Geospatial Visualisation

**Domain:** Healthcare Analytics · Clinical Research · Lab Operations · Supply Chain · TAT Analysis · KPI Design

---

## Contact

- **Email:** tiamiyuyusufademola@gmail.com
- **LinkedIn:** [linkedin.com/in/yusuf-tiamiyu-demola](https://linkedin.com/in/yusuf-tiamiyu-demola)
- **Location:** Lagos, Nigeria

---

*All Cerba Lancet Nigeria projects have been anonymised. Patient data, site-identifying details, and specific operational metrics have been removed before public display.*
