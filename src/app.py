from pathlib import Path

import pandas as pd
from shiny import reactive
from shiny.express import input, render, ui
from utils.filter_sales import filter_sales
from utils.kpi_helpers import (
    format_delta_detail_with_value,
    format_yoy_tile,
)


DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "chocolate_sales_clean.csv"
)
sales_df = pd.read_csv(DATA_PATH)
sales_df["year"] = sales_df["year"].astype(int)

# Reactive function to filter sales data based on user input
@reactive.calc
def filtered_sales() -> pd.DataFrame:
    return filter_sales(
        sales_df=sales_df,
        start_year=input.start_year(),
        end_year=input.end_year(),
        country=input.country(),
        product=input.product(),
    )


# kpi_metrics
@reactive.calc
def kpi_metrics() -> dict:
    df = filtered_sales().copy()

    if df.shape[0] == 0:
        return {
            "total_revenue": 0.0,
            "avg_sales_per_tran": 0.0,
            "total_transactions": 0,
            "yoy_growth_rate": None,
            "revenue_delta_pct": None,
            "avg_sales_delta_pct": None,
            "transactions_delta_pct": None,
            "prev_revenue": None,
            "prev_avg_sales_per_tran": None,
            "prev_total_transactions": None,
            "prev_year_sales": None,
            "prev_year": int(input.end_year()) - 1,
        }

    # sales numeric safeguard
    if df["sales"].dtype == "object":
        df["sales"] = (
            df["sales"].astype(str).str.replace(r"[\$,]", "", regex=True).astype(float)
        )

    total_revenue = float(df["sales"].sum())
    avg_sales_per_tran = float(df["sales"].mean())
    total_transactions = int(df.shape[0])

    # YoY and KPI comparisons based on selected end_year vs end_year-1
    end_year = int(input.end_year())
    prev_year = end_year - 1

    current_year_df = df[df["year"] == end_year]
    previous_year_df = df[df["year"] == prev_year]

    current_revenue = float(current_year_df["sales"].sum())
    previous_revenue = float(previous_year_df["sales"].sum())

    current_avg_sales = (
        float(current_year_df["sales"].mean())
        if current_year_df.shape[0] > 0
        else 0.0
    )
    previous_avg_sales = (
        float(previous_year_df["sales"].mean())
        if previous_year_df.shape[0] > 0
        else 0.0
    )

    current_transactions = int(current_year_df.shape[0])
    previous_transactions = int(previous_year_df.shape[0])

    sales_by_year = df.groupby("year")["sales"].sum()
    if (
        (end_year in sales_by_year.index)
        and (prev_year in sales_by_year.index)
        and (sales_by_year.loc[prev_year] != 0)
    ):
        yoy_growth_rate = float(
            (sales_by_year.loc[end_year] - sales_by_year.loc[prev_year])
            / sales_by_year.loc[prev_year]
        )
    else:
        yoy_growth_rate = 0.0

    if previous_revenue != 0:
        revenue_delta_pct = (current_revenue - previous_revenue) / previous_revenue
    else:
        revenue_delta_pct = None

    if previous_avg_sales != 0:
        avg_sales_delta_pct = (
            current_avg_sales - previous_avg_sales
        ) / previous_avg_sales
    else:
        avg_sales_delta_pct = None

    if previous_transactions != 0:
        transactions_delta_pct = (
            current_transactions - previous_transactions
        ) / previous_transactions
    else:
        transactions_delta_pct = None

    return {
        "total_revenue": total_revenue,
        "avg_sales_per_tran": avg_sales_per_tran,
        "total_transactions": total_transactions,
        "yoy_growth_rate": yoy_growth_rate,
        "revenue_delta_pct": revenue_delta_pct,
        "avg_sales_delta_pct": avg_sales_delta_pct,
        "transactions_delta_pct": transactions_delta_pct,
        "prev_revenue": previous_revenue,
        "prev_avg_sales_per_tran": previous_avg_sales,
        "prev_total_transactions": previous_transactions,
        "prev_year_sales": previous_revenue,
        "prev_year": prev_year,
    }

#set the page title for the app
ui.page_opts(title="ChocoSales Analyser", fillable=True)

# add sidebar with filters
with ui.sidebar(title="Filters", open="desktop"):
    with ui.layout_columns(col_widths=[5, 5]):
        ui.input_select(
            "start_year",
            "Start Year",
            choices=["2022", "2023", "2024", "2025"],
            selected="2022"
        )
        ui.input_select(
            "end_year",
            "End Year",
            choices=["2022", "2023", "2024", "2025"],
            selected="2025"
        )
    ui.input_select(
        "country",
        "Country",
        choices=["All"] + sorted(sales_df["country"].dropna().unique().tolist()),
        selected="All"
    )
    ui.input_select(
        "product",
        "Product Category",
        choices=["All"] + sorted(sales_df["product"].dropna().unique().tolist()),
        selected="All"
    )

