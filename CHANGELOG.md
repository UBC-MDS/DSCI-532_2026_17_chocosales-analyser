# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-28

### Added
- Sidebar filters for Start Year, End Year, Country, and Product Category.
- Shared reactive filtering step `filtered_sales()` so outputs update consistently from the same filtered dataset.
- KPI tiles powered by `kpi_metrics()` and rendered as `ui.value_box()` (total revenue, YoY growth rate, avg sales/transaction, total transactions).
- Row 1 interactive Altair charts:
  - YoY % change by country (bar chart)
  - Sales trend over time by country (line chart)
  - Country-level sales choropleth map
- Reusable utilities in `utils/` (e.g., `filter_sales`).
- Footer + active filter state outputs to give users context while filtering.
- Completed M2 spec sections (component inventory, reactivity diagram, calculation details) to match the prototype.

### Changed
- Switched charts to Altair rendering using shinywidgets (`@render_altair`) for interactivity.
- Refined KPI tile styling (colors + detail text) and tightened spacing between the title and KPI row.

### Fixed
- Improved choropleth map join by using a proper country-name lookup and handling UK/USA name matching.
- Prevented YoY-by-country errors when Start Year equals End Year (shows empty state instead of error).
- Fixed KPI renderer/display issues (duplicate outputs and rendering errors).
- Improved year parsing robustness and validated required columns for filtering to avoid runtime errors.

### Known Issues


### Reflection
- Added KPI summaries and supporting utilities to make the dashboard more informative and keep filtering logic reusable/consistent across outputs.
- Updated the M2 spec (inventory/diagram/calculation details) to track implemented components and planned next steps.
