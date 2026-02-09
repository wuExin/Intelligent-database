/** Chat bubble component for rendering individual messages. */

import React from "react";
import { Typography, Button, Space, Spin } from "antd";
import {
  CheckCircleFilled,
  CloseCircleFilled,
  DownloadOutlined,
  CodeOutlined,
} from "@ant-design/icons";
import { ChatMessage } from "../types/chat";

const { Text, Paragraph } = Typography;

interface ChatBubbleProps {
  message: ChatMessage;
  onQuickExport?: (format: "csv" | "json") => void;
  onDeclineExport?: () => void;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  message,
  onQuickExport,
  onDeclineExport,
}) => {
  const isUser = message.role === "user";

  // Container alignment
  const containerStyle: React.CSSProperties = {
    display: "flex",
    justifyContent: isUser ? "flex-end" : "flex-start",
    marginBottom: 4,
  };

  // Base bubble style
  const baseBubble: React.CSSProperties = {
    maxWidth: "85%",
    padding: "10px 14px",
    borderRadius: 2,
    border: "2px solid #000000",
    fontSize: 14,
    lineHeight: 1.6,
  };

  // User bubble
  if (isUser) {
    return (
      <div style={containerStyle}>
        <div style={{ ...baseBubble, background: "#EBF9FF" }}>
          <Text>{message.content}</Text>
        </div>
      </div>
    );
  }

  // Executing / loading
  if (message.type === "executing") {
    return (
      <div style={containerStyle}>
        <div
          style={{
            ...baseBubble,
            background: "#F8F8F7",
            borderColor: "#D9D9D9",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <Spin size="small" />
          <Text type="secondary">{message.content}</Text>
        </div>
      </div>
    );
  }

  // SQL generated
  if (message.type === "sql_generated") {
    return (
      <div style={containerStyle}>
        <div style={{ ...baseBubble, background: "#FFFFFF" }}>
          <Text>{message.content}</Text>
          {message.data?.sql && (
            <div
              style={{
                marginTop: 8,
                background: "#1e1e1e",
                borderRadius: 2,
                padding: "10px 12px",
                position: "relative",
              }}
            >
              <CodeOutlined
                style={{
                  position: "absolute",
                  top: 8,
                  right: 8,
                  color: "#666",
                  fontSize: 12,
                }}
              />
              <Paragraph
                copyable={{ text: message.data.sql }}
                style={{
                  color: "#d4d4d4",
                  fontFamily: "monospace",
                  fontSize: 13,
                  whiteSpace: "pre-wrap",
                  margin: 0,
                }}
              >
                {message.data.sql}
              </Paragraph>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Query result
  if (message.type === "query_result") {
    return (
      <div style={containerStyle}>
        <div
          style={{
            ...baseBubble,
            background: "#FFFFFF",
            borderColor: "#16AA98",
          }}
        >
          <Space>
            <CheckCircleFilled style={{ color: "#16AA98", fontSize: 16 }} />
            <Text strong>{message.content}</Text>
          </Space>
        </div>
      </div>
    );
  }

  // Export prompt with quick action buttons
  if (message.type === "export_prompt") {
    return (
      <div style={containerStyle}>
        <div style={{ ...baseBubble, background: "#FFFFFF" }}>
          <Text>{message.content}</Text>
          <Space style={{ marginTop: 10, display: "flex", flexWrap: "wrap" }}>
            <Button
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => onQuickExport?.("csv")}
              style={{ fontWeight: 700, borderWidth: 2 }}
            >
              EXPORT CSV
            </Button>
            <Button
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => onQuickExport?.("json")}
              style={{ fontWeight: 700, borderWidth: 2 }}
            >
              EXPORT JSON
            </Button>
            <Button
              size="small"
              onClick={onDeclineExport}
              style={{ fontWeight: 700, borderWidth: 2, borderColor: "#D9D9D9", color: "#666" }}
            >
              NO THANKS
            </Button>
          </Space>
        </div>
      </div>
    );
  }

  // Export complete
  if (message.type === "export_complete") {
    return (
      <div style={containerStyle}>
        <div
          style={{
            ...baseBubble,
            background: "#F6FFED",
            borderColor: "#16AA98",
          }}
        >
          <Space>
            <CheckCircleFilled style={{ color: "#16AA98", fontSize: 16 }} />
            <Text strong>{message.content}</Text>
          </Space>
        </div>
      </div>
    );
  }

  // Error
  if (message.type === "error") {
    return (
      <div style={containerStyle}>
        <div
          style={{
            ...baseBubble,
            background: "#FFF2F0",
            borderColor: "#FF4D4F",
          }}
        >
          <Space>
            <CloseCircleFilled style={{ color: "#FF4D4F", fontSize: 16 }} />
            <Text type="danger">{message.content}</Text>
          </Space>
        </div>
      </div>
    );
  }

  // Default text bubble (assistant/system)
  return (
    <div style={containerStyle}>
      <div style={{ ...baseBubble, background: "#FFFFFF" }}>
        <Text>{message.content}</Text>
      </div>
    </div>
  );
};
