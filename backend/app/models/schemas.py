"""API request/response schemas with camelCase aliases."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Any
from datetime import datetime
from app.models.query import QuerySource


# Database Connection Schemas
class DatabaseConnectionInput(BaseModel):
    """Input schema for creating/updating database connection."""

    url: str = Field(..., description="Database connection URL (PostgreSQL or MySQL)")
    db_type: str | None = Field(default=None, alias="dbType", description="Database type (postgresql or mysql). Auto-detected from URL if not provided.")
    description: str | None = Field(default=None, max_length=200)


class DatabaseConnectionResponse(BaseModel):
    """Response schema for database connection."""

    name: str
    url: str
    db_type: str = Field(..., alias="dbType")
    description: str | None
    created_at: datetime
    updated_at: datetime
    last_connected_at: datetime | None
    status: str


# Metadata Schemas
class ColumnMetadata(BaseModel):
    """Column metadata schema."""

    name: str = Field(..., max_length=63)
    data_type: str = Field(..., alias="dataType")
    nullable: bool
    primary_key: bool = Field(..., alias="primaryKey")
    unique: bool = False
    default_value: str | None = Field(default=None, alias="defaultValue")
    comment: str | None = None


class TableMetadata(BaseModel):
    """Table/View metadata schema."""

    name: str = Field(..., max_length=63)
    type: Literal["table", "view"]
    columns: list[ColumnMetadata]
    row_count: int | None = Field(default=None, alias="rowCount")
    schema_name: str = Field(default="public", alias="schemaName")


class DatabaseMetadataResponse(BaseModel):
    """Response schema for database metadata."""

    database_name: str = Field(..., alias="databaseName")
    tables: list[TableMetadata]
    views: list[TableMetadata]
    fetched_at: datetime = Field(..., alias="fetchedAt")
    is_stale: bool = Field(..., alias="isStale")


# Query Schemas
class QueryInput(BaseModel):
    """Input schema for SQL query execution."""

    sql: str = Field(..., min_length=1, description="SQL SELECT query to execute")


class QueryColumn(BaseModel):
    """Query result column schema."""

    name: str
    data_type: str = Field(..., alias="dataType")


class QueryResult(BaseModel):
    """Query result response schema."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True, by_alias=True)

    columns: list[QueryColumn]
    rows: list[dict[str, Any]]
    row_count: int = Field(..., alias="rowCount")
    execution_time_ms: int = Field(..., alias="executionTimeMs")
    sql: str
    # Export URLs (optional, nullable)
    export_csv_url: str | None = Field(default=None, alias="exportCsvUrl")
    export_json_url: str | None = Field(default=None, alias="exportJsonUrl")
    export_expires_at: datetime | None = Field(default=None, alias="exportExpiresAt")


class QueryHistoryEntry(BaseModel):
    """Query history entry schema."""

    id: int
    database_name: str = Field(..., alias="databaseName")
    sql_text: str = Field(..., alias="sqlText")
    executed_at: datetime = Field(..., alias="executedAt")
    execution_time_ms: int | None = Field(None, alias="executionTimeMs")
    row_count: int | None = Field(None, alias="rowCount")
    success: bool
    error_message: str | None = Field(None, alias="errorMessage")
    query_source: str = Field(..., alias="querySource")


# Natural Language Schemas
class NaturalLanguageInput(BaseModel):
    """Input schema for natural language to SQL conversion."""

    prompt: str = Field(..., min_length=5, max_length=500)


class GeneratedSqlResponse(BaseModel):
    """Response schema for generated SQL."""

    sql: str
    explanation: str


# Error Schema
class ErrorResponse(BaseModel):
    """Error response schema."""

    error: dict[str, Any]


# Export Schemas
class ExportConfig(BaseModel):
    """Export configuration schema."""

    format: str = Field(..., description="Export format (csv or json)")
    filename: str | None = Field(default=None, max_length=255, description="Custom filename (without extension)")
    data_source: str = Field(..., alias="dataSource", description="Source of data (query, tables, table)")
    sql: str | None = Field(default=None, description="SQL query (if dataSource=query)")
    table_name: str | None = Field(default=None, alias="tableName", description="Table name (if dataSource=table)")
    table_names: list[str] | None = Field(default=None, alias="tableNames", description="List of tables (if dataSource=tables)")


class ExportResult(BaseModel):
    """Export result metadata schema."""

    filename: str = Field(..., description="Final filename used")
    format: str = Field(..., description="Format used (csv or json)")
    row_count: int = Field(..., alias="rowCount", description="Total rows exported")
    file_size_bytes: int = Field(..., alias="fileSizeBytes", description="File size in bytes")
    generated_at: datetime = Field(..., alias="generatedAt", description="ISO 8601 timestamp")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")
    table_name: str | None = Field(default=None, alias="tableName", description="Table name (if single table export)")
    table_names: list[str] | None = Field(default=None, alias="tableNames", description="Table names (if multi-table export)")


class ExportUrlResponse(BaseModel):
    """Export URL response schema."""

    export_csv_url: str = Field(..., alias="exportCsvUrl", description="Signed URL for CSV download")
    export_json_url: str = Field(..., alias="exportJsonUrl", description="Signed URL for JSON download")
    expires_at: datetime = Field(..., alias="expiresAt", description="URL expiration timestamp")
    default_filename: str = Field(..., alias="defaultFilename", description="Suggested filename (without extension)")
    row_count: int = Field(..., alias="rowCount", description="Number of rows available for export")
