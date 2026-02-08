"""Export API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import Literal
import io
import csv
import json

from app.database import get_session
from app.models.database import DatabaseConnection
from app.models.schemas import ErrorResponse
from app.services.export_service import (
    validate_export_token,
    stream_query_export,
    get_export_urls
)
from app.services.query_wrapper import execute_query_with_service
from app.models.query import QuerySource
from sqlmodel import select
from app.utils.formatters import format_rows_as_csv, format_rows_as_json
from app.services.filename_generator import generate_filename
from datetime import datetime

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/query")
async def export_query_results(
    name: str,
    token: str,
    format: Literal["csv", "json"],
    filename: str | None = None,
    session: Session = Depends(get_session)
):
    """
    Export query results to CSV or JSON format.

    Args:
        name: Database connection name
        token: Signed JWT token for authorization
        format: Export format (csv or json)
        filename: Optional custom filename (without extension)
        session: Database session

    Returns:
        StreamingResponse with CSV/JSON data
    """
    # Validate token
    is_valid, payload = validate_export_token(token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Export token has expired or is invalid"
        )

    # Extract SQL from token payload
    sql = payload.get("sql")
    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token: missing SQL query"
        )

    # Verify database access
    statement = select(DatabaseConnection).where(DatabaseConnection.name == name)
    connection = session.exec(statement).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database connection '{name}' not found"
        )

    # Execute query
    try:
        result = await execute_query_with_service(
            session,
            name,
            connection.db_type,
            connection.url,
            sql,
            QuerySource.MANUAL,
        )

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_query_{timestamp}"

        # Create streaming response
        media_type = "text/csv" if format == "csv" else "application/json"
        full_filename = f"{filename}.{format}"

        async def generate():
            """Generate CSV or JSON content."""
            if format == "csv":
                # Generate CSV
                output = io.StringIO()
                writer = csv.writer(output)

                # Write header
                columns = [col.name for col in result.columns]
                writer.writerow(columns)

                # Write rows
                for row in result.rows:
                    values = [row.get(col, "") for col in columns]
                    writer.writerow(values)

                yield output.getvalue()

            else:  # json
                # Generate JSON
                yield json.dumps(result.rows, ensure_ascii=False, indent=2)

        return StreamingResponse(
            generate(),
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{full_filename}"'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.get("/table/{table_name}")
async def export_table(
    name: str,
    table_name: str,
    token: str,
    format: Literal["csv", "json"],
    filename: str | None = None,
    session: Session = Depends(get_session)
):
    """
    Export single table to CSV or JSON format.

    Args:
        name: Database connection name
        table_name: Table name to export
        token: Signed JWT token for authorization
        format: Export format (csv or json)
        filename: Optional custom filename
        session: Database session

    Returns:
        StreamingResponse with CSV/JSON data
    """
    # Validate token
    is_valid, payload = validate_export_token(token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Export token has expired or is invalid"
        )

    # Verify database exists
    statement = select(DatabaseConnection).where(DatabaseConnection.name == name)
    connection = session.exec(statement).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database connection '{name}' not found"
        )

    # TODO: Implement table export
    # 1. Validate table exists in database
    # 2. Construct SELECT * FROM table query
    # 3. Call stream_query_export

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Table export endpoint pending implementation"
    )


@router.get("/tables")
async def export_all_tables(
    name: str,
    token: str,
    format: Literal["csv", "json"],
    session: Session = Depends(get_session)
):
    """
    Export all tables from database.

    For 1-2 tables: Returns JSON with download URLs
    For 3+ tables: Returns ZIP archive

    Args:
        name: Database connection name
        token: Signed JWT token for authorization
        format: Export format (csv or json)
        session: Database session

    Returns:
        StreamingResponse (ZIP) or JSON with file URLs
    """
    # Validate token
    is_valid, payload = validate_export_token(token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Export token has expired or is invalid"
        )

    # Verify database exists
    statement = select(DatabaseConnection).where(DatabaseConnection.name == name)
    connection = session.exec(statement).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database connection '{name}' not found"
        )

    # TODO: Implement all tables export
    # 1. Fetch list of all tables from metadata
    # 2. If 1-2 tables: return JSON array of export URLs
    # 3. If 3+ tables: return ZIP archive

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="All tables export endpoint pending implementation"
    )
