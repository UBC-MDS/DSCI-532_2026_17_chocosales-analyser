import re
from typing import Tuple


def enforce_select_and_limit(
    sql: str,
    *,
    max_rows: int,
    strict_select: bool,
    table_name: str = "chocolate_sales",
) -> Tuple[str, str]:
    """
    Return (new_sql, warning_message).

    - strict_select=True blocks non-SELECT queries (read-only)
    - always enforces LIMIT (tightens existing LIMIT if needed)
    """
    if not sql:
        return sql, ""

    s = sql.strip().rstrip(";")

    if strict_select and not s.lstrip().upper().startswith("SELECT"):
        safe_sql = f"SELECT * FROM {table_name} LIMIT 0"
        return safe_sql, "Blocked non-SELECT query (SELECT-only enabled)."

    # If query already ends with LIMIT N, tighten it to max_rows if needed
    m = re.search(r"^(.*)\bLIMIT\s+(\d+)\s*$", s, flags=re.IGNORECASE | re.DOTALL)
    if m:
        base = m.group(1).rstrip()
        try:
            existing = int(m.group(2))
            new_limit = min(existing, int(max_rows))
        except ValueError:
            new_limit = int(max_rows)
        return f"{base} LIMIT {new_limit}", ""

    # Otherwise append LIMIT
    return f"{s} LIMIT {int(max_rows)}", ""