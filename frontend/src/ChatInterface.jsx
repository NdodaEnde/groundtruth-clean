import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, X, Sparkles, FileText, Loader } from 'lucide-react';
import './ChatInterface.css';

const ChatInterface = ({ onClose, onDocumentClick }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hi! I can answer questions about your uploaded documents. Ask me anything!',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.content,
          conversation_history: messages.slice(-6) // Last 3 exchanges
        })
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      const data = await response.json();

      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error processing your question. Please try again.",
        error: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSourceClick = (source) => {
    if (onDocumentClick) {
      onDocumentClick(source.doc_id, source.chunk_id);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="chat-overlay">
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-header-content">
            <Sparkles size={20} />
            <h3>Ask GroundTruth</h3>
          </div>
          <button className="chat-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="chat-messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role} ${message.error ? 'error' : ''}`}
            >
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <div className="sources-label">Sources:</div>
                    {message.sources.map((source, idx) => (
                      <div
                        key={idx}
                        className="source-item"
                        onClick={() => handleSourceClick(source)}
                      >
                        <FileText size={14} />
                        <div className="source-info">
                          <div className="source-doc">{source.filename || `Doc ${source.doc_id.substring(0, 8)}`}</div>
                          <div className="source-meta">
                            Page {source.page + 1} • {source.chunk_type}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="message-time">{formatTime(message.timestamp)}</div>
            </div>
          ))}

          {isLoading && (
            <div className="message assistant loading">
              <div className="message-content">
                <Loader className="loading-spinner" size={16} />
                <span>Thinking...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            className="chat-input"
            placeholder="Ask a question about your documents..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="chat-send"
            disabled={!input.trim() || isLoading}
          >
            <Send size={18} />
          </button>
        </form>

        <div className="chat-suggestions">
          <span className="suggestions-label">Try asking:</span>
          <button
            className="suggestion-chip"
            onClick={() => setInput("Which certificates are expiring soon?")}
            disabled={isLoading}
          >
            Which certificates are expiring soon?
          </button>
          <button
            className="suggestion-chip"
            onClick={() => setInput("Summarize all fitness certificates")}
            disabled={isLoading}
          >
            Summarize all fitness certificates
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
