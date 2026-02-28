# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-28

### Added
- Sidebar filters for Start Year, End Year, Country, and Product Category.
- Shared reactive filtering step `filtered_sales()` so outputs update consistently from the same filtered dataset.
- KPI tiles powered by `kpi_metrics()` and rendered as `ui.value_box()` (total revenue, YoY growth rate, avg sales, total transactions).
- Row 1 interactive Altair charts:
  - YoY % change by country (bar chart)
  - Sales trend over time by country (line chart)
  - Country-level sales choropleth map
- Countries sales contribution summary table (country, top sales rep, total sales, contribution %).
- Top 5 products bar chart driven by a reactive calculation.
- Reset Filters button to quickly return to the default view.
- Reusable utilities in `utils/` (e.g.`filter_sales`).
- Footer & active filter state outputs to give users context while filtering.
- Completed M2 spec sections (component inventory, reactivity diagram, calculation details) to match the prototype.

### Changed
- Switched charts to Altair rendering using shinywidgets (`@render_altair`) for interactivity.
- Updated environment dependencies to support shinywidgets/anywidget/vega_datasets.
- Refined KPI tile styling (colors & detail text) and tightened spacing between the title and KPI row.

### Fixed
- Improved choropleth map join by using a proper country-name lookup and handling UK/USA name matching.
- Prevented YoY-by-country errors when Start Year equals End Year (shows empty state instead of error).
- Fixed KPI renderer/display issues (duplicate outputs and rendering errors).
- Improved year parsing robustness and validated required columns for filtering to avoid runtime errors.

### Known Issues
- No known issues at the time of release.

### Reflection
- JTBD #1, #2, and #4 are implemented in the prototype (filters, KPI summary, YoY/trend/map, top products, and a reset button).
- JTBD #3 is partially supported in M2 through the country contribution table.
- We stayed close to the M1 sketch but adjusted the layout so KPIs and key charts are visible, with filters in a sidebar plus a reset button for faster exploration.
- Using a shared `filtered_sales()` reactive step kept outputs consistent and reduced duplicated logic across renderers.
- switching charts to Altair improved legend interactions.