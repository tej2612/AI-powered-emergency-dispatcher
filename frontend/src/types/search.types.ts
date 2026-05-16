export interface SearchSource {
  title: string;
  url: string;
  score?: number;
}

export interface SearchResultBlock {
  answer: string;
  results: SearchSource[];
}

export interface SecondarySearchResult {
  query: string;
  results: SearchResultBlock;
}

export interface WebSearchResult {
  enabled: boolean;
  queries?: {
    primary: string;
    secondary: string[];
  };
  primary_results?: SearchResultBlock;
  secondary_results?: SecondarySearchResult[];
  error?: string;
}
