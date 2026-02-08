"""Filename generation utility for export files."""

import re
from datetime import datetime
from typing import Optional


def generate_filename(
    database: str,
    table: str,
    timestamp: Optional[datetime] = None,
    format: str = "csv",
    sequence: Optional[int] = None
) -> str:
    """
    Generate export filename using pattern: {database}_{table}_{timestamp}.{format}

    Args:
        database: Database connection name
        table: Table name or 'query' for query results
        timestamp: Datetime object (defaults to now)
        format: File format (csv, json, zip)
        sequence: Optional sequence number if filename conflict

    Returns:
        Sanitized filename with extension

    Examples:
        >>> generate_filename("mydb", "users", format="csv")
        "mydb_users_20250208_143052.csv"

        >>> generate_filename("mydb", "users", format="csv", sequence=1)
        "mydb_users_20250208_143052_1.csv"
    """
    if timestamp is None:
        timestamp = datetime.utcnow()

    # Format timestamp as YYYYMMDD_HHMMSS
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

    # Sanitize components
    sanitized_db = sanitize_filename(database)
    sanitized_table = sanitize_filename(table)

    # Build base filename
    components = [sanitized_db, sanitized_table, timestamp_str]
    if sequence is not None:
        components.append(str(sequence))

    base_filename = "_".join(components)

    # Add extension
    return f"{base_filename}.{format}"


def sanitize_filename(name: str) -> str:
    """
    Sanitize filename by removing invalid filesystem characters.

    Rules:
    - Remove invalid chars: < > : " / \ | ? *
    - Replace spaces with underscores
    - Convert to lowercase
    - Limit to 100 characters (per component)

    Args:
        name: Original filename component

    Returns:
        Sanitized filename component
    """
    # Remove invalid filesystem characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)

    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')

    # Convert to lowercase
    sanitized = sanitized.lower()

    # Limit to 100 characters
    if len(sanitized) > 100:
        sanitized = sanitized[:100]

    # Remove any remaining whitespace
    sanitized = sanitized.strip()

    return sanitized


def validate_filename(filename: str) -> tuple[bool, Optional[str]]:
    """
    Validate filename meets requirements.

    Args:
        filename: Filename to validate (with or without extension)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty"

    # Check length (before sanitization, max 255 chars)
    if len(filename) > 255:
        return False, "Filename cannot exceed 255 characters"

    # Check if empty after sanitization
    sanitized = sanitize_filename(filename)
    if not sanitized:
        return False, "Filename contains no valid characters"

    return True, None
