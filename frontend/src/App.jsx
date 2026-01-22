import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { Upload, FileText, ZoomIn, ZoomOut, AlertCircle, Loader, MessageSquare } from 'lucide-react';
import axios from 'axios';
import SearchBar from './SearchBar';
import SearchResults from './SearchResults';
import BatchUpload from './BatchUpload';
import ChatInterface from './ChatInterface';
import './App.css';

// Configure PDF.js worker - use unpkg for better reliability
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';

import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

const API_BASE = '/api';

function App() {
  // Document state
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [selectedFilename, setSelectedFilename] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  
  // PDF state
  const [numPages, setNumPages] = useState(null);
  const [pdfScale, setPdfScale] = useState(1.0);
  const [pageSize, setPageSize] = useState({ width: 0, height: 0 });
  
  // Overview state
  const [chunks, setChunks] = useState([]);
  const [selectedChunkId, setSelectedChunkId] = useState(null);
  const [hoveredChunkId, setHoveredChunkId] = useState(null);
  
  // Panel state
  const [leftWidth, setLeftWidth] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  
  // Batch upload state
  const [showBatchUpload, setShowBatchUpload] = useState(false);
  
  // Chat state
  const [showChat, setShowChat] = useState(false);
  
  // Refs
  const containerRef = useRef(null);
  const pdfContainerRef = useRef(null);
  const pageRef = useRef(null);
  const overviewScrollRef = useRef(null);
  const chunkRefs = useRef({});

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  // Load documents list
  const loadDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE}/documents`);
      setDocuments(response.data.documents || []);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  // Handle file upload
  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setDocuments(prev => [...prev, response.data]);
      setSelectedDocId(response.data.doc_id);
      setSelectedFilename(file.name);
      
      // Load chunks
      await loadDocumentChunks(response.data.doc_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  // Load document chunks
  const loadDocumentChunks = async (docId) => {
    try {
      const response = await axios.get(`${API_BASE}/document/${docId}/chunks`);
      setChunks(response.data.chunks || []);
    } catch (err) {
      console.error('Failed to load chunks:', err);
      setError('Failed to load document chunks');
    }
  };

  // Search documents
  const handleSearch = async (query) => {
    setIsSearching(true);
    setSearchQuery(query);
    
    try {
      const response = await axios.post(`${API_BASE}/query`, {
        query: query,
        n_results: 10
      });
      
      setSearchResults(response.data.results || []);
      setShowSearchResults(true);
    } catch (err) {
      console.error('Search failed:', err);
      setError('Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  // Clear search
  const handleClearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchResults(false);
  };

  // Jump to source from search result
  const handleSearchResultClick = async (result) => {
    // Load the document
    setSelectedDocId(result.doc_id);
    setSelectedFilename(`Document ${result.doc_id.substring(0, 8)}`);
    
    // Load chunks for this document
    await loadDocumentChunks(result.doc_id);
    
    // Wait a bit for chunks to load, then scroll to it
    setTimeout(() => {
      const chunkIndex = chunks.findIndex(c => c.chunk_id === result.chunk_id);
      if (chunkIndex !== -1) {
        const chunkId = `chunk_${chunkIndex}`;
        handleChunkClick(chunkId, result.grounding, chunkIndex);
      }
    }, 500);
    
    // Close search results
    setShowSearchResults(false);
  };

  // Handle batch upload completion
  const handleBatchUploadComplete = ({ total, success }) => {
    // Reload documents list
    loadDocuments();
    
    // Close modal after a delay
    setTimeout(() => {
      setShowBatchUpload(false);
    }, 1500);
  };

  // Handle document click from chat sources
  const handleChatDocumentClick = async (docId, chunkId) => {
    // Load the document
    setSelectedDocId(docId);
    
    // Find filename
    const doc = documents.find(d => d.doc_id === docId);
    setSelectedFilename(doc?.filename || `Document ${docId.substring(0, 8)}`);
    
    // Load chunks
    await loadDocumentChunks(docId);
    
    // Find and highlight the chunk
    setTimeout(() => {
      const chunkIndex = chunks.findIndex(c => c.chunk_id === chunkId);
      if (chunkIndex !== -1) {
        const chunkIdStr = `chunk_${chunkIndex}`;
        const chunk = chunks[chunkIndex];
        handleChunkClick(chunkIdStr, chunk.grounding, chunkIndex);
      }
    }, 500);
  };

  // Handle document selection
  const handleDocumentSelect = async (docId, filename) => {
    setSelectedDocId(docId);
    setSelectedFilename(filename);
    setSelectedChunkId(null);
    setHoveredChunkId(null);
    await loadDocumentChunks(docId);
  };

  // PDF options
  const pdfOptions = useMemo(() => ({
    cMapUrl: 'https://unpkg.com/pdfjs-dist@3.11.174/cmaps/',
    cMapPacked: true,
  }), []);

  // PDF load handlers
  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
  };

  const onPageLoadSuccess = (page) => {
    setPageSize({
      width: page.width,
      height: page.height
    });
  };

  // Zoom controls
  const zoomIn = () => setPdfScale(prev => Math.min(prev + 0.2, 2.0));
  const zoomOut = () => setPdfScale(prev => Math.max(prev - 0.2, 0.5));

  // Scroll chunk into view in Overview panel
  const scrollToChunk = useCallback((chunkId) => {
    const chunkElement = chunkRefs.current[chunkId];
    const scrollContainer = overviewScrollRef.current;
    
    if (chunkElement && scrollContainer) {
      const containerRect = scrollContainer.getBoundingClientRect();
      const elementRect = chunkElement.getBoundingClientRect();
      
      const containerCenter = containerRect.height / 2;
      const elementCenter = elementRect.height / 2;
      const scrollTop = scrollContainer.scrollTop + (elementRect.top - containerRect.top) - containerCenter + elementCenter;
      
      scrollContainer.scrollTo({
        top: scrollTop,
        behavior: 'smooth'
      });
    }
  }, []);

  // Scroll PDF to highlight region
  const scrollToHighlightedRegion = useCallback((chunk) => {
    if (!chunk.grounding || !pdfContainerRef.current || !pageRef.current) return;
    
    const g = chunk.grounding;
    const container = pdfContainerRef.current;
    const containerHeight = container.clientHeight;
    const singlePageHeight = pageRef.current.clientHeight;
    
    // For continuous scrolling
    const pageNumber = g.page; // 0-indexed
    const marginBetweenPages = 16;
    
    const scrollToPage = (singlePageHeight + marginBetweenPages) * pageNumber;
    const regionCenterY = (g.box.top + (g.box.bottom - g.box.top) / 2) * singlePageHeight;
    const scrollTop = scrollToPage + regionCenterY - containerHeight / 2;
    
    container.scrollTo({
      top: Math.max(0, scrollTop),
      behavior: 'smooth'
    });
  }, []);

  // Handle chunk click
  const handleChunkClick = (chunkId, grounding, chunkIndex) => {
    const wasSelected = selectedChunkId === chunkId;
    setSelectedChunkId(wasSelected ? null : chunkId);
    
    if (!wasSelected && grounding && grounding.page !== undefined) {
      const chunk = chunks[chunkIndex];
      setTimeout(() => scrollToHighlightedRegion(chunk), 200);
    }
    
    if (!wasSelected) {
      setTimeout(() => scrollToChunk(chunkId), 100);
    }
  };

  // Handle chunk hover
  const handleChunkHover = (chunkId) => {
    setHoveredChunkId(chunkId);
  };

  const handleChunkUnhover = () => {
    setHoveredChunkId(null);
  };

  // Resizable divider handlers
  const handleMouseDown = (e) => {
    setIsDragging(true);
    e.preventDefault();
  };

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || !containerRef.current) return;
    
    e.preventDefault();
    e.stopPropagation();
    
    const container = containerRef.current;
    const containerRect = container.getBoundingClientRect();
    const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    
    const clampedWidth = Math.max(30, Math.min(70, newLeftWidth));
    setLeftWidth(clampedWidth);
  }, [isDragging]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const pdfUrl = selectedDocId ? `${API_BASE}/document/${selectedDocId}/pdf` : null;

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>⚡ GroundTruth</h2>
          <p className="tagline">Paperless Vision</p>
        </div>

        <div className="sidebar-section">
          <h3>📁 Documents</h3>
          <div className="upload-buttons">
            <label className="upload-button">
              <Upload size={16} />
              {uploading ? 'Uploading...' : 'Upload PDF'}
              <input
                type="file"
                accept=".pdf"
                onChange={handleUpload}
                disabled={uploading}
                style={{ display: 'none' }}
              />
            </label>
            <button 
              className="batch-upload-button"
              onClick={() => setShowBatchUpload(true)}
              disabled={uploading}
            >
              <Upload size={16} />
              Batch Upload
            </button>
            <button 
              className="chat-button"
              onClick={() => setShowChat(true)}
            >
              <MessageSquare size={16} />
              Ask Questions
            </button>
          </div>
        </div>

        <div className="sidebar-section" style={{ flex: 1, overflowY: 'auto' }}>
          {documents.length === 0 ? (
            <p className="empty-state">No documents yet</p>
          ) : (
            <div className="document-list">
              {documents.map(doc => (
                <div
                  key={doc.doc_id}
                  className={`document-item ${selectedDocId === doc.doc_id ? 'active' : ''}`}
                  onClick={() => handleDocumentSelect(doc.doc_id, doc.filename)}
                >
                  <FileText size={16} />
                  <span className="document-name">{doc.filename}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {error && (
          <div className="sidebar-section error-message">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Search Bar */}
        <SearchBar 
          onSearch={handleSearch}
          onClear={handleClearSearch}
          isSearching={isSearching}
        />

        {/* Content Container */}
        <div className="content-container">
          {selectedDocId ? (
          <div 
            ref={containerRef}
            className="viewer-container"
            style={{ cursor: isDragging ? 'col-resize' : 'default' }}
          >
            {/* Left Panel - PDF Viewer */}
            <div 
              className="pdf-panel"
              style={{ width: `${leftWidth}%` }}
            >
              <div className="pdf-header">
                <h3>
                  <FileText size={16} />
                  {selectedFilename}
                </h3>
                {numPages && (
                  <div className="pdf-controls">
                    <span className="page-info">
                      {numPages} page{numPages > 1 ? 's' : ''} • {Math.round(pdfScale * 100)}%
                    </span>
                    <button onClick={zoomOut} className="icon-button">
                      <ZoomOut size={16} />
                    </button>
                    <button onClick={zoomIn} className="icon-button">
                      <ZoomIn size={16} />
                    </button>
                  </div>
                )}
              </div>

              <div className="pdf-container" ref={pdfContainerRef}>
                {pdfUrl ? (
                  <Document
                    file={pdfUrl}
                    onLoadSuccess={onDocumentLoadSuccess}
                    options={pdfOptions}
                    loading={
                      <div className="pdf-loading">
                        <Loader className="spinner" size={32} />
                        <p>Loading PDF...</p>
                      </div>
                    }
                    error={
                      <div className="pdf-error">
                        <AlertCircle size={32} />
                        <p>Failed to load PDF</p>
                      </div>
                    }
                  >
                    {/* Render all pages for continuous scrolling */}
                    {Array.from(new Array(numPages), (el, index) => {
                      const currentPage = index + 1;
                      return (
                        <div 
                          key={`page_${currentPage}`} 
                          className="pdf-page"
                          ref={currentPage === 1 ? pageRef : null}
                        >
                          <Page 
                            pageNumber={currentPage} 
                            scale={pdfScale}
                            renderTextLayer={false}
                            renderAnnotationLayer={false}
                            onLoadSuccess={currentPage === 1 ? onPageLoadSuccess : undefined}
                          />
                          
                          {/* Grounding boxes overlay */}
                          {pageSize.width > 0 && chunks.length > 0 && (
                            <div className="grounding-overlay">
                              {chunks
                                .filter(chunk => chunk.grounding && (chunk.grounding.page + 1) === currentPage)
                                .map((chunk, idx) => {
                                  const chunkIndex = chunks.indexOf(chunk);
                                  const chunkId = `chunk_${chunkIndex}`;
                                  const isSelected = selectedChunkId === chunkId;
                                  const isHovered = hoveredChunkId === chunkId;
                                  
                                  const box = chunk.grounding.box;
                                  if (!box) return null;
                                  
                                  return (
                                    <div
                                      key={chunkId}
                                      className={`grounding-box ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
                                      style={{
                                        left: `${box.left * 100}%`,
                                        top: `${box.top * 100}%`,
                                        width: `${(box.right - box.left) * 100}%`,
                                        height: `${(box.bottom - box.top) * 100}%`,
                                      }}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleChunkClick(chunkId, chunk.grounding, chunkIndex);
                                      }}
                                      onMouseEnter={() => handleChunkHover(chunkId)}
                                      onMouseLeave={handleChunkUnhover}
                                    />
                                  );
                                })}
                            </div>
                          )}
                          
                          <div className="page-number">
                            Page {currentPage} of {numPages}
                          </div>
                        </div>
                      );
                    })}
                  </Document>
                ) : (
                  <div className="pdf-empty">
                    <FileText size={48} />
                    <p>No document selected</p>
                  </div>
                )}
              </div>
            </div>

            {/* Resizable Divider */}
            <div
              className="divider"
              onMouseDown={handleMouseDown}
            />

            {/* Right Panel - Overview */}
            <div 
              className="overview-panel"
              style={{ width: `${100 - leftWidth}%` }}
            >
              <div className="overview-header">
                <h3>📄 Document Overview</h3>
                <p className="subtitle">
                  {chunks.length} section{chunks.length !== 1 ? 's' : ''} • Click to view in PDF
                </p>
              </div>

              <div className="overview-content" ref={overviewScrollRef}>
                {chunks.length > 0 ? (
                  chunks.map((chunk, idx) => {
                    const chunkId = `chunk_${idx}`;
                    const isSelected = selectedChunkId === chunkId;
                    const isHovered = hoveredChunkId === chunkId;
                    
                    return (
                      <div
                        key={idx}
                        id={chunkId}
                        ref={el => chunkRefs.current[chunkId] = el}
                        className={`chunk-card ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
                        onClick={() => handleChunkClick(chunkId, chunk.grounding, idx)}
                        onMouseEnter={() => handleChunkHover(chunkId)}
                        onMouseLeave={handleChunkUnhover}
                      >
                        <div className="chunk-header">
                          <span className="chunk-page">
                            {chunk.grounding?.page !== undefined ? `Page ${chunk.grounding.page + 1}` : 'N/A'}
                          </span>
                          <span className="chunk-type">{chunk.chunk_type || 'text'}</span>
                        </div>
                        <div 
                          className="chunk-content"
                          dangerouslySetInnerHTML={{ __html: chunk.text || 'No content' }}
                        />
                      </div>
                    );
                  })
                ) : (
                  <p className="empty-state">No chunks available</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="welcome-screen">
            <div className="welcome-content">
              <Upload size={64} className="welcome-icon" />
              <h1>Welcome to GroundTruth</h1>
              <p className="welcome-tagline">Paperless Vision: See What Matters</p>
              <p className="welcome-description">
                Transform legacy documents into searchable, grounded intelligence
              </p>
              <div className="welcome-features">
                <div className="feature">✓ AI-powered document parsing</div>
                <div className="feature">✓ Visual grounding with exact locations</div>
                <div className="feature">✓ Interactive PDF navigation</div>
                <div className="feature">✓ Semantic search across documents</div>
              </div>
            </div>
          </div>
        )}
        </div>

        {/* Search Results Overlay */}
        {showSearchResults && (
          <SearchResults 
            results={searchResults}
            query={searchQuery}
            onResultClick={handleSearchResultClick}
            onClose={handleClearSearch}
          />
        )}

        {/* Batch Upload Modal */}
        {showBatchUpload && (
          <BatchUpload 
            onClose={() => setShowBatchUpload(false)}
            onUploadComplete={handleBatchUploadComplete}
          />
        )}

        {/* Chat Interface */}
        {showChat && (
          <ChatInterface 
            onClose={() => setShowChat(false)}
            onDocumentClick={handleChatDocumentClick}
          />
        )}
      </div>
    </div>
  );
}

export default App;
