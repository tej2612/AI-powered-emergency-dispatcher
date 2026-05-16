import { apiClient } from './client';
import type { ChatRequest, ChatResponse, HistoryResponse } from '../types/chat.types';

export const sendMessage = (req: ChatRequest) =>
  apiClient.post<ChatResponse>('/chat/', req).then((r) => r.data);

export const clearSession = (sessionId: string) =>
  apiClient.delete(`/chat/${sessionId}`).then((r) => r.data);

export const getHistory = (sessionId: string) =>
  apiClient.get<HistoryResponse>(`/chat/${sessionId}/history`).then((r) => r.data);
