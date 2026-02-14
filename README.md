# Welcome to ChocoSales Analyser

ChocoSales Analyser is an interactive dashboard for exploring global chocolate sales data from 2022 to 2025 (dataset from [kaggle](https://www.kaggle.com/datasets/saidaminsaidaxmadov/chocolate-sales)).
The dashboard enables users to analyze sales trends, compare performance across countries and products, and evaluate individual sales representative contributions.
Through filtering, ranking, and visual comparison, the app supports data-driven decision-making for sales managers and business analysts.

## Get Started

Clone the repo and follow the steps below to run the dashboard locally.

### Create the Conda Environment

install the conda environment with:

```bash
conda env create -f environment.yml
conda activate chocosales-analyser
```

### Download the Dataset

```bash
python src/download_data.py
```

This will save the dataset to: `data/raw/`.

### Run the Dashboard Locally

```bash
shiny run --reload src/app.py
```
