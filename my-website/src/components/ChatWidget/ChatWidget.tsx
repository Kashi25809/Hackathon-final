import React, { useState, useRef, useEffect } from 'react';
import './ChatWidget.css';

interface Source {
  title: string;
  file_path: string;
  module: string;
  score: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string | JSX.Element; // Allow JSX for the welcome message
  sources?: Source[];
}

interface ChatWidgetProps {
  apiUrl?: string;
}

export default function ChatWidget({ apiUrl = 'http://localhost:8000' }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Initial Welcome Message matching the screenshot
  const initialMessage: Message = {
    role: 'assistant',
    content: (
      <div>
        <p>👋 Hi! I'm your <strong>Physical AI & Humanoid Robotics</strong> assistant.</p>
        <p>I can help you with:</p>
        <ul style={{ paddingLeft: '20px', margin: '8px 0' }}>
          <li>ROS 2 and robotics middleware</li>
          <li>Digital twin simulation</li>
          <li>NVIDIA Isaac and navigation</li>
          <li>Vision-Language-Action systems</li>
        </ul>
        <p style={{ marginTop: '12px', fontSize: '0.9em', opacity: 0.9 }}>
          💡 <strong>Tip:</strong> Select any text on the page, then ask me about it!
        </p>
      </div>
    )
  };

  const [messages, setMessages] = useState<Message[]>([initialMessage]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  // Handle Text Selection
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection()?.toString();
      if (selection && selection.length > 0 && isOpen) {
        // Optional: you could auto-fill input or show a popup. 
        // For now, let's just focus input if they select something? 
        // Or leave it passive as per "Tip".
      }
    };
    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    const newMessages = [...messages, { role: 'user', content: userMessage } as Message];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      // Detect selection context
      const selection = window.getSelection()?.toString();
      let queryToSend = userMessage;
      if (selection) {
        queryToSend = `Context: "${selection}"\n\nQuestion: ${userMessage}`;
      }

      const messageHistory = newMessages
        .filter(m => typeof m.content === 'string') // Filter out JSX messages for backend
        .map(msg => ({
          role: msg.role,
          content: msg.content as string
        }));

      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: queryToSend,
          messages: messageHistory,
          top_k: 5,
          include_sources: true
        }),
      });

      if (!response.ok) throw new Error('Failed');
      const data = await response.json();

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I lost connection to the robot brain (backend). Please check if it\'s running.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([initialMessage]);
  };

  const formatSourcePath = (path: string) => {
    return `/docs/${path.replace('.md', '').replace(/\\/g, '/')}`;
  };

  return (
    <div className="chat-widget-container" style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 999999 }}>
      {/* Toggle Button (Floating Icon) */}
      {!isOpen && (
        <button
          className="chat-toggle-btn"
          onClick={() => setIsOpen(true)}
        >
          <span style={{ fontSize: '24px' }}>🤖</span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window-frame">
          {/* Header */}
          <div className="chat-header-bar">
            <div className="header-title">
              <span className="robot-icon">🤖</span>
              <span>Physical AI Assistant</span>
            </div>
            <div className="header-actions">
              <button onClick={handleClear} title="Clear Conversation" className="icon-btn">🗑️</button>
              <button onClick={() => setIsOpen(false)} title="Close" className="icon-btn">✕</button>
            </div>
          </div>

          {/* Messages */}
          <div className="chat-message-list">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.role}`}>
                <div className="bubble-content">
                  {msg.content}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources-list">
                    <span>Sources:</span>
                    <ul>
                      {msg.sources.map((src, i) => (
                        <li key={i}>
                          <a href={formatSourcePath(src.file_path)} target="_blank" rel="noopener noreferrer">{src.title}</a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="chat-bubble assistant">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form onSubmit={handleSubmit} className="chat-input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about robotics, ROS 2, or AI..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !input.trim()} className="send-btn">
              ➤
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
