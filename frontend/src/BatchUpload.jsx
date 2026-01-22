import React, { useState, useRef } from 'react';
import { Upload, X, CheckCircle, AlertCircle, Loader, Folder } from 'lucide-react';
import './BatchUpload.css';

const BatchUpload = ({ onClose, onUploadComplete }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadQueue, setUploadQueue] = useState([]);
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);

  // File status: 'pending', 'uploading', 'parsing', 'indexing', 'success', 'error'
  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files).filter(
      file => file.type === 'application/pdf'
    );
    
    const fileObjects = selectedFiles.map(file => ({
      file,
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      name: file.name,
      size: file.size,
      status: 'pending',
      progress: 0,
      error: null,
      doc_id: null
    }));
    
    setFiles(prev => [...prev, ...fileObjects]);
  };

  const removeFile = (id) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const uploadFile = async (fileObj) => {
    const formData = new FormData();
    formData.append('file', fileObj.file);

    // Update status to uploading
    setFiles(prev => prev.map(f => 
      f.id === fileObj.id ? { ...f, status: 'uploading', progress: 10 } : f
    ));

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();

      // Update to parsing
      setFiles(prev => prev.map(f => 
        f.id === fileObj.id ? { ...f, status: 'parsing', progress: 40 } : f
      ));

      // Simulate parsing time (in reality, backend is processing)
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Update to indexing (auto-indexing happens on backend)
      setFiles(prev => prev.map(f => 
        f.id === fileObj.id ? { 
          ...f, 
          status: 'indexing', 
          progress: 70,
          doc_id: data.doc_id 
        } : f
      ));

      // Wait for indexing to complete
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Success
      setFiles(prev => prev.map(f => 
        f.id === fileObj.id ? { 
          ...f, 
          status: 'success', 
          progress: 100,
          doc_id: data.doc_id
        } : f
      ));

      return data;

    } catch (error) {
      console.error('Upload error:', error);
      setFiles(prev => prev.map(f => 
        f.id === fileObj.id ? { 
          ...f, 
          status: 'error', 
          error: error.message 
        } : f
      ));
      throw error;
    }
  };

  const startBatchUpload = async () => {
    setUploading(true);

    // Process files with concurrency limit (3 at a time)
    const concurrency = 3;
    const pendingFiles = files.filter(f => f.status === 'pending');
    
    for (let i = 0; i < pendingFiles.length; i += concurrency) {
      const batch = pendingFiles.slice(i, i + concurrency);
      await Promise.allSettled(batch.map(file => uploadFile(file)));
    }

    setUploading(false);
    
    // Notify parent of completion
    const successCount = files.filter(f => f.status === 'success').length;
    if (onUploadComplete) {
      onUploadComplete({ total: files.length, success: successCount });
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'uploading':
      case 'parsing':
      case 'indexing':
        return <Loader className="status-icon spinning" size={16} />;
      case 'success':
        return <CheckCircle className="status-icon success" size={16} />;
      case 'error':
        return <AlertCircle className="status-icon error" size={16} />;
      default:
        return null;
    }
  };

  const getStatusText = (fileObj) => {
    switch (fileObj.status) {
      case 'pending':
        return 'Ready to upload';
      case 'uploading':
        return 'Uploading...';
      case 'parsing':
        return 'Parsing document...';
      case 'indexing':
        return 'Indexing for search...';
      case 'success':
        return 'Complete ✓';
      case 'error':
        return fileObj.error || 'Upload failed';
      default:
        return '';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const stats = {
    total: files.length,
    pending: files.filter(f => f.status === 'pending').length,
    processing: files.filter(f => ['uploading', 'parsing', 'indexing'].includes(f.status)).length,
    success: files.filter(f => f.status === 'success').length,
    error: files.filter(f => f.status === 'error').length,
  };

  return (
    <div className="batch-upload-overlay">
      <div className="batch-upload-modal">
        <div className="batch-upload-header">
          <h2>Batch Upload Documents</h2>
          <button className="close-modal" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="batch-upload-actions">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <input
            ref={folderInputRef}
            type="file"
            webkitdirectory="true"
            directory="true"
            multiple
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          
          <button
            className="select-files-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            <Upload size={16} />
            Select Files
          </button>
          
          <button
            className="select-folder-btn"
            onClick={() => folderInputRef.current?.click()}
            disabled={uploading}
          >
            <Folder size={16} />
            Select Folder
          </button>

          {files.length > 0 && !uploading && (
            <button
              className="start-upload-btn"
              onClick={startBatchUpload}
            >
              Upload {stats.pending} File{stats.pending !== 1 ? 's' : ''}
            </button>
          )}
        </div>

        {files.length > 0 && (
          <>
            <div className="batch-stats">
              <div className="stat">
                <span className="stat-label">Total:</span>
                <span className="stat-value">{stats.total}</span>
              </div>
              {stats.processing > 0 && (
                <div className="stat processing">
                  <span className="stat-label">Processing:</span>
                  <span className="stat-value">{stats.processing}</span>
                </div>
              )}
              {stats.success > 0 && (
                <div className="stat success">
                  <span className="stat-label">Completed:</span>
                  <span className="stat-value">{stats.success}</span>
                </div>
              )}
              {stats.error > 0 && (
                <div className="stat error">
                  <span className="stat-label">Failed:</span>
                  <span className="stat-value">{stats.error}</span>
                </div>
              )}
            </div>

            <div className="file-list">
              {files.map(fileObj => (
                <div key={fileObj.id} className={`file-item ${fileObj.status}`}>
                  <div className="file-info">
                    <div className="file-name">{fileObj.name}</div>
                    <div className="file-meta">
                      <span className="file-size">{formatFileSize(fileObj.size)}</span>
                      <span className="file-status">{getStatusText(fileObj)}</span>
                    </div>
                  </div>

                  <div className="file-actions">
                    {getStatusIcon(fileObj.status)}
                    {fileObj.status === 'pending' && !uploading && (
                      <button
                        className="remove-file-btn"
                        onClick={() => removeFile(fileObj.id)}
                      >
                        <X size={14} />
                      </button>
                    )}
                  </div>

                  {['uploading', 'parsing', 'indexing'].includes(fileObj.status) && (
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${fileObj.progress}%` }}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}

        {files.length === 0 && (
          <div className="empty-state">
            <Upload size={48} className="empty-icon" />
            <p>No files selected</p>
            <p className="empty-hint">Click "Select Files" or "Select Folder" to add PDFs</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BatchUpload;
