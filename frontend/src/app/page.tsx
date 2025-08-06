'use client';

import { useState } from 'react';

export default function Home() {
  const [selectedChat, setSelectedChat] = useState('ACE');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAsk = async (query: string) => {
    setLoading(true);
    setAnswer('');

    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setAnswer(data.answer);
    } catch (error) {
      console.error('Error:', error);
      setAnswer('Sorry, there was an error processing your request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const faqQuestions = [
    "How much time did I spend on Project A last month?",
    "What's my average daily productivity?",
    "Which tasks are overdue?",
    "Generate a weekly time report."
  ];

  const chats = [
    "Time spent on project x",
    "Task completed",
    "Weekly progress",
    "Deadlines"
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-blue-100 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-blue-200">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
              <span className="text-white font-bold text-sm">⚡</span>
            </div>
            <div>
              <h1 className="font-semibold text-gray-800">TimeTrack Workspace</h1>
              <p className="text-sm text-gray-600">sainand@updated.com</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-blue-200 cursor-pointer">
            <span className="text-blue-600">⏱️</span>
            <span className="text-gray-700">Timer</span>
          </div>
          
          <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-blue-200 cursor-pointer">
            <span className="text-blue-600">📋</span>
            <span className="text-gray-700">Projects</span>
          </div>
          
          <div className="flex items-center space-x-3 p-2 rounded-lg bg-gray-800 text-white cursor-pointer">
            <span>🤖</span>
            <span>ACE</span>
          </div>
          
          <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-blue-200 cursor-pointer">
            <span className="text-blue-600">📊</span>
            <span className="text-gray-700">Report</span>
          </div>
          
          <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-blue-200 cursor-pointer">
            <span className="text-blue-600">🏢</span>
            <span className="text-gray-700">Organization</span>
          </div>
        </nav>

        {/* Bottom Navigation */}
        <div className="p-4 border-t border-blue-200 space-y-2">
          <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-blue-200 cursor-pointer">
            <span className="text-blue-600">👤</span>
            <span className="text-gray-700">Profile</span>
          </div>
          
          <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-blue-200 cursor-pointer">
            <span className="text-blue-600">🔔</span>
            <span className="text-gray-700">Notification</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Center Panel */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="bg-white border-b border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-800">ACE</h2>
              <button className="text-blue-600 hover:text-blue-800">
                <span className="text-xl">→</span>
              </button>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="flex-1 p-6 overflow-y-auto flex flex-col">
            <h3 className="text-xl font-semibold mb-6 text-gray-800">FAQ</h3>
            
            <div className="space-y-4 mb-8">
              {faqQuestions.map((faq, index) => (
                <button
                  key={index}
                  onClick={() => handleAsk(faq)}
                  className="w-full p-4 text-left bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors duration-200"
                  disabled={loading}
                >
                  <span className="text-gray-700">{faq}</span>
                </button>
              ))}
            </div>

            {/* Answer Display */}
            {(loading || answer) && (
              <div className="mb-6 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-xl">🤖</span>
                  <span className="font-medium text-gray-700">ACE says:</span>
                </div>
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600">Thinking...</span>
                  </div>
                ) : (
                  <p className="text-gray-700 leading-relaxed whitespace-pre-line">{answer}</p>
                )}
              </div>
            )}

            {/* Spacer to push input to bottom */}
            <div className="flex-1"></div>

            {/* Custom Input at Bottom */}
            <div className="mt-auto border-t border-gray-200 pt-4">
              <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask me anything..."
                  className="w-full p-4 border-none rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[60px] text-black placeholder-gray-400"
                  rows={2}
                  disabled={loading}
                  style={{ color: 'black' }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      if (question.trim()) {
                        handleAsk(question);
                        setQuestion('');
                      }
                    }
                  }}
                />
                <div className="flex justify-between items-center px-4 pb-3">
                  <span className="text-xs text-gray-500">Press Enter to send, Shift+Enter for new line</span>
                  <button
                    onClick={() => {
                      if (question.trim()) {
                        handleAsk(question);
                        setQuestion('');
                      }
                    }}
                    disabled={loading || !question.trim()}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                  >
                    {loading ? 'Sending...' : 'Send'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-800">Chats</h3>
              <button className="text-blue-600 hover:text-blue-800">
                <span className="text-sm">✏️ New chat</span>
              </button>
            </div>
          </div>

          {/* Chat List */}
          <div className="flex-1 p-4">
            <div className="space-y-2">
              {chats.map((chat, index) => (
                <div
                  key={index}
                  className="p-3 rounded-lg hover:bg-gray-50 cursor-pointer border border-transparent hover:border-gray-200"
                >
                  <span className="text-gray-700 text-sm">{chat}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
