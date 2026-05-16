import { apiClient } from './client';
import type { RetrievalRequest, RetrievalResponse, CollectionStats } from '../types/retrieval.types';

export const searchRetrieval = (req: RetrievalRequest) =>
  apiClient.post<RetrievalResponse>('/retrieval/search', req).then((r) => r.data);

export const getCollectionStats = () =>
  apiClient.get<CollectionStats>('/retrieval/collection/stats').then((r) => r.data);
