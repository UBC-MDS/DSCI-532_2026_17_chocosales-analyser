# ChocoSales Analyser (main app file)
#
# This is a Shiny for Python dashboard that lets users explore chocolate sales
# data by country, product, and year. The sidebar filters drive everything when
# you change a filter, every chart, table, and KPI tile updates automatically.
#
# Layout overview:
#   Sidebar: year range, country, product dropdowns + a reset button
#   Top row: 4 headline KPI tiles (revenue, YoY growth, avg sale, transactions)
#   Row 1: YoY bar chart | quarterly trend lines | world sales map
#   Row 2: country breakdown table | top-5 products bar chart
#   Footer: app info, authors, GitHub link, live row count
#
# Authors: Chikire Aku-Ibe, Shihan Xu, Samrawit Mezgebo Tsegay

from datetime import date
from pathlib import Path

import altair as alt         # all charts are built with Altair
import pandas as pd
from shiny import reactive
from shiny.express import input, render, ui   # Express mode — no explicit App() needed
from shinywidgets import render_altair        # lets us drop Altair charts into Shiny outputs
from vega_datasets import data as vega_data  # provides the world map TopoJSON for the choropleth

# our own helpers — filter_sales does the row filtering, kpi_helpers formats the tile text
from utils.filter_sales import filter_sales
from utils.kpi_helpers import (
    format_delta_detail_with_value,
    format_yoy_tile,
)


# Load the cleaned dataset once when the app starts up.
# All filtering happens downstream — we never modify this original DataFrame.
DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "chocolate_sales_clean.csv"
)
sales_df = pd.read_csv(DATA_PATH)
sales_df["year"] = sales_df["year"].astype(int)  # make year an int so filter comparisons work cleanly

# Grab today's date once so we can show it in the header and footer
_last_updated = date.today().strftime("%B %d, %Y")

# ---------------------------------------------------------------------------
# Reactive calculations — these are the engine behind the dashboard.
# Shiny re-runs each one automatically whenever the inputs it reads change.
# ---------------------------------------------------------------------------

# filtered_sales is the single source of truth for the whole app.
# Every chart and KPI reads from here, so changing a sidebar filter
# automatically flows through to every visible element.
@reactive.calc
def filtered_sales() -> pd.DataFrame:
    return filter_sales(
        sales_df=sales_df,
        start_year=input.start_year(),
        end_year=input.end_year(),
        country=input.country(),
        product=input.product(),
    )


# kpi_metrics bundles all four headline numbers into one dict.
# Doing it in a single reactive calc means the aggregation only runs once
# per filter change, even though four separate value boxes consume it.
@reactive.calc
def kpi_metrics() -> dict:
    df = filtered_sales().copy()

    # If the current filters return no data, give back safe zero/None defaults
    # so the tiles display sensibly rather than crashing.
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

    # The sales column occasionally arrives as a string like "$1,200" —
    # strip the dollar sign and commas before doing any arithmetic.
    if df["sales"].dtype == "object":
        df["sales"] = (
            df["sales"].astype(str).str.replace(r"[\$,]", "", regex=True).astype(float)
        )

    total_revenue = float(df["sales"].sum())
    avg_sales_per_tran = float(df["sales"].mean())
    total_transactions = int(df.shape[0])

    # For the KPI tiles we always compare the *end year* against the year
    # immediately before it, regardless of what start_year is set to.
    # This keeps the YoY comparison consistent and meaningful.
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

# yoy_by_country shows how each country's sales changed between the user's
# chosen start year and end year. We use a pivot (long to wide) approach:
# group by country + year, pivot so each year is its own column, then
# calculate the percentage change. Countries that only appear in one of the
# two years are excluded since we need both to draw a meaningful bar.
# Returns a dict (not just a DataFrame) so the chart render function can
# also know which years were compared, without having to re-read inputs.
@reactive.calc
def yoy_by_country() -> dict:
    df = filtered_sales().copy()

    end_year = int(input.end_year())
    prev_year = int(input.start_year())

    _empty_df = pd.DataFrame(
        columns=["country", "sales_prev", "sales_curr", "pct_change"]
    )
    _empty = {"data": _empty_df, "prev_year": prev_year, "end_year": end_year}
    
    if prev_year == end_year:
        return _empty

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

