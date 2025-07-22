import React from 'react';

interface Citation {
  id: number;
  text: string;
  source: string;
  page: number;
  sourceFileId?: string;
  title?: string;
  authors?: string;
  year?: string;
  url?: string;
  doi?: string;
  journal?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  isbn?: string;
  publisher?: string;
  tags?: string[];
  notes?: string;
}

interface GlobalReferencesProps {
  citations: Citation[];
  className?: string;
}

export const GlobalReferences: React.FC<GlobalReferencesProps> = ({
  citations,
  className = ''
}) => {
  // Sort citations by ID for consistent display
  const sortedCitations = [...citations].sort((a, b) => {
    return a.id - b.id;
  });

  if (citations.length === 0) {
    return (
      <div className={`text-gray-500 italic ${className}`}>
        No references available.
      </div>
    );
  }

  const formatCitation = (citation: Citation): string => {
    const parts = [];
    
    // Authors
    if (citation.authors) {
      parts.push(citation.authors);
    }
    
    // Year
    if (citation.year) {
      parts.push(`(${citation.year})`);
    }
    
    // Title
    if (citation.title) {
      parts.push(`"${citation.title}"`);
    }
    
    // Journal/Source
    if (citation.journal) {
      parts.push(`*${citation.journal}*`);
    } else if (citation.source) {
      parts.push(citation.source);
    }
    
    // Volume/Issue
    if (citation.volume) {
      let volIssue = citation.volume;
      if (citation.issue) {
        volIssue += `(${citation.issue})`;
      }
      parts.push(volIssue);
    }
    
    // Pages
    if (citation.pages) {
      parts.push(`pp. ${citation.pages}`);
    } else if (citation.page) {
      parts.push(`p. ${citation.page}`);
    }
    
    // Publisher
    if (citation.publisher) {
      parts.push(citation.publisher);
    }
    
    return parts.join('. ') + '.';
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <h2 className="text-xl font-bold text-gray-900 mb-4">References</h2>
      <div className="space-y-3">
        {sortedCitations.map((citation) => (
          <div key={citation.id} className="flex gap-3 text-sm leading-relaxed">
            <span className="flex-shrink-0 font-medium text-blue-600 min-w-[2rem]">
              [{citation.id}]
            </span>
            <div className="flex-1">
              <div className="text-gray-800 mb-1">
                {formatCitation(citation)}
              </div>
              
              {/* Additional metadata */}
              <div className="flex flex-wrap gap-4 text-xs text-gray-600">
                {citation.doi && (
                  <span>
                    DOI: 
                    <a 
                      href={`https://doi.org/${citation.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-1 text-blue-600 hover:text-blue-800 underline"
                    >
                      {citation.doi}
                    </a>
                  </span>
                )}
                
                {citation.url && !citation.doi && (
                  <span>
                    URL: 
                    <a 
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-1 text-blue-600 hover:text-blue-800 underline break-all"
                    >
                      {citation.url}
                    </a>
                  </span>
                )}
                
                {citation.isbn && (
                  <span>ISBN: {citation.isbn}</span>
                )}
                
                {citation.sourceFileId && (
                  <span className="bg-gray-100 px-2 py-1 rounded text-gray-700">
                    Source: {citation.sourceFileId}
                  </span>
                )}
              </div>
              
              {/* Tags */}
              {citation.tags && citation.tags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {citation.tags.map((tag, index) => (
                    <span 
                      key={index}
                      className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              
              {/* Notes */}
              {citation.notes && (
                <div className="mt-2 text-xs text-gray-600 italic">
                  Note: {citation.notes}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GlobalReferences;
