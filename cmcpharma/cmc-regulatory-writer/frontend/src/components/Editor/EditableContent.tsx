import React, { useState } from 'react';

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
}

interface EditableContentProps {
  content: string;
  citations?: Citation[];
  className?: string;
}

export const EditableContent: React.FC<EditableContentProps> = ({
  content,
  citations = [],
  className = ''
}) => {
  const [showCitation, setShowCitation] = useState<number | null>(null);

  // Create a map of citation IDs to citation objects for quick lookup
  const citationMap = citations.reduce((map, citation) => {
    map[citation.id] = citation;
    return map;
  }, {} as Record<number, Citation>);

  // Parse content and render with interactive citations
  const renderContentWithCitations = (text: string) => {
    // Match citation patterns like [1], [2], etc.
    const citationRegex = /\[(\d+)\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = citationRegex.exec(text)) !== null) {
      const citationId = parseInt(match[1]);
      const citation = citationMap[citationId];
      
      // Add text before the citation
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }
      
      // Add the citation as an interactive element
      if (citation) {
        parts.push(
          <span
            key={`citation-${citationId}-${match.index}`}
            className="citation-marker"
            onMouseEnter={() => setShowCitation(citationId)}
            onMouseLeave={() => setShowCitation(null)}
          >
            <span className="inline-flex items-center px-1 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded-full cursor-help hover:bg-blue-200 transition-colors">
              [{citationId}]
            </span>
            {showCitation === citationId && (
              <div className="absolute z-50 p-3 mt-2 max-w-sm bg-white border border-gray-300 rounded-lg shadow-lg">
                <div className="text-sm font-semibold text-gray-900 mb-1">
                  {citation.title}
                </div>
                {citation.authors && (
                  <div className="text-xs text-gray-600 mb-1">
                    Authors: {citation.authors}
                  </div>
                )}
                {citation.source && (
                  <div className="text-xs text-gray-600 mb-1">
                    Source: {citation.source}
                  </div>
                )}
                {citation.year && (
                  <div className="text-xs text-gray-600 mb-1">
                    Year: {citation.year}
                  </div>
                )}
                {citation.url && (
                  <div className="text-xs">
                    <a 
                      href={citation.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      View Source
                    </a>
                  </div>
                )}
              </div>
            )}
          </span>
        );
      } else {
        // Citation not found, render as plain text
        parts.push(match[0]);
      }
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }
    
    return parts;
  };

  // Split content into paragraphs and render each
  const paragraphs = content.split('\n\n').filter(p => p.trim());
  
  return (
    <div className={`relative ${className}`}>
      {paragraphs.map((paragraph, index) => (
        <div key={index} className="mb-4 leading-relaxed">
          {paragraph.split('\n').map((line, lineIndex) => (
            <div key={lineIndex} className="mb-2">
              {renderContentWithCitations(line)}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default EditableContent;
