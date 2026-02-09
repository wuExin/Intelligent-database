/** Chat panel component for conversational NL query + export flow. */

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Input, Button } from "antd";
import { SendOutlined, LoadingOutlined } from "@ant-design/icons";
import { apiClient } from "../services/api";
import { QueryResult } from "../types/query";
import { ChatMessage, ChatMessageRole, ChatMessageType, ChatMessageData } from "../types/chat";
import { ChatBubble } from "./ChatBubble";
import { downloadExportFile } from "../services/export";

const { TextArea } = Input;

interface ChatPanelProps {
  selectedDatabase: string;
  onQueryResultReady?: (result: QueryResult) => void;
}

function generateId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function parseExportIntent(input: string): "csv" | "json" | "decline" | "unknown" {
  const lower = input.toLowerCase().trim();

  if (/^(不需要|不用|no|取消|算了|cancel|不|nope)/.test(lower)) return "decline";
  if (/json|导出json|export\s*json/.test(lower)) return "json";
  if (/csv|导出csv|export\s*csv/.test(lower)) return "csv";
  if (/^(需要|是|yes|ok|好|导出|export|要|y|sure|好的|嗯|行)/.test(lower)) return "csv";

  return "unknown";
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  selectedDatabase,
  onQueryResultReady,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      type: "text",
      content: "Hello! Describe what you want to query in natural language.\n你好！请用自然语言描述你想查询的内容。",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [awaitingExportResponse, setAwaitingExportResponse] = useState(false);
  const [latestResult, setLatestResult] = useState<QueryResult | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addMessage = useCallback(
    (
      role: ChatMessageRole,
      type: ChatMessageType,
      content: string,
      data?: ChatMessageData
    ) => {
      const msg: ChatMessage = {
        id: generateId(),
        role,
        type,
        content,
        timestamp: new Date(),
        data,
      };
      setMessages((prev) => [...prev, msg]);
      return msg.id;
    },
    []
  );

  const removeMessageByType = useCallback((type: ChatMessageType) => {
    setMessages((prev) => prev.filter((m) => m.type !== type));
  }, []);

  const clientSideExport = useCallback(
    (format: "csv" | "json") => {
      if (!latestResult) return;

      if (format === "csv") {
        const headers = latestResult.columns.map((col) => col.name);
        const csvRows = [headers.join(",")];
        latestResult.rows.forEach((row) => {
          const values = headers.map((header) => {
            const value = row[header];
            if (value === null || value === undefined) return "";
            const str = String(value);
            if (str.includes(",") || str.includes('"') || str.includes("\n")) {
              return `"${str.replace(/"/g, '""')}"`;
            }
            return str;
          });
          csvRows.push(values.join(","));
        });
        const blob = new Blob(["\uFEFF" + csvRows.join("\n")], {
          type: "text/csv;charset=utf-8;",
        });
        triggerDownload(blob, `${selectedDatabase}_query.csv`);
      } else {
        const jsonContent = JSON.stringify(latestResult.rows, null, 2);
        const blob = new Blob([jsonContent], {
          type: "application/json;charset=utf-8;",
        });
        triggerDownload(blob, `${selectedDatabase}_query.json`);
      }
    },
    [latestResult, selectedDatabase]
  );

  const triggerDownload = (blob: Blob, filename: string) => {
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const performExport = useCallback(
    async (format: "csv" | "json") => {
      if (!latestResult) return;

      setIsProcessing(true);
      try {
        const timestamp = new Date()
          .toISOString()
          .replace(/[:.]/g, "-")
          .slice(0, -5);
        const filename = `${selectedDatabase}_${timestamp}.${format}`;

        try {
          if (format === "csv" && latestResult.exportCsvUrl) {
            await downloadExportFile(latestResult.exportCsvUrl, filename);
          } else if (format === "json" && latestResult.exportJsonUrl) {
            await downloadExportFile(latestResult.exportJsonUrl, filename);
          } else {
            clientSideExport(format);
          }
        } catch {
          // Fallback to client-side export if server export fails
          clientSideExport(format);
        }

        addMessage(
          "assistant",
          "export_complete",
          `已导出 ${latestResult.rowCount.toLocaleString()} 行数据为 ${format.toUpperCase()} 格式。`
        );
      } catch (error: any) {
        addMessage(
          "system",
          "error",
          `导出失败: ${error.message || "Unknown error"}`
        );
      } finally {
        setIsProcessing(false);
        setAwaitingExportResponse(false);
      }
    },
    [latestResult, selectedDatabase, addMessage, clientSideExport]
  );

  const handleExportResponse = useCallback(
    async (text: string) => {
      const intent = parseExportIntent(text);

      if (intent === "decline") {
        addMessage("assistant", "text", "好的，如需导出可随时告诉我。");
        setAwaitingExportResponse(false);
        return;
      }

      if (intent === "unknown") {
        addMessage(
          "assistant",
          "text",
          '请回复 "导出CSV"、"导出JSON" 或 "不需要"。'
        );
        return;
      }

      await performExport(intent);
    },
    [addMessage, performExport]
  );

  const handleQuickExport = useCallback(
    async (format: "csv" | "json") => {
      addMessage("user", "export_request", `导出${format.toUpperCase()}`);
      await performExport(format);
    },
    [addMessage, performExport]
  );

  const handleDeclineExport = useCallback(() => {
    addMessage("user", "export_request", "不需要");
    addMessage("assistant", "text", "好的，如需导出可随时告诉我。");
    setAwaitingExportResponse(false);
  }, [addMessage]);

  const handleSend = useCallback(async () => {
    const text = inputValue.trim();
    if (!text || isProcessing) return;
    setInputValue("");

    // Add user message
    addMessage(
      "user",
      awaitingExportResponse ? "export_request" : "nl_prompt",
      text
    );

    // Handle export response
    if (awaitingExportResponse) {
      await handleExportResponse(text);
      return;
    }

    // NL query flow
    setIsProcessing(true);
    try {
      // Step 1: Generate SQL
      const nlResponse = await apiClient.post<{
        sql: string;
        explanation: string;
      }>(`/api/v1/dbs/${selectedDatabase}/query/natural`, { prompt: text });

      // Check if AI determined this is not a database query
      if (nlResponse.data.explanation === "NOT_A_QUERY" || !nlResponse.data.sql) {
        addMessage(
          "assistant",
          "text",
          "这个问题似乎与数据库查询无关。请尝试描述你想从数据库中查询的内容，例如：\n- \"查询所有用户\"\n- \"统计每个部门的人数\"\n- \"最近的订单有哪些\""
        );
        setIsProcessing(false);
        return;
      }

      addMessage("assistant", "sql_generated", nlResponse.data.explanation, {
        sql: nlResponse.data.sql,
        explanation: nlResponse.data.explanation,
      });

      // Step 2: Auto-execute
      addMessage("system", "executing", "Executing query...");

      const queryResponse = await apiClient.post<QueryResult>(
        `/api/v1/dbs/${selectedDatabase}/query`,
        { sql: nlResponse.data.sql }
      );

      removeMessageByType("executing");

      const result = queryResponse.data;
      setLatestResult(result);
      onQueryResultReady?.(result);

      addMessage(
        "assistant",
        "query_result",
        `查询完成: ${result.rowCount} 行, 耗时 ${result.executionTimeMs}ms`,
        { queryResult: result }
      );

      // Step 3: Ask about export
      addMessage(
        "assistant",
        "export_prompt",
        `共 ${result.rowCount.toLocaleString()} 行数据。需要导出吗?`
      );
      setAwaitingExportResponse(true);
    } catch (error: any) {
      removeMessageByType("executing");
      let errorMsg = "An error occurred";
      const detail = error.response?.data?.detail;
      if (typeof detail === "string") {
        errorMsg = detail;
      } else if (Array.isArray(detail)) {
        errorMsg = detail.map((d: any) => d.msg || d.message || JSON.stringify(d)).join("; ");
      } else if (error.message) {
        errorMsg = error.message;
      }
      addMessage("system", "error", errorMsg);
    } finally {
      setIsProcessing(false);
    }
  }, [
    inputValue,
    isProcessing,
    awaitingExportResponse,
    selectedDatabase,
    addMessage,
    removeMessageByType,
    handleExportResponse,
    onQueryResultReady,
  ]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      handleSend();
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* Message feed */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "16px",
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        {messages.map((msg) => (
          <ChatBubble
            key={msg.id}
            message={msg}
            onQuickExport={
              msg.type === "export_prompt" ? handleQuickExport : undefined
            }
            onDeclineExport={
              msg.type === "export_prompt" ? handleDeclineExport : undefined
            }
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div
        style={{
          borderTop: "2px solid #000000",
          padding: "12px 16px",
          background: "#FFFFFF",
          display: "flex",
          gap: 8,
          alignItems: "flex-end",
        }}
      >
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            awaitingExportResponse
              ? "回复 '导出CSV' / '导出JSON' / '不需要'"
              : "用自然语言描述你的查询... (Ctrl+Enter 发送)"
          }
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={isProcessing}
          style={{ flex: 1, borderWidth: 2, borderRadius: 2 }}
        />
        <Button
          type="primary"
          icon={isProcessing ? <LoadingOutlined /> : <SendOutlined />}
          onClick={handleSend}
          loading={isProcessing}
          disabled={!inputValue.trim() || isProcessing}
          style={{ height: 40, fontWeight: 700 }}
        >
          SEND
        </Button>
      </div>
    </div>
  );
};
