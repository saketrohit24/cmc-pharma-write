import React from 'react';
import { Settings } from 'lucide-react';

export interface CitationSettings {
  hoverableInlineCitations: boolean;
  globalReferencesSection: boolean;
  citationStyle: 'APA' | 'Chicago' | 'IEEE';
}

interface CitationSettingsProps {
  settings: CitationSettings;
  onSettingsChange: (settings: CitationSettings) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export const CitationSettingsPanel: React.FC<CitationSettingsProps> = ({
  settings,
  onSettingsChange,
  isOpen,
  onToggle
}) => {
  const handleSettingChange = (key: keyof CitationSettings, value: boolean | CitationSettings['citationStyle']) => {
    onSettingsChange({
      ...settings,
      [key]: value
    });
  };

  return (
    <div className="citation-settings-container">
      <button 
        className="citation-settings-toggle"
        onClick={onToggle}
        title="Citation Settings"
      >
        <Settings size={16} />
        <span>Citation Settings</span>
      </button>
      
      {isOpen && (
        <div className="citation-settings-panel">
          <div className="citation-settings-header">
            <h3>Citation Settings</h3>
          </div>
          
          <div className="citation-settings-content">
            <div className="setting-group">
              <label className="setting-item">
                <input
                  type="checkbox"
                  checked={settings.hoverableInlineCitations}
                  onChange={(e) => handleSettingChange('hoverableInlineCitations', e.target.checked)}
                />
                <span className="setting-label">☑ Hoverable inline citations</span>
              </label>
            </div>
            
            <div className="setting-group">
              <label className="setting-item">
                <input
                  type="checkbox"
                  checked={settings.globalReferencesSection}
                  onChange={(e) => handleSettingChange('globalReferencesSection', e.target.checked)}
                />
                <span className="setting-label">☑ Global References section</span>
              </label>
            </div>
            
            <div className="setting-group">
              <label className="setting-item-select">
                <span className="setting-label">Citation Style:</span>
                <select
                  value={settings.citationStyle}
                  onChange={(e) => handleSettingChange('citationStyle', e.target.value as CitationSettings['citationStyle'])}
                  className="citation-style-select"
                >
                  <option value="APA">APA</option>
                  <option value="Chicago">Chicago</option>
                  <option value="IEEE">IEEE</option>
                </select>
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
