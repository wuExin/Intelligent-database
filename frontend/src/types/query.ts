/** Query execution types. */

export interface QueryColumn {
  name: string;
  dataType: string;
}

export interface QueryResult {
  columns: QueryColumn[];
  rows: Record<string, any>[];
  rowCount: number;
  executionTimeMs: number;
  sql: string;
  // Export URLs (optional)
  exportCsvUrl?: string | null;
  exportJsonUrl?: string | null;
  exportExpiresAt?: string | null;
}

export interface QueryInput {
  sql: string;
}

export interface QueryHistoryEntry {
  id: number;
  databaseName: string;
  sqlText: string;
  executedAt: string;
  executionTimeMs?: number | null;
  rowCount?: number | null;
  success: boolean;
  errorMessage?: string | null;
  querySource: "manual" | "natural_language";
}
