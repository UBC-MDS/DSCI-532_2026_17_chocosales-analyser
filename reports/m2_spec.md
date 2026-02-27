# Milestone 2 Specification

> Team note:this spec is a living document.please update the Status column (✅ / 🔄 Revised / ⏳ Pending M2 / ⏳ Pending M3) as we finalize scope and implement features,fill sections 2.2-2.4 based on the final M2 prototype.

## 2.1 Updated Job Stories

> Status values may be adjusted after we finalize M2 MVP vs M3 stretch scope.

| # | Job Story | Status | Notes |
|---|----------|--------|------|
| 1 | When I’m reviewing sales performance across countries over time, I want to filter by year range and country and see sales trends/YoY growth, so I can spot which markets are growing faster/slower and decide where to focus. | ⏳ Pending M2 | From M1 JTBD 1 |
| 2 | When I’m evaluating product performance, I want to filter by product category and see top products by sales (and/or average transaction value), so I can prioritize products for marketing/promos. | ⏳ Pending M2 | From M1 JTBD 2 |
| 3 | When I’m evaluating team performance, I want to compare sales reps under selected filters, so I can reward top performers and provide targeted support. | ⏳ Pending M3 (TBD) | From M1 JTBD 3 |
| 4 | When I’ve changed multiple filters, I want a reset button, so I can quickly return to the default view. | ⏳ Pending M2 (Optional) | Optional enhancement |

## 2.2 Component Inventory

| ID | Type | Shiny Widget/renderer | Depends On | Job Story |
|---|---|---|---|---|
| input_start_year | Input | ui.input_select() | _ |  |
| input_end_year | Input | ui.input_select() | _ |  |
| input_country | Input | ui.input_select() | _ |  |
| input_product| Input | ui.input_select() |  |  |
| filtered_sales | Reactive calc  | @reactive.calc | input_start_year, input_end_year, input_country, input_product  |  |
|  kpi_metrics |  Reactive calc | @reactive.calc | filtered_sales |  |
| yoy_by_country | Reactive calc | @reactive.calc  | filtered_sales |  |
|  top5_products_data | Reactive calc  | @reactive.calc  | filtered_sales |  |
|  |  |  |  |  |
|  |  |  |  |  |


## 2.3 Reactivity Diagram
_TBD_

## 2.4 Calculation Details
_TBD_