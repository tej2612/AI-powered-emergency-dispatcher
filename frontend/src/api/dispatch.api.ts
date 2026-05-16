import { apiClient } from './client';
import type { DispatcherState } from '../types/dispatch.types';

export const analyzeDispatch = (sessionId: string) =>
  apiClient.post<DispatcherState>('/dispatch/analyze', { session_id: sessionId }).then((r) => r.data);