# Main content area
with ui.layout_columns(col_widths=[8, 4], class_="mb-0", fill=False):
    ui.h2("Chocolate Sales Analyser Dashboard", class_="mb-0")
    ui.tags.div(
        "Last updated: February 14, 2026",
        class_="text-end small pt-0"
    )

# Add statistics cards row
with ui.layout_columns(
    col_widths=[3, 3, 3, 3],
    class_="g-2 mt-0 pt-0",
    fill=False,
):
    @render.ui
    def out_total_revenue_tile():
        metrics = kpi_metrics()
        detail, detail_class = format_delta_detail_with_value(
            metrics["revenue_delta_pct"],
            metrics["prev_year"],
            metrics["prev_revenue"],
            "$",
        )
        return ui.value_box(
            title=ui.tags.div(
                "Total Sales Revenue (USD)",
                class_="fw-bold fs-5 text-white text-center mb-0",
            ),
            value=ui.TagList(
                ui.tags.div(
                    f"${metrics['total_revenue']:,.1f}",
                    class_="fs-3 fw-bold lh-1 text-white text-center",
                ),
                ui.tags.div(
                    detail,
                    class_=f"{detail_class} opacity-75",
                    style="font-size: 0.78rem;",
                ),
            ),
            style="background-color: #003c64; border-color: #003c64;",
            class_="h-100",
        )

    @render.ui
    def out_yoy_growth_rate():
        metrics = kpi_metrics()
        main_text, detail, detail_class, main_class = format_yoy_tile(
            metrics["yoy_growth_rate"],
            metrics["prev_year"],
            metrics["prev_year_sales"],
        )
        return ui.value_box(
            title=ui.tags.div(
                "Year Over Year Growth Rate (%)",
                class_="fw-bold fs-5 text-white text-center mb-0",
            ),
            value=ui.TagList(
                ui.tags.div(
                    main_text,
                    class_=f"fs-3 fw-bold lh-1 {main_class} text-center",
                ),
                ui.tags.div(
                    detail,
                    class_=f"{detail_class} opacity-75",
                    style="font-size: 0.78rem;",
                ),
            ),
            style="background-color: #003c64; border-color: #003c64;",
            class_="h-100",
        )

    @render.ui
    def out_avg_sales_per_tran_tile():
        metrics = kpi_metrics()
        detail, detail_class = format_delta_detail_with_value(
            metrics["avg_sales_delta_pct"],
            metrics["prev_year"],
            metrics["prev_avg_sales_per_tran"],
            "$",
        )
        return ui.value_box(
            title=ui.tags.div(
                "Average Sales Per Transaction (USD)",
                class_="fw-bold fs-5 text-white text-center mb-0",
            ),
            value=ui.TagList(
                ui.tags.div(
                    f"${metrics['avg_sales_per_tran']:,.1f}",
                    class_="fs-3 fw-bold lh-1 text-white text-center",
                ),
                ui.tags.div(
                    detail,
                    class_=f"{detail_class} opacity-75",
                    style="font-size: 0.78rem;",
                ),
            ),
            style="background-color: #003c64; border-color: #003c64;",
            class_="h-100",
        )

    @render.ui
    def out_total_transactions_tile():
        metrics = kpi_metrics()
        detail, detail_class = format_delta_detail_with_value(
            metrics["transactions_delta_pct"],
            metrics["prev_year"],
            metrics["prev_total_transactions"],
        )
        return ui.value_box(
            title=ui.tags.div(
                "Total Transaction (Count)",
                class_="fw-bold fs-5 text-white text-center mb-0",
            ),
            value=ui.TagList(
                ui.tags.div(
                    f"{metrics['total_transactions']:,}",
                    class_="fs-3 fw-bold lh-1 text-white text-center",
                ),
                ui.tags.div(
                    detail,
                    class_=f"{detail_class} opacity-75",
                    style="font-size: 0.78rem;",
                ),
            ),
            style="background-color: #003c64; border-color: #003c64;",
            class_="h-100",
        )
        
#Row 1 of Charts 
with ui.layout_columns(col_widths=[4,4,4]):
    with ui.card():
        ui.card_header("Year-over-Year Growth By Country")
        "Bar chart comparing YoY % change by country"

    with ui.card():
        ui.card_header("Sales Trend by Country Over Time")
        "Line chart showing sales over time, color-coded by country"
    
    with ui.card():
        ui.card_header("Countries and Regional Contribution Breakdown")
        "map showing sales by country"

# Row 2 of Chart and table
with ui.layout_columns(col_widths=[6,6]):
    with ui.card():
        ui.card_header("Countries Sales Contribution")
        "Interactive table with transaction details (Country, Top Sales Representative, Total Sales(USD), Percentage Contribution(%))"
    
    with ui.card():
        ui.card_header("Top 5 Products")
        "Horizontal bar chart of top-performing products by sales revenue"