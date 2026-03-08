# Changelog

All notable changes to this project will be documented in this file.


## [0.3.0] - 2026-03-08

### Added
- An AI Query tab
- QueryChat so users can ask questions in natural language and onfigured QueryChat to use GitHub Models
- A table to show the QueryChat filtered dataframe
- A text output to show the generated SQL
- A CSV download for the current QueryChat filtered dataframe
- A shared reactive calc querychat_filtered_df() to standardize QueryChat result handling
- Two new visual outputs based on the QueryChat filtered dataframe:
  - out_querychat_country_plot: AI-filtered sales by country
  - out_querychat_top_products_plot: AI-filtered top 5 products

### Changed
- Improved KPI detail text formatting and readability on row-1 cards.
- Adjusted app layout spacing/fill behavior for a cleaner dashboard presentation.
- Updated map rendering behavior for unsupported/invalid countries (shown as neutral/grey).
- Increased card typography/sizing for better visual hierarchy.
- Updated the AI table download and dataframe output to use querychat_filtered_df().

### Fixed
- Removed fillable=True from ui.page_opts() to move away from the page-fillable layout and better align with instructor feedback.
- Updated YoY KPI logic in kpi_metrics() so the YoY card uses the previous year as the baseline and returns None when no valid baseline is available.
- Updated the country map so countries with no matching sales data are no longer forced to zero values.
- Fixed the percentage for the KPI card details YoY statistics card.
- Fixed minor typos across UI text and code comments.
- Fix token and coding save error to make the local path align well with the cloud, and both run successfully.

### Known Issues
- No known issues at the time of release.

### Reflection
- In v0.3.0, we expanded the dashboard by adding an AI Query workflow where users can ask natural-language questions and see the generated filtered results.
- This release improved usability by standardizing QueryChat result handling with querychat_filtered_df(), which reduced duplicated logic and made table, download, and chart outputs more consistent.
- We improved visual clarity in the dashboard through typography and spacing updates, and refined KPI detail text so year-over-year context is easier to read.
- We also strengthened robustness by fixing YoY baseline logic and improving map behavior for unmatched countries, which reduced confusing or misleading displays.
- Overall, v0.3.0 moves the project closer to decision-support use cases by combining interactive visual analytics with conversational querying, while keeping the pipeline more maintainable.

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