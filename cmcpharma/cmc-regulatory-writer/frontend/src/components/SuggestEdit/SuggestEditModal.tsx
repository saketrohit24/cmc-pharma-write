import React, { useState, useEffect } from 'react';
import { X, Wand2, Check, AlertCircle } from 'lucide-react';
import { chatService } from '../../services/chatService';

interface SuggestEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  contentType: 'selected' | 'full' | 'section';
  onApply: (suggestedEdit: string) => void;
  sessionId?: string;
  sectionId?: string;
}

export const SuggestEditModal: React.FC<SuggestEditModalProps> = ({
  isOpen,
  onClose,
  content,
  contentType,
  onApply,
  sessionId,
  sectionId
}) => {
  const [suggestedEdit, setSuggestedEdit] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [customPrompt, setCustomPrompt] = useState('');
  const [selectedPreset, setSelectedPreset] = useState<string>('');

  // Preset options for editing
  const presetOptions = [
    {
      id: 'concise',
      label: 'Make it Concise',
      prompt: 'Make this text more concise and to the point while preserving all important information and regulatory requirements.',
      useRAG: false,
      icon: '📝'
    },
    {
      id: 'detailed',
      label: 'Make it More Detailed',
      prompt: 'Expand this text with more detailed explanations, technical details, and comprehensive regulatory information. Include relevant regulatory guidelines and best practices.',
      useRAG: true,
      icon: '📚'
    },
    {
      id: 'technical',
      label: 'More Technical',
      prompt: 'Make this text more technical and precise, using appropriate scientific and regulatory terminology.',
      useRAG: true,
      icon: '🔬'
    },
    {
      id: 'clarity',
      label: 'Improve Clarity',
      prompt: 'Improve the clarity and readability of this text while maintaining technical accuracy and regulatory compliance.',
      useRAG: false,
      icon: '✨'
    },
    {
      id: 'professional',
      label: 'More Professional',
      prompt: 'Rewrite this text in a more professional, formal tone suitable for regulatory submissions.',
      useRAG: false,
      icon: '👔'
    },
    {
      id: 'comprehensive',
      label: 'Make Comprehensive',
      prompt: 'Expand this text to be more comprehensive, including additional regulatory considerations, cross-references, and supporting information.',
      useRAG: true,
      icon: '🎯'
    }
  ];

  const generateSuggestion = React.useCallback(async (prompt?: string, useRAG?: boolean) => {
    if (!content.trim()) {
      setError('No content to edit');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setSuggestedEdit('');

    try {
      const editPrompt = prompt || customPrompt || 'Please improve this text for clarity, accuracy, and regulatory compliance:';
      const shouldUseRAG = useRAG !== undefined ? useRAG : false;
      
      console.log('🤖 Generating suggestion for:', contentType, 'content:', content.substring(0, 100) + '...');
      console.log('🤖 Using RAG:', shouldUseRAG);
      
      const response = await chatService.sendMessage(
        `${editPrompt}\n\nContent to edit:\n${content}\n\nIMPORTANT: Provide ONLY the improved version of the text as plain text. Do NOT use markdown formatting, headers (###), bullet points, or any other formatting. Return only the plain text content that should replace the original.`,
        { 
          sessionId: sessionId || 'suggest-edit-session',
          useRAG: shouldUseRAG
        }
      );

      if (response && response.text && response.text.trim()) {
        let cleanedText = response.text.trim();
        
        // Clean up any markdown formatting that might have been added
        cleanedText = cleanedText.replace(/^### /gm, ''); // Remove header markdown
        cleanedText = cleanedText.replace(/^## /gm, ''); // Remove header markdown
        cleanedText = cleanedText.replace(/^# /gm, ''); // Remove header markdown
        cleanedText = cleanedText.replace(/\*\*(.*?)\*\*/g, '$1'); // Remove bold markdown
        cleanedText = cleanedText.replace(/\*(.*?)\*/g, '$1'); // Remove italic markdown
        
        setSuggestedEdit(cleanedText);
      } else {
        setError('No suggestion generated. Please try again.');
      }
    } catch (err) {
      console.error('Error generating suggestion:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate suggestion');
    } finally {
      setIsGenerating(false);
    }
  }, [content, contentType, sessionId, customPrompt]);

  // Auto-generate suggestion when modal opens
  useEffect(() => {
    if (isOpen && content.trim()) {
      generateSuggestion();
    }
  }, [isOpen, content, generateSuggestion]);

  const handleApply = () => {
    if (suggestedEdit.trim() && content.trim()) {
      console.log('📝 Applying suggested edit:', {
        originalLength: content.length,
        suggestedLength: suggestedEdit.length,
        contentType,
        sectionId
      });
      
      onApply(suggestedEdit.trim());
      onClose();
    }
  };

  const handleClose = () => {
    setSuggestedEdit('');
    setError(null);
    setCustomPrompt('');
    setSelectedPreset('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] mx-4 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            <Wand2 size={20} className="text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Suggest Edit - {contentType === 'selected' ? 'Selected Text' : contentType === 'section' ? 'Section Content' : 'Full Section'}
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 p-4 overflow-y-auto">
          {/* Preset Options */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Choose an editing style:
            </label>
            <div className="grid grid-cols-2 gap-2 mb-4">
              {presetOptions.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => {
                    setSelectedPreset(preset.id);
                    generateSuggestion(preset.prompt, preset.useRAG);
                  }}
                  disabled={isGenerating}
                  className={`p-3 border rounded-lg text-left transition-colors hover:bg-blue-50 hover:border-blue-300 disabled:opacity-50 disabled:cursor-not-allowed ${
                    selectedPreset === preset.id ? 'bg-blue-50 border-blue-300' : 'border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">{preset.icon}</span>
                    <span className="font-medium text-sm">{preset.label}</span>
                    {preset.useRAG && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                        RAG
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-600" style={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>{preset.prompt}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Custom Prompt Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Or use custom instructions:
            </label>
            <div className="flex gap-2">
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="e.g., Make this more technical, Add more examples, Focus on safety aspects..."
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={2}
              />
              <div className="flex flex-col gap-1">
                <button
                  onClick={() => generateSuggestion(customPrompt, false)}
                  disabled={isGenerating || !customPrompt.trim()}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Generate
                </button>
                <button
                  onClick={() => generateSuggestion(customPrompt, true)}
                  disabled={isGenerating || !customPrompt.trim()}
                  className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  + RAG
                </button>
              </div>
            </div>
          </div>

          {/* Original vs Suggested */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Original Content */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                Original Content
                <span className="text-xs text-gray-500">({content.length} chars)</span>
              </h3>
              <div className="border border-gray-300 rounded-lg p-3 bg-gray-50 max-h-64 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                  {content}
                </pre>
              </div>
            </div>

            {/* Suggested Edit */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                Suggested Edit
                {suggestedEdit && (
                  <span className="text-xs text-gray-500">({suggestedEdit.length} chars)</span>
                )}
              </h3>
              <div className="border border-gray-300 rounded-lg p-3 bg-blue-50 max-h-64 overflow-y-auto">
                {isGenerating ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-sm text-gray-600">Generating suggestion...</span>
                  </div>
                ) : error ? (
                  <div className="flex items-center gap-2 text-red-600">
                    <AlertCircle size={16} />
                    <span className="text-sm">{error}</span>
                  </div>
                ) : suggestedEdit ? (
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                    {suggestedEdit}
                  </pre>
                ) : (
                  <div className="text-sm text-gray-500 italic">
                    Suggestion will appear here...
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 text-red-700">
                <AlertCircle size={16} />
                <span className="text-sm font-medium">Error: {error}</span>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t bg-gray-50">
          <div className="text-xs text-gray-500">
            {contentType === 'selected' 
              ? 'This will replace only the selected text' 
              : 'This will replace the entire section content'
            }
            {selectedPreset && (
              <div className="mt-1 text-blue-600">
                Using: {presetOptions.find(p => p.id === selectedPreset)?.label}
                {presetOptions.find(p => p.id === selectedPreset)?.useRAG && ' (with RAG)'}
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              disabled={!suggestedEdit.trim() || isGenerating}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <Check size={16} />
              Apply Suggestion
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SuggestEditModal;
