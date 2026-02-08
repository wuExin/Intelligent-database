"""CSV and JSON formatters for data export."""

import csv
import json
import io
from typing import Iterator, List, Any, Dict
from datetime import datetime, date


def format_rows_as_csv(
    columns: List[str],
    rows: Iterator[Dict[str, Any]],
    include_header: bool = True
) -> Iterator[str]:
    """
    Format query results as CSV (RFC 4180 compliant).

    Args:
        columns: List of column names
        rows: Iterator of row dictionaries
        include_header: Whether to include header row

    Yields:
        CSV formatted strings (chunks)

    Examples:
        >>> rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        >>> csv_chunks = list(format_rows_as_csv(["id", "name"], iter(rows)))
        >>> csv_chunks[0]
        'id,name\\n'
        >>> csv_chunks[1]
        '1,Alice\\n'
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Write header
    if include_header:
        header = ','.join(columns)
        yield header + '\n'
        output.seek(0)
        output.truncate()

    # Write rows
    for row in rows:
        # Convert row values to CSV-compatible format
        csv_row = [_format_value_for_csv(row.get(col)) for col in columns]
        writer.writerow(csv_row)
        yield output.getvalue()
        output.seek(0)
        output.truncate()


def _format_value_for_csv(value: Any) -> str:
    """
    Format a single value for CSV export.

    Args:
        value: Value to format

    Returns:
        CSV-formatted string
    """
    if value is None:
        return ''
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    else:
        return str(value)


def format_rows_as_json(
    columns: List[str],
    rows: Iterator[Dict[str, Any]]
) -> Iterator[str]:
    """
    Format query results as JSON (array of objects).

    Args:
        columns: List of column names
        rows: Iterator of row dictionaries

    Yields:
        JSON formatted strings (chunks)

    Examples:
        >>> rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        >>> json_chunks = list(format_rows_as_json(["id", "name"], iter(rows)))
        >>> ''.join(json_chunks)
        '[{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]'
    """
    yield '['

    first_row = True
    for row in rows:
        # Convert row to JSON-compatible format
        json_row = {col: _format_value_for_json(row.get(col)) for col in columns}

        if not first_row:
            yield ','

        yield json.dumps(json_row, ensure_ascii=False)
        first_row = False

    yield ']'


def _format_value_for_json(value: Any) -> Any:
    """
    Format a single value for JSON export.

    Args:
        value: Value to format

    Returns:
        JSON-compatible value
    """
    if value is None:
        return None
    elif isinstance(value, bool):
        return value
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, str):
        return value
    else:
        return str(value)
