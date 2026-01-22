import React from 'react';
import { FileText, ExternalLink, Target } from 'lucide-react';
import './SearchResults.css';

const SearchResults = ({ results, query, onResultClick, onClose }) => {
  if (!results || results.length === 0) {
    return (
      <div className="search-results-container">
        <div className="search-results-header">
          <h3>Search Results</h3>
          <button className="close-results" onClick={onClose}>×</button>
        </div>
        <div className="no-results">
          <p>No results found for "{query}"</p>
          <p className="no-results-hint">Try different keywords or check if documents are indexed</p>
        </div>
      </div>
    );
  }

  return (
    <div className="search-results-container">
      <div className="search-results-header">
        <h3>Search Results</h3>
        <div className="results-meta">
          <span className="results-count">{results.length} result{results.length !== 1 ? 's' : ''}</span>
          <button className="close-results" onClick={onClose}>×</button>
        </div>
      </div>

      <div className="search-results-list">
        {results.map((result, index) => (
          <div
            key={index}
            className="search-result-card"
            onClick={() => onResultClick(result)}
          >
            <div className="result-header">
              <div className="result-info">
                <FileText size={16} className="result-icon" />
                <span className="result-doc-id">{result.doc_id.substring(0, 8)}...</span>
                <span className="result-separator">•</span>
                <span className="result-page">Page {result.page + 1}</span>
                <span className="result-separator">•</span>
                <span className={`result-type type-${result.chunk_type}`}>
                  {result.chunk_type}
                </span>
              </div>
              <div className="result-score">
                <div className="score-bar-container">
                  <div 
                    className="score-bar" 
                    style={{ width: `${result.similarity_score * 100}%` }}
                  />
                </div>
                <span className="score-text">{(result.similarity_score * 100).toFixed(0)}%</span>
              </div>
            </div>

            <div className="result-text">
              {result.text.substring(0, 300)}
              {result.text.length > 300 && '...'}
            </div>

            <div className="result-actions">
              <button className="jump-to-source">
                <Target size={14} />
                <span>Jump to source</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResults;
