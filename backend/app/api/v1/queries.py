"""Query execution API endpoints."""

import json
import csv
import io
from typing import Literal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.database import DatabaseConnection
from app.models.query import QuerySource
from app.models.schemas import (
    QueryInput,
    QueryResult,
    QueryHistoryEntry,
    NaturalLanguageInput,
    GeneratedSqlResponse,
)
from app.services.query_wrapper import execute_query_with_service
from app.services.query import get_query_history
from app.services.sql_validator import SqlValidationError
from app.services.nl2sql import nl2sql_service
from app.services.metadata import get_cached_metadata
from app.services.export_service import get_export_urls, validate_export_token

router = APIRouter(prefix="/api/v1/dbs", tags=["queries"])


def to_history_entry(history) -> QueryHistoryEntry:
    """Convert QueryHistory to QueryHistoryEntry schema."""
    return QueryHistoryEntry(
        id=history.id,
        databaseName=history.database_name,
        sqlText=history.sql_text,
        executedAt=history.executed_at,
        executionTimeMs=history.execution_time_ms,
        rowCount=history.row_count,
        success=history.success,
        errorMessage=history.error_message,
        querySource=history.query_source.value,
    )


@router.get("/{name}/export/query")
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
    # Debug logging
    import sys
    print(f"[DEBUG] Export endpoint called: name={name}, format={format}, token={token[:20]}...", file=sys.stderr)

    # Validate token
    is_valid, payload = validate_export_token(token)
    if not is_valid:
        print(f"[DEBUG] Token validation failed", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Export token has expired or is invalid"
        )

    print(f"[DEBUG] Token validated, payload: {payload}", file=sys.stderr)

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


@router.post("/{name}/query", response_model=QueryResult)
async def execute_sql_query(
    name: str,
    input_data: QueryInput,
    session: Session = Depends(get_session),
) -> QueryResult:
    """
    Execute SQL query against a database.

    Args:
        name: Database connection name
        input_data: Query input with SQL
        session: Database session

    Returns:
        Query result with columns and rows
    """
    # Get connection
    statement = select(DatabaseConnection).where(
        DatabaseConnection.name == name
    )
    connection = session.exec(statement).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database connection '{name}' not found",
        )

    # Execute query
    try:
        result = await execute_query_with_service(
            session,
            name,
            connection.db_type,
            connection.url,
            input_data.sql,
            QuerySource.MANUAL,
        )

        # Generate export URLs for successful queries
        export_csv_url = None
        export_json_url = None
        export_expires_at = None

        try:
            export_info = get_export_urls(name, input_data.sql)
            export_csv_url = export_info["exportCsvUrl"]
            export_json_url = export_info["exportJsonUrl"]
            export_expires_at = export_info["expiresAt"]
        except Exception as export_error:
            # Log error but don't fail the query if export URL generation fails
            export_csv_url = None
            export_json_url = None
            export_expires_at = None

        # Create new QueryResult with export URLs
        result_with_exports = QueryResult(
            columns=result.columns,
            rows=result.rows,
            row_count=result.row_count,
            execution_time_ms=result.execution_time_ms,
            sql=result.sql,
            export_csv_url=export_csv_url,
            export_json_url=export_json_url,
            export_expires_at=export_expires_at
        )

        return result_with_exports
    except SqlValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}",
        )


@router.get("/{name}/history", response_model=List[QueryHistoryEntry])
async def get_query_history_for_database(
    name: str,
    limit: int = 50,
    session: Session = Depends(get_session),
) -> List[QueryHistoryEntry]:
    """
    Get query history for a database.

    Args:
        name: Database connection name
        limit: Maximum number of queries to return
        session: Database session

    Returns:
        List of query history entries
    """
    # Verify connection exists
    statement = select(DatabaseConnection).where(
        DatabaseConnection.name == name
    )
    connection = session.exec(statement).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database connection '{name}' not found",
        )

    # Get history
    history_list = await get_query_history(session, name, limit)
    return [to_history_entry(h) for h in history_list]


@router.post("/{name}/query/natural", response_model=GeneratedSqlResponse)
async def natural_language_to_sql(
    name: str,
    input_data: NaturalLanguageInput,
    session: Session = Depends(get_session),
) -> GeneratedSqlResponse:
    """
    Convert natural language to SQL query using OpenAI.

    Args:
        name: Database connection name
        input_data: Natural language prompt
        session: Database session

    Returns:
        Generated SQL query with explanation
    """
    # Get connection
    statement = select(DatabaseConnection).where(DatabaseConnection.name == name)
    connection = session.exec(statement).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database connection '{name}' not found",
        )

    # Get metadata for context
    try:
        metadata_obj = await get_cached_metadata(session, connection.name)
        if not metadata_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata not found for database '{name}'. Please refresh metadata first.",
            )
        metadata = json.loads(metadata_obj.metadata_json)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load metadata: {str(e)}",
        )

    # Generate SQL
    try:
        result = await nl2sql_service.generate_sql(input_data.prompt, metadata, connection.db_type)
        return GeneratedSqlResponse(
            sql=result["sql"],
            explanation=result["explanation"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SQL: {str(e)}",
        )