# top5_products_data picks the five best-selling products under the current
# filters and returns their total sales, average transaction value, and
# transaction count. The extra columns power the rich tooltip in the chart.
@reactive.calc
def top5_products_data() -> pd.DataFrame:
    df = filtered_sales().copy()

    _empty = pd.DataFrame(columns=["product", "total_sales", "avg_transaction", "total_transactions"])

    if df.shape[0] == 0:
        return _empty

    if df["sales"].dtype == "object":
        df["sales"] = (
            df["sales"].astype(str).str.replace(r"[\$,]", "", regex=True).astype(float)
        )

    ranked = (
        df.groupby("product", as_index=False)
        .agg(
            total_sales=("sales", "sum"),
            avg_transaction=("sales", "mean"),
            total_transactions=("sales", "count"),
        )
        .sort_values("total_sales", ascending=False)
        .head(5)
    )

    return ranked[["product", "total_sales", "avg_transaction", "total_transactions"]]


# reset_filters listens for a click on the "Reset Filters" button and puts
# all four dropdowns back to their default values. Because we use
# @reactive.event, this function only runs on an explicit button click —
# it won't fire just because the app loads. Updating the dropdowns
# automatically triggers filtered_sales() to rerun, so every chart refreshes.
@reactive.effect
@reactive.event(input.reset_filters)
def reset_filters():
    year_choices = ["2022", "2023", "2024"]
    ui.update_select("start_year", selected=year_choices[0])  # back to the earliest year
    ui.update_select("end_year", selected=year_choices[-1])   # back to the latest year
    ui.update_select("country", selected="All")               # show all countries
    ui.update_select("product", selected="All")               # show all products


# ---------------------------------------------------------------------------
# UI — everything below defines what the user actually sees.
# Shiny Express uses indented `with` blocks instead of nested function calls.
# ---------------------------------------------------------------------------

# fillable=True lets the page expand to fill the full browser height.
ui.page_opts(title="ChocoSales Analyser", fillable=True)

