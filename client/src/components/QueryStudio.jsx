import React, { useState } from 'react';
import { Sparkles, Send, Terminal, Cpu, AlertCircle, Database, Check } from 'lucide-react';
import { queryNaturalLanguage } from '../services/api';

const SAMPLE_QUERIES = [
  "How many critical tickets are unresolved?",
  "Which agent has the lowest average customer rating?",
  "What is the average customer rating for Technical category tickets?",
  "Show me all Critical tickets not resolved within 12 hours.",
  "Which agent resolved the most tickets?",
  "Are there any anomalies in resolution times?"
];

export default function QueryStudio() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [queryResult, setQueryResult] = useState(null);
  const [error, setError] = useState(null);

  const handleQuery = async (queryToRun) => {
    const targetQ = queryToRun || question;
    if (!targetQ.strip && !targetQ.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await queryNaturalLanguage(targetQ);
      setQueryResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error processing query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Prompt Card */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
          <Sparkles size={20} color="#3B82F6" />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Natural Language AI Query Studio</h2>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Ask natural language questions about your support tickets. The LLM engine will dynamically translate your intent into structured SQL queries and explain the results.
        </p>

        {/* Input bar */}
        <form onSubmit={(e) => { e.preventDefault(); handleQuery(); }} style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
          <input
            type="text"
            className="input-field"
            placeholder="e.g. How many critical tickets are unresolved?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button type="submit" className="btn-primary" disabled={loading} style={{ whiteSpace: 'nowrap' }}>
            {loading ? <Cpu className="spin" size={18} /> : <Send size={18} />}
            {loading ? 'Analyzing...' : 'Ask AI'}
          </button>
        </form>

        {/* Sample query pills */}
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '8px' }}>
            Sample Assessment Queries:
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {SAMPLE_QUERIES.map((q, idx) => (
              <button
                key={idx}
                onClick={() => { setQuestion(q); handleQuery(q); }}
                className="btn-secondary"
                style={{ fontSize: '0.75rem', padding: '6px 12px' }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="glass-card" style={{ padding: '16px 20px', borderColor: 'rgba(239, 68, 68, 0.4)', background: 'rgba(239, 68, 68, 0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#F87171' }}>
            <AlertCircle size={18} />
            <span style={{ fontWeight: 600 }}>Query Error</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>{error}</p>
        </div>
      )}

      {/* Result Presentation */}
      {queryResult && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Answer Card & SQL Generated */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
            
            {/* Natural Language Synthesis - Black Chat Box */}
            <div className="chat-response-box" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffd39b', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Sparkles size={18} color="#ffd39b" /> AI Chat Answer
                </span>
                <span style={{ fontSize: '0.75rem', color: '#cdb79e', background: '#1c1917', padding: '3px 10px', borderRadius: '6px', border: '1px solid #333333' }}>
                  {queryResult.provider}
                </span>
              </div>
              <div style={{ fontSize: '1.05rem', color: '#ffffff', lineHeight: 1.6, fontWeight: 500 }}>
                {queryResult.answer}
              </div>
            </div>

            {/* Executed SQL Query */}
            <div className="glass-card" style={{ padding: '20px', background: '#ffffff' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#57615c', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Terminal size={16} color="#a17a74" /> Executed SQL Query
                </span>
                <span style={{ fontSize: '0.75rem', color: '#15803d', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
                  <Check size={14} /> Validated SQL
                </span>
              </div>
              <pre style={{
                background: '#111827',
                padding: '14px',
                borderRadius: '8px',
                color: '#ffd39b',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.85rem',
                overflowX: 'auto',
                border: '1px solid #374151'
              }}>
                {queryResult.sql_query}
              </pre>
            </div>
          </div>

          {/* Result Data Table */}
          <div className="glass-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Database size={16} /> Query Execution Results ({queryResult.results_count} records)
              </h3>
            </div>

            {queryResult.results && queryResult.results.length > 0 ? (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                      {Object.keys(queryResult.results[0]).map((col) => (
                        <th key={col} style={{ padding: '10px 14px', fontWeight: 600 }}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {queryResult.results.map((row, rIdx) => (
                      <tr key={rIdx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', transition: 'background 0.15s' }}>
                        {Object.entries(row).map(([k, val], cIdx) => (
                          <td key={cIdx} style={{ padding: '10px 14px' }}>
                            {k === 'status' ? (
                              <span className={`badge badge-${val?.toLowerCase()}`}>{val}</span>
                            ) : k === 'priority' ? (
                              <span className={`badge badge-${val?.toLowerCase()}`}>{val}</span>
                            ) : (
                              val !== null && val !== undefined ? String(val) : <span style={{ color: 'var(--text-dim)' }}>null</span>
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No rows returned by this query.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
