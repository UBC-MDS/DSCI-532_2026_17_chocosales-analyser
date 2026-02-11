# Proposal Examples

These examples are provided to help you understand the expected depth and style of your proposal. You do not need to follow them exactly, but your sections should cover similar ground. Use the lecture materials to better motivate your proposal.

## Section 1: Motivation and Purpose

> **Our role:** Data scientist consultancy firm specializing in business analytics
> **Target audience:** Sales Managers and business analysts especially in the confectionery industry
>
> Global chocolate sales operations are bringing us substaintial volumes of transactional data across countries, products and individual sales representatives. However, managers mostly rely on those static reports or aggregated summaries, which makes it hard to understand what affects the performance and identify the growth opportunities. Without interactive exploration tools, it could be challenging to determine which region, products or individuals contribute most to revenue growth.
>
> To address this challenge, our goal is to build an interactive data visualization dashoard that enables sales managers to explore global chocolate sales performance from 2022 to 2025. Our app allows users to check total sales and the trend, compare performance across countries and products, also evaluate individual sales representatives through filtering, ranking and other time-based trend analysis. Users can interactively explore the dataset via our dashboard, make more informed strategic decisions related to resource allocation, product focus, and regional expansion based on this supportive tool.

## Section 2: Description of the Data

> We will be visualizing the **Chocolate Sales** dataset from Kaggle, which contains approximately 3,282 transaction records spanning the years 2022 to 2025. Each record represents a single chocolate sales transaction and includes several variables that describe the context and magnitude of the sale.
>
> The dataset includes the following key characteristics:
>
> - **Sales Representative Information** (`Sales Person`)
> The name of the salesperson responsible for the transaction, enabling performance comparison across individuals.
> - **Geographic Information** (`Country`)
> The country where the sale occurred, allowing for regional analysis and cross-country comparisons.
> - **Product Information** (`Product`)
> The name and type of chocolate product sold, which supports product-level performance evaluation.
> - **Temporal Information** (`Date`)
> The date of the transaction (DD/MM/YYYY format), enabling time-series trend analysis and year-over-year comparisons.
> - **Sales Metrics**
> `Amount`: Total sales value of the transaction (in USD).
> `Boxes Shipped`: Number of boxes shipped as part of the transaction.
> Using this data, we will derive additional variables to support exploratory analysis, such as:
> - Year and Month (extracted from Date) for trend visualization.
> - Year-over-Year Growth Metrics at aggregated levels.
> - Aggregated Sales per Country/Product/Sales Person to enable ranking and comparison.
> - Average Transaction Value to evaluate pricing and sales intensity.
> These variables directly support decision-making related to revenue growth, sales performance monitoring, and product strategy optimization.

## Section 3: Research Questions & Usage Scenarios

### Usage Scenario

> Jordan is a regional sales manager overseeing chocolate sales across multiple countries. Jordan is responsible for evaluating performance, identifying high-growth markets, and allocating sales resources effectively. However, reviewing static spreadsheets makes it difficult to quickly understand which segments are driving growth.
>
> When Jordan logs into our **ChocoSales Analyser** dashboard, they first see an overview of total sales and overall performance trends over time. Using interactive filters (Year, Country, Product), Jordan can explore specific segments of interest. For example, Jordan may filter the dashboard to view 2024 performance in Australia and observe that certain premium dark chocolate products contribute disproportionately to revenue.
>
> Jordan can then compare sales representatives to identify top performers and assess whether growth is concentrated among a few individuals or broadly distributed across the team. By exploring ranked product performance and year-over-year growth patterns, Jordan gains actionable insights to guide marketing focus, inventory decisions, and performance incentives.
>
> Based on findings from the dashboard, Jordan may decide to invest more resources in high-performing regions or provide additional support and training to underperforming areas.

### User Stories

> **User Story 1:**  
> As a **sales manager**, I want to **filter sales by year and country** in order to **compare regional performance and identify high-growth markets**.
>
> **User Story 2:**  
> As a **sales manager**, I want to **rank products by total sales or average transaction value** in order to **identify best-selling and most profitable chocolate products**.
>
> **User Story 3:**  
> As a **business analyst**, I want to **compare sales performance across sales representatives** in order to **identify top contributors and potential training opportunities**.

### Jobs to Be Done

> **JTBD 1:**
>
> - **Situation:** When I am reviewing quarterly sales reports...
> - **Motivation:** I want to understand which countries and products are driving overall revenue growth...
> - **Outcome:** So I can prioritize markets and adjust strategic planning accordingly.
>
> **JTBD 2:**
>
> - **Situation:** When I notice fluctuations in sales performance...
> - **Motivation:** I want to explore trends over time and compare year-over-year growth...
> - **Outcome:** So I can determine whether changes reflect seasonal patterns or structural shifts in demand.
>
> **JTBD 3:**
>
> - **Situation:** When evaluating team performance...
> - **Motivation:** I want to compare sales representatives across regions and products...
> - **Outcome:** So I can reward high performers and provide targeted support where needed.

## Section 4: Exploratory Data Analysis

> *To address User Story 1 (Demographics), we analyzed the no-show rate across different age groups.*
>
> **Analysis:** The bar chart in `notebooks/eda_analysis.ipynb` reveals that patients in the 20-30 age bracket have a 15% higher no-show rate than the average.
>
> **Reflection:** This finding supports the need for a targeted filter in the dashboard. By allowing the policy maker to isolate "Young Adults," they can investigate if this high trend holds true across different clinic locations, helping them decide if age-specific text message reminders are needed.

## Section 5: App Sketch & Description

![Dashboard](sketch.png "App Sketch")

> The app contains a landing page that shows the distribution (depending on data type, bar chart, density chart etc) of dataset factors (hypertension, physical disabilities etc.) colored coded according to whether patients showed up or didn't show up for an appointment. From a dropdown list, users can filter out variables from the distribution display, by patient demographics (i.e. only show female patients), by appointment data (i.e. if SMS was sent), and finally by the date range of appointments. A different dropdown menu will allow users to re-order variables according to the probability of patients being a no-show or in alphabetical order to co-morbidities. Users can compare the distribution of co-morbidities by scrolling down through the app interface.