# Sidebar is open by default on desktop and collapses on mobile.
# Every dropdown here feeds directly into filtered_sales().
with ui.sidebar(title="Filters", open="desktop"):
    with ui.layout_columns(col_widths=[5, 5]):
        ui.input_select(
            "start_year",
            "Start Year",
            choices=["2022", "2023", "2024"],
            selected="2022"
        )
        ui.input_select(
            "end_year",
            "End Year",
            choices=["2022", "2023", "2024"],
            selected="2024"
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
    ui.input_action_button(
        "reset_filters",
        "Reset Filters",
        # outline style keeps it unobtrusive; w-100 stretches it to the sidebar width
        class_="btn btn-outline-secondary btn-sm w-100 mt-2",
    )

# Dashboard title on the left, auto-updating date on the right
with ui.layout_columns(col_widths=[8, 4], class_="mb-0", fill=False):
    ui.h2("Chocolate Sales Analyser Dashboard", class_="mb-0")
    ui.tags.div(
        f"Last updated: {_last_updated}",
        class_="text-end small pt-0"
    )

# Four KPI value boxes in a single row — all read from kpi_metrics() so the
# numbers are computed once and shared, not recalculated four separate times.
with ui.layout_columns(
    col_widths=[3, 3, 3, 3],
    class_="g-2 mt-0 pt-0",
    fill=False,
):
    # Sum of all sales in the filtered dataset
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
    # Percentage change in revenue from end_year-1 to end_year
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
    # Average value of a single transaction across the filtered rows
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
    # Total number of rows in the filtered dataset (each row = one transaction)
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
        
# ---------------------------------------------------------------------------
# Row 1 — three equal-width chart cards.
# full_screen=True adds the little expand icon in the top-right corner.
# All charts use width='container' so they fill the card, and height=260
# so the row stays visually balanced.
# ---------------------------------------------------------------------------
with ui.layout_columns(col_widths=[4, 4, 4], fill=True):

    # Horizontal bar chart — one bar per country showing % sales change
    # between start_year and end_year. Blue = growth, orange = decline.
    # A thin vertical line at 0 makes it easy to read positive vs negative.
    with ui.card(full_screen=True, class_="shadow-sm border-0"):
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

    # Quarterly line chart which shows one coloured line per country over time.
    # Clicking a country name in the legend highlights that line and fades
    # the others, making it easier to follow a single country's trend.
    # The chart is also zoomable and pannable (`.interactive()`).
    with ui.card(full_screen=True, class_="shadow-sm border-0"):
        ui.card_header("Sales Trend by Country Over Time")

        @render_altair
        def out_sales_trend_plot():
            # Pull filtered rows and aggregate them to quarterly totals
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
            df = df.dropna(subset=["ym"])
            if df.shape[0] == 0:
                return _empty

            # Aggregate to quarters
            df["quarter"] = df["ym"].dt.to_period("Q").dt.start_time

            trend = (
                df.groupby(["quarter", "country"], as_index=False)
                .agg(total_sales=("sales", "sum"), transactions=("sales", "count"))
            )
            if trend.shape[0] == 0:
                return _empty

            selection = alt.selection_point(fields=["country"], bind="legend")

            return (
                alt.Chart(trend)
                .mark_line(point=True)
                .encode(
                    x=alt.X("quarter:T", title="Quarter", axis=alt.Axis(format="%Y Q%q", labelAngle=-45, labelFontSize=10)),
                    y=alt.Y(
                        "total_sales:Q",
                        title="Total Sales (USD)",
                        axis=alt.Axis(format="$,.0f"),
                    ),
                    color=alt.Color(
                        "country:N",
                        title="Country",
                        scale=alt.Scale(
                            range=["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7"]
                        ),
                        legend=alt.Legend(
                            orient="bottom",
                            columns=3,
                            labelFontSize=10,
                            titleFontSize=10,
                        ),
                    ),
                    opacity=alt.condition(selection, alt.value(1.0), alt.value(0.1)),
                    tooltip=[
                        alt.Tooltip("country:N", title="Country"),
                        alt.Tooltip("quarter:T", title="Quarter", format="%Y Q%q"),
                        alt.Tooltip("total_sales:Q", title="Total Sales (USD)", format="$,.0f"),
                        alt.Tooltip("transactions:Q", title="Transactions", format=","),
                    ],
                )
                .add_params(selection)
                .properties(height=220, width="container")
                .interactive()
                .configure_view(strokeOpacity=0)
                .configure_axis(
                    gridColor="#e5e7eb",
                    labelFontSize=10,
                    titleFontSize=11,
                )
            )

    # World choropleth map of countries shaded by total sales volume.
    # We join our aggregated sales data onto the Vega world topology using
    # a country-name lookup. Countries with no sales under the current
    # filters are shown as 0 rather than blank so the map always renders.
    with ui.card(full_screen=True, class_="shadow-sm border-0"):
        ui.card_header("Countries and Regional Contribution Breakdown")

        @render_altair
        def out_country_map():
            # Re-aggregate every time the filters change
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

            # Aggregate totals, then join onto the world map by country name
            sales_by_country = (
                df.groupby("country", as_index=False)
                .agg(total_sales=("sales", "sum"))
            )

            # Fix common abbreviations so they match the map's country names
            name_fixes = {"UK": "United Kingdom", "USA": "United States"}
            sales_by_country["name"] = sales_by_country["country"].replace(name_fixes)

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
                    from_=alt.LookupData(sales_by_country, "name", ["total_sales"]),
                )
                .transform_calculate(
                    # Countries not present in the filtered data should still render as 0
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

# ---------------------------------------------------------------------------
# Row 2 — summary table on the left, top-5 products chart on the right.
# ---------------------------------------------------------------------------
with ui.layout_columns(col_widths=[6, 6]):

    # Table showing each country's total revenue and its share of the grand
    # total, plus the top-earning sales rep for that country.
    # Rows are sorted by contribution % so the biggest markets are at the top.
    with ui.card():
        ui.card_header("Countries Sales Contribution")

        @render.data_frame
        def out_country_contrib_table():
            df = filtered_sales().copy()

            if df.shape[0] == 0:
                return render.DataGrid(
                    pd.DataFrame(columns=["Country", "Top Sales Rep", "Total Sales (USD)", "Contribution (%)"]),
                    summary=False,
                )

            if df["sales"].dtype == "object":
                df["sales"] = (
                    df["sales"].astype(str).str.replace(r"[\$,]", "", regex=True).astype(float)
                )

            # Total sales per country
            country_totals = (
                df.groupby("country", as_index=False)
                .agg(total_sales=("sales", "sum"))
            )

            # Top sales rep per country (by total sales)
            rep_totals = (
                df.groupby(["country", "sales_person"], as_index=False)
                .agg(rep_sales=("sales", "sum"))
            )
            top_reps = (
                rep_totals.sort_values("rep_sales", ascending=False)
                .drop_duplicates(subset="country", keep="first")[["country", "sales_person"]]
                .rename(columns={"sales_person": "top_rep"})
            )

            # Merge and compute percentage contribution
            table = country_totals.merge(top_reps, on="country", how="left")
            grand_total = table["total_sales"].sum()
            table["pct_contribution"] = (table["total_sales"] / grand_total * 100).round(1)

            # Sort by contribution descending
            table = table.sort_values("pct_contribution", ascending=False).reset_index(drop=True)

            # Format for display
            display = pd.DataFrame({
                "Country": table["country"],
                "Top Sales Rep": table["top_rep"],
                "Total Sales (USD)": table["total_sales"].apply(lambda v: f"${v:,.0f}"),
                "Contribution (%)": table["pct_contribution"].apply(lambda v: f"{v:.1f}%"),
            })

            return render.DataGrid(display, summary=False)
    
    # Horizontal bar chart of top 5 products by total sales under the current
    # filters. Clicking a product in the legend highlights its bar.
    # The ranking is fixed to total_sales for this milestone.
    with ui.card(full_screen=True):
        ui.card_header("Top 5 Products")

        @render_altair
        def out_top5_products_plot():
            top5 = top5_products_data()

            _empty = (
                alt.Chart(pd.DataFrame({"message": ["No product data available"]}))
                .mark_text(color="#6b7280", fontSize=12)
                .encode(text="message:N")
                .properties(height=260)
            )

            if top5.shape[0] == 0:
                return _empty

            selection = alt.selection_point(fields=["product"], bind="legend")

            return (
                alt.Chart(top5)
                .mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3)
                .encode(
                    y=alt.Y(
                        "product:N",
                        sort="-x",
                        title=None,
                        axis=alt.Axis(labelLimit=200),
                    ),
                    x=alt.X(
                        "total_sales:Q",
                        title="Total Sales (USD)",
                        axis=alt.Axis(format="$,.0f"),
                    ),
                    color=alt.Color(
                        "product:N",
                        title="Product",
                        scale=alt.Scale(
                            range=["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00"]
                        ),
                        legend=alt.Legend(orient="bottom"),
                    ),
                    opacity=alt.condition(selection, alt.value(1.0), alt.value(0.2)),
                    tooltip=[
                        alt.Tooltip("product:N", title="Product"),
                        alt.Tooltip("total_sales:Q", title="Total Sales (USD)", format="$,.0f"),
                        alt.Tooltip("avg_transaction:Q", title="Avg Transaction (USD)", format="$,.2f"),
                        alt.Tooltip("total_transactions:Q", title="Transactions", format=","),
                    ],
                )
                .add_params(selection)
                .properties(height=260, width="container")
                .configure_view(strokeOpacity=0)
                .configure_axis(gridColor="#e5e7eb")
            )

