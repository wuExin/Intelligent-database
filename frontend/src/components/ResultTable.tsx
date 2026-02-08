/** Query result table component with pagination. */

import React, { useState, useEffect, useRef } from "react";
import { Table, Tag } from "antd";
import { QueryResult } from "../types/query";
import { ExportDialog } from "./ExportDialog";

interface ResultTableProps {
  result: QueryResult | null;
  loading?: boolean;
}

export const ResultTable: React.FC<ResultTableProps> = ({
  result,
  loading = false,
}) => {
  // Debug: Log when ResultTable component renders
  console.log('[ResultTable] Render called:', {
    hasResult: !!result,
    loading,
    resultRowCount: result?.rowCount,
    hasExportCsvUrl: !!result?.exportCsvUrl,
    hasExportJsonUrl: !!result?.exportJsonUrl,
    exportCsvUrl: result?.exportCsvUrl?.substring(0, 60) + '...',
    exportJsonUrl: result?.exportJsonUrl?.substring(0, 60) + '...'
  });

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 50,
  });

  // Track export prompt state
  const [showExportPrompt, setShowExportPrompt] = useState(false);
  const exportPromptShownRef = useRef<string | null>(null);

  // Debug: Track showExportPrompt state changes
  useEffect(() => {
    console.log('[ResultTable] showExportPrompt state changed:', showExportPrompt);
  }, [showExportPrompt]);

  // Show export dialog when result has export URLs and prompt hasn't been shown yet
  useEffect(() => {
    console.log('[ResultTable] useEffect triggered:', {
      hasResult: !!result,
      loading,
      hasExportCsvUrl: !!result?.exportCsvUrl,
      hasExportJsonUrl: !!result?.exportJsonUrl,
      shouldShow: !!(result && !loading && (result.exportCsvUrl || result.exportJsonUrl))
    });

    if (
      result &&
      !loading &&
      (result.exportCsvUrl || result.exportJsonUrl)
    ) {
      // Use execution time + SQL to create a unique ID for each query execution
      const resultId = `${result.executionTimeMs}-${result.sql}`;

      // Only show if we haven't shown a prompt for this result
      if (exportPromptShownRef.current !== resultId) {
        console.log('[ResultTable] Export URLs detected, showing dialog:', {
          hasCsvUrl: !!result.exportCsvUrl,
          hasJsonUrl: !!result.exportJsonUrl,
          csvUrl: result.exportCsvUrl?.substring(0, 60) + '...',
          jsonUrl: result.exportJsonUrl?.substring(0, 60) + '...',
          resultId
        });
        setShowExportPrompt(true);
        exportPromptShownRef.current = resultId;
      } else {
        console.log('[ResultTable] Dialog already shown for this result, skipping');
      }
    }
  }, [result, loading]);

  if (!result) {
    return null;
  }

  const columns = result.columns.map((col) => ({
    title: col.name,
    dataIndex: col.name,
    key: col.name,
    render: (value: any) => {
      if (value === null || value === undefined) {
        return <Tag color="default">NULL</Tag>;
      }
      if (typeof value === "boolean") {
        return value ? "✓" : "✗";
      }
      if (value instanceof Date) {
        return value.toLocaleString();
      }
      return String(value);
    },
  }));

  const handleTableChange = (newPagination: any) => {
    setPagination({
      current: newPagination.current,
      pageSize: newPagination.pageSize,
    });
  };

  const handleCloseExportDialog = () => {
    setShowExportPrompt(false);
  };

  // Extract default filename from export URLs
  const getDefaultFilename = (): string => {
    if (result.exportCsvUrl) {
      // Extract filename from URL (it will be in the format)
      // For now, generate a default based on result metadata
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
      return `query_${timestamp}`;
    }
    return 'export';
  };

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Tag color="blue">Rows: {result.rowCount}</Tag>
        <Tag color="green">Execution Time: {result.executionTimeMs}ms</Tag>
      </div>
      <Table
        columns={columns}
        dataSource={result.rows.map((row, index) => ({
          ...row,
          key: index,
        }))}
        loading={loading}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: result.rowCount,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} rows`,
          pageSizeOptions: ["10", "50", "100", "500"],
        }}
        onChange={handleTableChange}
        scroll={{ x: "max-content" }}
      />

      {/* Export Dialog */}
      {(result.exportCsvUrl || result.exportJsonUrl) && (
        <ExportDialog
          visible={showExportPrompt}
          csvUrl={result.exportCsvUrl}
          jsonUrl={result.exportJsonUrl}
          defaultFilename={getDefaultFilename()}
          rowCount={result.rowCount}
          onClose={handleCloseExportDialog}
        />
      )}
    </div>
  );
};
