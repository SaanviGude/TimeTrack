'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import { Sidebar } from '../../components/Sidebar';
import { projectService } from '../../services/projectService';
import '../../styles/dashboard.css';

interface ChatMessage {
  id: string;
  question: string;
  answer: string;
  timestamp: Date;
}

export default function AcePage() {
  const { user } = useAuth();
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<any[]>([]);

  const predefinedQuestions = [
    "How much time did I spend on Project A last month?",
    "What's my average daily productivity?",
    "Which tasks are overdue?",
    "Generate a weekly time report"
  ];

  useEffect(() => {
    if (user) {
      // Load user projects for context
      const userProjects = projectService.getProjectsByUserId(user.id);
      setProjects(userProjects);
    }
  }, [user]);

  const generateAnswer = async (question: string): Promise<string> => {
    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: question }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.answer || 'Sorry, I could not process your request at this time.';
    } catch (error) {
      console.error('Error calling AI API:', error);
      return 'Sorry, there was an error processing your request. Please try again later.';
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    
    try {
      const answer = await generateAnswer(question.trim());
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        question: question.trim(),
        answer,
        timestamp: new Date()
      };
      
      setChatHistory(prev => [newMessage, ...prev]);
      setQuestion('');
    } catch (error) {
      console.error('Error in handleAsk:', error);
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        question: question.trim(),
        answer: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date()
      };
      setChatHistory(prev => [errorMessage, ...prev]);
      setQuestion('');
    } finally {
      setLoading(false);
    }
  };

  const handlePredefinedQuestion = (predefinedQ: string) => {
    setQuestion(predefinedQ);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
    <ProtectedRoute>
      <div className="dashboard-container">
        <Sidebar activeItem="ACE" />
        
        <div className="main-content">
          {/* Header */}
          <header className="content-header">
            <div className="header-content">
              <div>
                <h1 className="header-title">ACE</h1>
                <p className="header-subtitle">AI-powered project insights and analytics</p>
              </div>
            </div>
          </header>

          <main className="content-main">
            {/* FAQ Section */}
            <div className="ace-section">
              <div className="faq-header">
                <h2 className="section-title">FAQ</h2>
                <p className="section-subtitle">Quick answers to common questions</p>
              </div>
              
              <div className="faq-grid">
                {predefinedQuestions.map((q, index) => (
                  <button
                    key={index}
                    onClick={() => handlePredefinedQuestion(q)}
                    className="faq-button"
                  >
                    <span className="faq-icon">❓</span>
                    <span className="faq-text">{q}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Chat Interface */}
            <div className="ace-section">
              <div className="chat-container">
                <div className="chat-input-section">
                  <h3 className="chat-title">Ask me anything about your projects</h3>
                  <div className="input-group">
                    <textarea
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      placeholder="Ask me anything..."
                      className="chat-textarea"
                      rows={3}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleAsk();
                        }
                      }}
                    />
                    <div className="input-actions">
                      <span className="input-hint">Press Enter to send, Shift+Enter for new line</span>
                      <button
                        onClick={handleAsk}
                        disabled={loading || !question.trim()}
                        className="send-button"
                      >
                        {loading ? (
                          <span className="loading-text">
                            <div className="loading-spinner"></div>
                            Thinking...
                          </span>
                        ) : (
                          <span>Send</span>
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Chat History */}
                {chatHistory.length > 0 && (
                  <div className="chat-history">
                    <h3 className="chat-title">Recent Conversations</h3>
                    <div className="chat-messages">
                      {chatHistory.map((message) => (
                        <div key={message.id} className="chat-message">
                          <div className="message-header">
                            <span className="message-time">
                              {formatTime(message.timestamp)}
                            </span>
                          </div>
                          
                          <div className="question-bubble">
                            <div className="bubble-header">
                              <span className="user-icon">👤</span>
                              <span className="user-label">You asked:</span>
                            </div>
                            <p className="question-text">{message.question}</p>
                          </div>
                          
                          <div className="answer-bubble">
                            <div className="bubble-header">
                              <span className="ace-icon">🤖</span>
                              <span className="ace-label">ACE responds:</span>
                            </div>
                            <div className="answer-text">
                              {message.answer.split('\n').map((line, index) => (
                                <p key={index} className={line.trim() ? '' : 'empty-line'}>
                                  {line || '\u00A0'}
                                </p>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Empty State */}
                {chatHistory.length === 0 && !loading && (
                  <div className="chat-empty-state">
                    <div className="empty-icon">🤖</div>
                    <h3 className="empty-title">Start a conversation with ACE</h3>
                    <p className="empty-subtitle">
                      Ask questions about your projects, productivity, or try one of the FAQ options above
                    </p>
                  </div>
                )}
              </div>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
