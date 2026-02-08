/** Export service for file downloads. */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Download an export file from the given URL.
 *
 * @param url - The export URL (signed)
 * @param filename - The filename to save as
 * @throws Error if download fails
 */
export async function downloadExportFile(
  url: string,
  filename: string
): Promise<void> {
  try {
    // Build full URL if relative path
    const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;

    console.log('[Export] Downloading from:', fullUrl);

    const response = await fetch(fullUrl);

    console.log('[Export] Response status:', response.status);
    console.log('[Export] Response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      console.error('[Export] Request failed:', response.status, response.statusText);

      if (response.status === 401) {
        throw new Error('Export link has expired. Please refresh your query results.');
      } else if (response.status === 404) {
        throw new Error('Database or table not found.');
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Export failed. Please try again.');
      }
    }

    // Get blob from response
    const blob = await response.blob();

    // Create temporary link
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();

    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('An unexpected error occurred during download.');
  }
}

/**
 * Export all tables from a database.
 *
 * @param databaseName - The database connection name
 * @param format - Export format ('csv' or 'json')
 * @returns Promise with export result
 */
export async function exportAllTables(
  databaseName: string,
  format: 'csv' | 'json'
): Promise<MultiFileExportResponse | void> {
  try {
    // This endpoint is not yet implemented, placeholder for now
    const url = `/api/v1/dbs/${databaseName}/export/tables?format=${format}`;
    const response = await fetch(url, {
      headers: {
        // Add auth headers if needed
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to export tables: ${response.statusText}`);
    }

    const contentType = response.headers.get('content-type');

    // If ZIP file, trigger download
    if (contentType?.includes('zip')) {
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${databaseName}_tables.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    } else {
      // JSON response with multiple file URLs
      const data: MultiFileExportResponse = await response.json();
      return data;
    }
  } catch (error) {
    console.error('Error exporting all tables:', error);
    throw error;
  }
}

/**
 * Export a single table.
 *
 * @param databaseName - The database connection name
 * @param tableName - The table name
 * @param format - Export format
 * @param filename - Optional custom filename
 */
export async function exportTable(
  databaseName: string,
  tableName: string,
  format: 'csv' | 'json',
  filename?: string
): Promise<void> {
  const url = new URL(`/api/v1/dbs/${databaseName}/export/table/${tableName}`, window.location.origin);

  // This will need a token in production
  // url.searchParams.set('token', token);
  url.searchParams.set('format', format);
  if (filename) {
    url.searchParams.set('filename', filename);
  }

  const defaultFilename = filename || `${databaseName}_${tableName}.${format}`;

  await downloadExportFile(url.toString(), defaultFilename);
}

/**
 * Types for export responses.
 */
export interface MultiFileExportResponse {
  files: ExportFile[];
  expiresAt: string;
}

export interface ExportFile {
  tableName: string;
  url: string;
  filename: string;
  rowCount: number;
}
