# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-28

### Added
- Sidebar filters for Start Year, End Year, Country, and Product Category.
- Shared reactive filtering step `filtered_sales()` to apply filters consistently across outputs.
- KPI value boxes (Total Sales Revenue, YoY Growth Rate, Avg Sales per Transaction, Total Transactions).
- Row 1 interactive Altair charts:
  - YoY % change by country (bar chart)
  - Sales trend over time by country (line chart)
  - Country-level sales choropleth map

### Changed
- Switched Row 1 charts to Altair rendering using shinywidgets (`@render_altair`) for interactivity.

### Fixed
- Improved choropleth map join by using a proper country-name lookup and handling UK/USA name matching.
- Prevented YoY-by-country errors when Start Year equals End Year (shows empty state instead of error).

### Known Issues

### Reflection