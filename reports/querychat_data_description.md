# ChocoSales dataset (for AI Query)

You are working with **one table**: `chocolate_sales`.

Each row is a chocolate sales transaction.

## Columns
- `sales_person` (text): sales representative
- `country` (text): country of the transaction
- `product` (text): product category
- `date` (date): transaction date
- `sales` (number): sales amount in USD
- `boxes_shipped` (int): number of boxes shipped
- `year` (int): year (e.g., 2022–2024)
- `year_month_period` (text): year-month period label used for grouping (from the dataset)
- `year_month` (text): year-month label
- `month_name` (text): month name
- `month_num` (int): month number

## Helpful notes
- Use `sales` for revenue calculations (SUM/AVG).
- For time trends, group by `date`, `year_month`, or `year_month_period` (depending on the question).
- If someone asks “top” results, sort by `SUM(sales)` unless they specify another metric.