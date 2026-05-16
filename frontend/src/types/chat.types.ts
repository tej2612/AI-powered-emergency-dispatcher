import type { RetrievedResult } from './retrieval.types';
import type { DispatcherState } from './dispatch.types';
import type { WebSearchResult } from './search.types';

export interface ConversationTurn {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  enable_web_search?: boolean;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  retrieved_results: RetrievedResult[];
  dispatcher_state: DispatcherState;
  web_search: WebSearchResult;
}

export interface HistoryResponse {
  session_id: string;
  history: ConversationTurn[];
  turn_count: number;
}
