# Welcome to ChocoSales Analyser

ChocoSales Analyser is an interactive dashboard for exploring global chocolate sales data from 2022 to 2025 (dataset from [kaggle](https://www.kaggle.com/datasets/saidaminsaidaxmadov/chocolate-sales)).
The dashboard enables users to analyze sales trends, compare performance across countries and products, and evaluate individual sales representative contributions.
Through filtering, ranking, and visual comparison, the app supports data-driven decision-making for sales managers and business analysts.

## Get Started

Clone the repo and follow the steps below to run the dashboard locally:

```bash
git clone https://github.com/UBC-MDS/DSCI-532_2026_17_chocosales-analyser.git
cd DSCI-532_2026_17_chocosales-analyser/
```

### Create the Conda Environment

install the conda environment with:

```bash
conda env create -f environment.yml
conda activate chocosales-analyser
```

### Download the Dataset

For reproducibility, run the script in the terminal using:

```bash
python src/download_data.py
```

This will save the dataset to: `data/raw/`.

### Run the EDA Notebook (Milestone 1)

To explore the data cleaning steps and static visualizations created for the proposal, run:

```bash
jupyter lab
```

Then open `notebooks/eda_analysis.ipynb` and run all cells to reproduce the exploratory data analysis and static plots supporting our dashboard user story.

### Run the Dashboard Locally

```bash
shiny run --reload src/app.py
```
After running this command, open your browser and nagivate to: http://127.0.0.1:8000

## Contributors

- Chikire Aku-Ibe
- Samrawit Mezgebo Tsegay
- Shihan Xu

## Copyright

Copyright © 2026 Chikire Aku-Ibe, Samrawit Mezgebo Tsegay, Shihan Xu  
Distributed under the MIT [License](https://github.com/UBC-MDS/DSCI-532_2026_17_chocosales-analyser/blob/readme-eda/LICENSE).
