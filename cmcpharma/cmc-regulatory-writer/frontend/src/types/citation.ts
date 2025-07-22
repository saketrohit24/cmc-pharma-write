/**
 * Citation types for frontend components
 */

export interface Citation {
  id: string;
  text: string;
  source: string;
  page?: number;
  source_file_id?: string;
  url?: string;
  doi?: string;
  authors?: string;
  publication_date?: string;
  journal?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  isbn?: string;
  publisher?: string;
  citation_style?: string;
  tags?: string[];
  notes?: string;
  created_at?: string;
  last_modified?: string;
  title?: string;
  year?: string;
}

export interface CitationCreate {
  text: string;
  source: string;
  page: number;
  source_file_id?: string;
  url?: string;
  doi?: string;
  authors?: string[];
  publication_date?: string;
  journal?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  isbn?: string;
  publisher?: string;
  citation_style?: string;
  tags?: string[];
  notes?: string;
}

export interface CitationResponse {
  citations: Citation[];
}
