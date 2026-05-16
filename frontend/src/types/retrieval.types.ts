export interface RetrievedResult {
  id: string;
  tweet_text: string;
  tweet_id: string;
  image_id: string | null;
  disaster_type: string;
  extracted_location: string;
  source_file: string;
  score: number;
  image_base64: string | null;
  image_caption: string;
  image_damage: 'HIGH' | 'MEDIUM' | 'LOW' | '' | null;
  image_info: 'INFORMATIVE' | 'NOT INFORMATIVE' | null;
}

export interface RetrievalRequest {
  query: string;
  top_k?: number;
  filter_disaster_type?: string;
}

export interface RetrievalResponse {
  query: string;
  total_results: number;
  results: RetrievedResult[];
}

export interface CollectionStats {
  collection_name: string;
  total_documents: number;
  disaster_type_breakdown: Record<string, number>;
}
