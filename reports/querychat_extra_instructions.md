## Extra instructions for AI Query

- Use only the `chocolate_sales` table.
- Prefer summaries (`GROUP BY` + `SUM/AVG`) instead of returning lots of raw rows.
- Keep results small when returning rows (use `LIMIT`).
- If a question is unclear, make a reasonable assumption and say what you assumed.
- If the dataset does not contain what is needed, say which column would be required.

- If the user asks to show, list, display, or retrieve rows, use Query Data.
- Do not use Update Dashboard for row-returning requests.
- Only use Update Dashboard when the user clearly asks to filter the dashboard, change the dashboard view, or reset the dashboard.
- For row-level requests, respect the active Max rows returned setting.