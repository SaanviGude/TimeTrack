// src/app/ace/page.tsx
'use client';

import { useState } from 'react';

export default function AceChat() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setLoading(true);
    setAnswer('');

    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question }),
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

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-3xl mx-auto bg-white shadow-md p-6 rounded-lg">
        <h1 className="text-2xl font-bold mb-4">🧠 ACE AI Chat Assistant</h1>

        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={4}
          placeholder="Ask something like: What was my most productive day last week?"
          className="w-full p-3 border rounded mb-4"
        />

        <button
          onClick={handleAsk}
          disabled={loading || !question}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Thinking...' : 'Ask ACE'}
        </button>

        {answer && (
          <div className="mt-6 p-4 bg-gray-50 border rounded">
            <strong>🗨️ AI says:</strong>
            <p className="mt-2">{answer}</p>
          </div>
        )}
      </div>
    </main>
  );
}