# ---------------------------------------------------------------------------
# Footer with static info (authors, repo) plus live stats that update with
# the filters (transaction count and data date range).
# ---------------------------------------------------------------------------
with ui.layout_columns(col_widths=[12], fill=False):
    @render.ui
    def out_app_footer():
        df = filtered_sales()
        row_count = df.shape[0]

        if row_count > 0:
            date_col = pd.to_datetime(df["date"], errors="coerce").dropna()
            if len(date_col) > 0:
                date_range = (
                    f"{date_col.min().strftime('%b %d, %Y')} – {date_col.max().strftime('%b %d, %Y')}"
                )
            else:
                date_range = "N/A"
        else:
            date_range = "N/A"

        return ui.tags.footer(
            ui.tags.hr(style="margin: 0.5rem 0; border-color: #dee2e6;"),
            ui.tags.div(
                ui.tags.div(
                    ui.tags.strong("ChocoSales Analyser"),
                    " — Interactive dashboard for exploring chocolate sales performance "
                    "across countries, products, and time periods.",
                    class_="mb-1",
                ),
                ui.tags.div(
                    ui.tags.span("Authors: ", class_="fw-semibold"),
                    "Chikire Aku-Ibe, Shihan Xu, Samrawit Mezgebo Tsegay",
                    ui.tags.span(" · ", class_="text-muted mx-1"),
                    ui.tags.a(
                        "GitHub Repository",
                        href="https://github.com/UBC-MDS/DSCI-532_2026_17_chocosales-analyser",
                        target="_blank",
                        class_="text-decoration-none",
                    ),
                    ui.tags.span(" · ", class_="text-muted mx-1"),
                    ui.tags.span(f"Last updated: {_last_updated}"),
                    class_="mb-1",
                ),
                ui.tags.div(
                    ui.tags.span("Filtered dataset: ", class_="fw-semibold"),
                    f"{row_count:,} transactions",
                    ui.tags.span(" · ", class_="text-muted mx-1"),
                    ui.tags.span("Date range: "),
                    date_range,
                    class_="text-muted",
                ),
                class_="small py-2 px-1",
            ),
        )