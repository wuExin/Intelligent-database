/** Export dialog component for query result export. */

import React, { useState } from 'react';
import { Modal, Radio, Input, Button, Space, Typography, message, Spin } from 'antd';
import { DownloadOutlined, CloseOutlined } from '@ant-design/icons';
import { downloadExportFile } from '../services/export';

const { Text } = Typography;

interface ExportDialogProps {
  visible: boolean;
  csvUrl?: string | null;
  jsonUrl?: string | null;
  defaultFilename: string;
  rowCount: number;
  onClose: () => void;
}

export const ExportDialog: React.FC<ExportDialogProps> = ({
  visible,
  csvUrl,
  jsonUrl,
  defaultFilename,
  rowCount,
  onClose,
}) => {
  // Debug: Log when component renders
  console.log('[ExportDialog] Render called:', {
    visible,
    hasCsvUrl: !!csvUrl,
    hasJsonUrl: !!jsonUrl,
    csvUrl: csvUrl?.substring(0, 60) + '...',
    jsonUrl: jsonUrl?.substring(0, 60) + '...',
    defaultFilename,
    rowCount
  });

  const [format, setFormat] = useState<'csv' | 'json'>('csv');
  const [filename, setFilename] = useState(defaultFilename);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    if (!csvUrl || !jsonUrl) {
      setError('Export URLs not available');
      return;
    }

    setExporting(true);
    setError(null);

    try {
      const url = format === 'csv' ? csvUrl : jsonUrl;
      const fullFilename = `${filename}.${format}`;

      await downloadExportFile(url, fullFilename);

      message.success(`Exported ${rowCount} rows to ${fullFilename}`);
      onClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Export failed';
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setExporting(false);
    }
  };

  const handleCancel = () => {
    onClose();
  };

  return (
    <Modal
      title={
        <Space direction="vertical" size={4}>
          <Text strong style={{ fontSize: 16 }}>
            Export Query Results
          </Text>
          <Text type="secondary" style={{ fontSize: 13 }}>
            Would you like to export these results to a file?
          </Text>
        </Space>
      }
      open={visible}
      onCancel={handleCancel}
      footer={[
        <Button key="cancel" onClick={handleCancel} disabled={exporting}>
          Cancel
        </Button>,
        <Button
          key="export"
          type="primary"
          icon={exporting ? <Spin size="small" /> : <DownloadOutlined />}
          onClick={handleExport}
          loading={exporting}
          disabled={!csvUrl || !jsonUrl}
        >
          Export {format.toUpperCase()}
        </Button>,
      ]}
      width={500}
      closeIcon={<CloseOutlined />}
    >
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        {/* Row count info */}
        <div>
          <Text type="secondary">Ready to export:</Text>
          <Text strong style={{ marginLeft: 8 }}>
            {rowCount.toLocaleString()} rows
          </Text>
        </div>

        {/* Format selection */}
        <div>
          <Text strong style={{ display: 'block', marginBottom: 8 }}>
            Export Format
          </Text>
          <Radio.Group
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            style={{ width: '100%' }}
            disabled={exporting}
          >
            <Space direction="vertical">
              <Radio value="csv">
                <Space>
                  <Text>CSV</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    (Best for spreadsheets like Excel)
                  </Text>
                </Space>
              </Radio>
              <Radio value="json">
                <Space>
                  <Text>JSON</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    (Best for data processing)
                  </Text>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        {/* Filename input */}
        <div>
          <Text strong style={{ display: 'block', marginBottom: 8 }}>
            Filename
          </Text>
          <Space.Compact style={{ width: '100%' }}>
            <Input
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="Enter filename"
              disabled={exporting}
              maxLength={255}
            />
            <Input
              value={`.${format}`}
              disabled
              style={{ width: 80 }}
            />
          </Space.Compact>
          <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 4 }}>
            File will be saved to your Downloads folder
          </Text>
        </div>

        {/* Error message */}
        {error && (
          <div style={{ padding: '8px 12px', background: '#fff2f0', borderRadius: 4 }}>
            <Text type="danger" style={{ fontSize: 13 }}>
              {error}
            </Text>
          </div>
        )}
      </Space>
    </Modal>
  );
};
