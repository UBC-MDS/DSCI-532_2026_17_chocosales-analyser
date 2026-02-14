from shiny.express import ui

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
        choices=["All"],
        selected="All"
    )
    ui.input_select(
        "product",
        "Product",
        choices=["All"],
        selected="All"
    )

# Main content area
ui.h2("ChocoSales Analyser Dashboard")

