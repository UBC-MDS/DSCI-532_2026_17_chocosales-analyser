from pathlib import Path

import altair as alt
import pandas as pd
from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_altair
from vega_datasets import data as vega_data
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

#Reactive function to calculate YoY growth by country for the bar chart
@reactive.calc
def yoy_by_country() -> dict:
    df = filtered_sales().copy()

    end_year = int(input.end_year())
    prev_year = int(input.start_year())

    _empty_df = pd.DataFrame(
        columns=["country", "sales_prev", "sales_curr", "pct_change"]
    )
    _empty = {"data": _empty_df, "prev_year": prev_year, "end_year": end_year}

    if df.shape[0] == 0:
        return _empty

    if df["sales"].dtype == "object":
        df["sales"] = (
            df["sales"].astype(str).str.replace(r"[\$,]", "", regex=True).astype(float)
        )

    totals = (
        df[df["year"].isin([prev_year, end_year])]
        .groupby(["country", "year"], as_index=False)
        .agg(total_sales=("sales", "sum"))
    )

    if totals.shape[0] == 0:
        return _empty

    wide = totals.pivot(
        index="country", columns="year", values="total_sales"
    ).reset_index()
    wide.columns.name = None

    # Ensure both year columns exist
    for col in [prev_year, end_year]:
        if col not in wide.columns:
            wide[col] = float("nan")

    wide = wide.rename(columns={prev_year: "sales_prev", end_year: "sales_curr"})
    wide["sales_prev"] = wide["sales_prev"].fillna(0.0)
    wide["sales_curr"] = wide["sales_curr"].fillna(0.0)

    # Only keep countries with data in both years
    wide = wide[(wide["sales_prev"] > 0) & (wide["sales_curr"] > 0)].copy()

    if wide.shape[0] == 0:
        return _empty

    wide["pct_change"] = (
        (wide["sales_curr"] - wide["sales_prev"]) / wide["sales_prev"] * 100
    )

    return {
        "data": wide[["country", "sales_prev", "sales_curr", "pct_change"]],
        "prev_year": prev_year,
        "end_year": end_year,
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
#output for YoY growth rate tile
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
#Output for average sales per transaction tile
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
#output for total transactions tile
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
        
# Row 1 of Charts
with ui.layout_columns(col_widths=[6, 3, 3]):
    with ui.card():
        ui.card_header("Year-over-Year Growth By Country")

        @render_altair
        def out_yoy_country_plot():
            result = yoy_by_country()
            wide = result["data"]
            prev_year = result["prev_year"]
            end_year = result["end_year"]

            _empty = (
                alt.Chart(pd.DataFrame({"message": ["No YoY comparison data available"]}))
                .mark_text(color="#6b7280", fontSize=12)
                .encode(text="message:N")
                .properties(height=260)
            )

            if wide.shape[0] == 0:
                return _empty

            bars = (
                alt.Chart(wide)
                .mark_bar()
                .encode(
                    y=alt.Y("country:N", sort="-x", title="Country"),
                    x=alt.X(
                        "pct_change:Q",
                        title=f"Percent change in sales (%) — {end_year} vs {prev_year}",
                    ),
                    color=alt.condition(
                        alt.datum.pct_change >= 0,
                        alt.value("#0072B2"),
                        alt.value("#E69F00"),
                    ),
                    tooltip=[
                        alt.Tooltip("country:N", title="Country"),
                        alt.Tooltip("sales_prev:Q", title=f"{prev_year} total", format=",.0f"),
                        alt.Tooltip("sales_curr:Q", title=f"{end_year} total", format=",.0f"),
                        alt.Tooltip("pct_change:Q", title="% change", format=".2f"),
                    ],
                )
            )

            rule = (
                alt.Chart(pd.DataFrame({"x": [0]}))
                .mark_rule(color="#6b7280", strokeWidth=1)
                .encode(x="x:Q")
            )

            return (
                (bars + rule)
                .properties(height=260, width="container")
                .configure_view(strokeOpacity=0)
                .configure_axis(gridColor="#e5e7eb")
            )

    with ui.card():
        ui.card_header("Sales Trend by Country Over Time")

        @render_altair
        def out_sales_trend_plot():
            df = filtered_sales().copy()

            _empty = (
                alt.Chart(pd.DataFrame({"message": ["No data available for selected filters"]}))
                .mark_text(color="#6b7280", fontSize=12)
                .encode(text="message:N")
                .properties(height=260)
            )

            if df.shape[0] == 0:
                return _empty

            if df["sales"].dtype == "object":
                df["sales"] = (
                    df["sales"].astype(str)
                    .str.replace(r"[\$,]", "", regex=True)
                    .astype(float)
                )

            df["ym"] = pd.to_datetime(df["year_month_period"], errors="coerce")

            trend = (
                df.dropna(subset=["ym"])
                .groupby(["ym", "country"], as_index=False)
                .agg(total_sales=("sales", "sum"))
            )

            if trend.shape[0] == 0:
                return _empty

            return (
                alt.Chart(trend)
                .mark_line(point=True)
                .encode(
                    x=alt.X("ym:T", title="Month"),
                    y=alt.Y(
                        "total_sales:Q",
                        title="Total sales (USD)",
                        axis=alt.Axis(format="$,.0f"),
                    ),
                    color=alt.Color("country:N", title="Country"),
                    tooltip=[
                        alt.Tooltip("country:N", title="Country"),
                        alt.Tooltip("ym:T", title="Month"),
                        alt.Tooltip("total_sales:Q", title="Sales", format="$,.0f"),
                    ],
                )
                .properties(height=260, width="container")
                .interactive()
                .configure_view(strokeOpacity=0)
                .configure_axis(gridColor="#e5e7eb")
            )

    with ui.card():
        ui.card_header("Countries and Regional Contribution Breakdown")

        @render_altair
        def out_country_map():
            df = filtered_sales().copy()

            _empty = (
                alt.Chart(pd.DataFrame({"message": ["No data available for selected filters"]}))
                .mark_text(color="#6b7280", fontSize=12)
                .encode(text="message:N")
                .properties(height=260)
            )

            if df.shape[0] == 0:
                return _empty

            if df["sales"].dtype == "object":
                df["sales"] = (
                    df["sales"].astype(str)
                    .str.replace(r"[\$,]", "", regex=True)
                    .astype(float)
                )

            sales_by_country = (
                df.groupby("country", as_index=False)
                .agg(total_sales=("sales", "sum"))
            )

            countries = alt.topo_feature(vega_data.world_110m.url, "countries")

            country_names_url = (
                "https://gist.githubusercontent.com/mbostock/4090846/raw/"
                "07e73f3c2d21558489604a0bc434b3a5cf41a867/world-country-names.tsv"
            )

            return (
                alt.Chart(countries)
                .mark_geoshape(stroke="white", strokeWidth=0.2)
                .project("equalEarth")
                .transform_lookup(
                    lookup="id",
                    from_=alt.LookupData(country_names_url, "id", ["name"]),
                )
                .transform_lookup(
                    lookup="name",
                    from_=alt.LookupData(sales_by_country, "country", ["total_sales"]),
                )
                .transform_calculate(
                    total_sales="isValid(datum.total_sales) ? datum.total_sales : 0"
                )
                .encode(
                    color=alt.Color("total_sales:Q", title="Total sales (USD)"),
                    tooltip=[
                        alt.Tooltip("name:N", title="Country"),
                        alt.Tooltip("total_sales:Q", title="Sales", format="$,.0f"),
                    ],
                )
                .properties(height=260, width="container")
                .configure_view(strokeOpacity=0)
            )

# Row 2 of Chart and table
with ui.layout_columns(col_widths=[6,6]):
    with ui.card():
        ui.card_header("Countries Sales Contribution")
        "Interactive table with transaction details (Country, Top Sales Representative, Total Sales(USD), Percentage Contribution(%))"
    
    with ui.card():
        ui.card_header("Top 5 Products")
        "Horizontal bar chart of top-performing products by sales revenue"