/** Chat message types for the conversational NL query interface. */

import { QueryResult } from "./query";

export type ChatMessageRole = "user" | "assistant" | "system";

export type ChatMessageType =
  | "nl_prompt"
  | "sql_generated"
  | "executing"
  | "query_result"
  | "export_prompt"
  | "export_request"
  | "export_complete"
  | "error"
  | "text";

export interface ChatMessageData {
  sql?: string;
  explanation?: string;
  queryResult?: QueryResult;
  exportFormat?: "csv" | "json";
  filename?: string;
}

export interface ChatMessage {
  id: string;
  role: ChatMessageRole;
  type: ChatMessageType;
  content: string;
  timestamp: Date;
  data?: ChatMessageData;
}
