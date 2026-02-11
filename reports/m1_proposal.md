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

> Mary is a policy maker with the Canadian Ministry of Health and she wants to understand what factors lead to missed appointments in order to devise an intervention that improves attendance numbers. She wants to be able to [explore] a dataset in order to [compare] the effect of different variables on absenteeism and [identify] the most relevant variables around which to frame her intervention policy.
>
> When Mary logs on to our "Missed Appointments app", she will see an overview of all the available variables in her dataset, according to the number of people that did or did not show up to their medical appointment. She can filter out variables for head-to-head comparisons, and explore which variables are most important in determining whether a patient will show up to their appointment. When she does so, Mary may e.g. notice that "physical disability" appears to be a strong predictor missing appointments, and in fact patients with a physical disability also have the largest number of missed appointments.
>
> Based on her findings from using our app, Mary hypothesizes that patients with a physical disability could be having a hard time finding transportation to their appointments, and decides she needs to conduct a follow-on study since transportation information is not captured in her current dataset.

### User Stories

*You can choose to frame your detailed requirements as User Stories...*

> **User Story 1:**
> As a **policy maker**, I want to **filter appointments by specific demographics (e.g., age, gender)** in order to **determine if specific population groups are disproportionately missing appointments**.
>
> **User Story 2:**
> As a **policy maker**, I want to **compare no-show rates between patients with and without specific conditions (e.g., hypertension)** in order to **identify if medical conditions are high-risk factors**.
>
> **User Story 3:**
> As a **policy maker**, I want to **visualize no-shows across days of the week** in order to **decide if specific days need scheduling interventions**.

### Jobs to Be Done

*...or as Jobs to Be Done:*

> **JTBD 1:**
> **Situation:** When I am reviewing monthly attendance reports...
> **Motivation:** ...I want to separate routine absences from systemic issues...
> **Outcome:** ...so I can allocate intervention budget to the right patient groups.
>
> **JTBD 2:**
> **Situation:** When investigating a spike in no-shows...
> **Motivation:** ...I want to see if specific physical disabilities correlate with absenteeism...
> **Outcome:** ...so I can propose targeted transportation support services.
>
> **JTBD 3:**
> **Situation:** When planning clinic hours...
> **Motivation:** ...I want to see if appointments on Mondays or Fridays are missed more often...
> **Outcome:** ...so I can optimize the scheduling grid.

## Section 4: Exploratory Data Analysis

> *To address User Story 1 (Demographics), we analyzed the no-show rate across different age groups.*
>
> **Analysis:** The bar chart in `notebooks/eda_analysis.ipynb` reveals that patients in the 20-30 age bracket have a 15% higher no-show rate than the average.
>
> **Reflection:** This finding supports the need for a targeted filter in the dashboard. By allowing the policy maker to isolate "Young Adults," they can investigate if this high trend holds true across different clinic locations, helping them decide if age-specific text message reminders are needed.

## Section 5: App Sketch & Description

![Dashboard](sketch.png "App Sketch")

> The app contains a landing page that shows the distribution (depending on data type, bar chart, density chart etc) of dataset factors (hypertension, physical disabilities etc.) colored coded according to whether patients showed up or didn't show up for an appointment. From a dropdown list, users can filter out variables from the distribution display, by patient demographics (i.e. only show female patients), by appointment data (i.e. if SMS was sent), and finally by the date range of appointments. A different dropdown menu will allow users to re-order variables according to the probability of patients being a no-show or in alphabetical order to co-morbidities. Users can compare the distribution of co-morbidities by scrolling down through the app interface.