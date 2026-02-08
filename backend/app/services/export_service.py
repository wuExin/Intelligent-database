"""Export service for streaming CSV/JSON exports."""

import hashlib
from datetime import datetime, timedelta
from typing import AsyncIterator, Dict, Any, List, Optional
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json as json_lib
from jose import jwt
from jose.exceptions import JWTError

from app.utils.formatters import format_rows_as_csv, format_rows_as_json
from app.services.filename_generator import generate_filename


# JWT secret for export URL signing (should be in config)
EXPORT_JWT_SECRET = "your-secret-key-change-in-production"
EXPORT_TOKEN_EXPIRY_MINUTES = 5


async def stream_query_results(
    db_url: str,
    sql: str,
    chunk_size: int = 1000
) -> AsyncIterator[Dict[str, Any]]:
    """
    Stream query results from database in chunks.

    Args:
        db_url: Database connection URL
        sql: SQL query to execute
        chunk_size: Number of rows to fetch per chunk

    Yields:
        Row dictionaries

    Raises:
        Exception: Database connection or query error
    """
    # This is a placeholder - actual implementation will use the existing
    # database connection service from the codebase
    # For now, we'll use a simple async approach
    raise NotImplementedError("Use existing query_wrapper service")


def generate_export_token(
    database: str,
    sql: str,
    format: str
) -> str:
    """
    Generate JWT token for export URL authorization.

    Args:
        database: Database name
        sql: SQL query (will be hashed)
        format: Export format (csv, json)

    Returns:
        JWT token string
    """
    # Create SQL hash for tamper detection
    sql_hash = hashlib.sha256(sql.encode()).hexdigest()

    # Create payload with full SQL
    payload = {
        "database": database,
        "sql": sql,
        "sql_hash": sql_hash,
        "format": format,
        "exp": datetime.utcnow() + timedelta(minutes=EXPORT_TOKEN_EXPIRY_MINUTES),
        "iat": datetime.utcnow()
    }

    # Generate token
    token = jwt.encode(payload, EXPORT_JWT_SECRET, algorithm="HS256")

    return token


def validate_export_token(token: str) -> tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validate export JWT token.

    Args:
        token: JWT token string

    Returns:
        Tuple of (is_valid, payload_dict)
    """
    try:
        payload = jwt.decode(token, EXPORT_JWT_SECRET, algorithms=["HS256"])
        return True, payload
    except JWTError:
        return False, None


async def stream_query_export(
    db_url: str,
    sql: str,
    columns: List[str],
    format: str,
    filename: Optional[str] = None
) -> StreamingResponse:
    """
    Stream query results as CSV or JSON export.

    Args:
        db_url: Database connection URL
        sql: SQL query to export
        columns: List of column names
        format: Export format (csv, json)
        filename: Optional filename for Content-Disposition header

    Returns:
        FastAPI StreamingResponse

    Raises:
        ValueError: Invalid format
    """
    if format not in ["csv", "json"]:
        raise ValueError(f"Invalid format: {format}. Must be 'csv' or 'json'")

    # Generate filename if not provided
    if filename is None:
        # Extract database name from URL (simplified)
        database = db_url.split("/")[-1].split("?")[0]
        filename = generate_filename(database, "query", format=format)

    async def generate():
        """Async generator for streaming data."""
        rows_stream = stream_query_results(db_url, sql)

        if format == "csv":
            async for chunk in format_rows_as_csv(columns, rows_stream):
                yield chunk
        else:  # json
            async for chunk in format_rows_as_json(columns, rows_stream):
                yield chunk

    # Determine media type
    media_type = "text/csv" if format == "csv" else "application/json"

    # Create streaming response
    response = StreamingResponse(
        generate(),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

    return response


def get_export_urls(
    database: str,
    sql: str,
    base_url: str = "/api/v1/dbs"
) -> Dict[str, Any]:
    """
    Generate export URLs for a query result.

    Args:
        database: Database name
        sql: SQL query
        base_url: Base API URL

    Returns:
        Dictionary with csv_url, json_url, expires_at, default_filename, row_count
    """
    # Generate tokens
    csv_token = generate_export_token(database, sql, "csv")
    json_token = generate_export_token(database, sql, "json")

    # Generate URLs
    csv_url = f"{base_url}/{database}/export/query?token={csv_token}&format=csv"
    json_url = f"{base_url}/{database}/export/query?token={json_token}&format=json"

    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(minutes=EXPORT_TOKEN_EXPIRY_MINUTES)

    # Generate default filename
    default_filename = generate_filename(database, "query", format="csv").replace(".csv", "")

    return {
        "exportCsvUrl": csv_url,
        "exportJsonUrl": json_url,
        "expiresAt": expires_at,
        "defaultFilename": default_filename,
        "rowCount": 0  # Will be populated by caller
    }
