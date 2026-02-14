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
        "Product Category",
        choices=["All"],
        selected="All"
    )

# Main content area
ui.h2("ChocoSales Analyser Dashboard")

# Add statistics cards row
with ui.layout_columns(col_widths=[3, 3, 3, 3]):
    with ui.card():
        ui.card_header("Total Sales Revenue(USD)")
        "XXX"
    
    with ui.card():
        ui.card_header("Year Over Year Growth Rate(%)")
        "X.X"
    
    with ui.card():
        ui.card_header("Average Sales Per Transaction(USD)")
        "XXX"
    
    with ui.card():
        ui.card_header("Total Transaction(Count)")
        "XXX"
        
#Row 1 of Charts 
with ui.layout_columns(col_widths=[6, 6]):
    with ui.card():
        ui.card_header("Sales Trend by Country Over Time")
        "Line chart showing sales over time, color-coded by country"
    
    with ui.card():
        ui.card_header("Countries and Regional Contribution Breakdown")
        "map showing sales by country"
    