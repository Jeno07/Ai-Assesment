import React, { useState, useEffect } from 'react';
import { Search, Filter, RefreshCw, Star } from 'lucide-react';
import { getTickets } from '../services/api';

export default function TicketTable() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchFilteredTickets = async () => {
    setLoading(true);
    try {
      const data = await getTickets({
        category: categoryFilter || undefined,
        priority: priorityFilter || undefined,
        status: statusFilter || undefined,
        limit: 100
      });
      setTickets(data.tickets || []);
    } catch (err) {
      console.error("Failed to load tickets", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFilteredTickets();
  }, [categoryFilter, priorityFilter, statusFilter]);

  const displayedTickets = tickets.filter(t => {
    if (!search.trim()) return true;
    const term = search.toLowerCase();
    return (
      t.ticket_id?.toLowerCase().includes(term) ||
      t.issue_summary?.toLowerCase().includes(term) ||
      t.remarks?.toLowerCase().includes(term) ||
      t.agent_id?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      {/* Header Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Support Tickets Explorer</h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Browse and filter 500 ingested support tickets</p>
        </div>

        {/* Filters & Search */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Search box */}
          <div style={{ position: 'relative', width: '220px' }}>
            <input
              type="text"
              className="input-field"
              placeholder="Search ID, summary, remarks, agent..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '32px', fontSize: '0.85rem' }}
            />
            <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: '10px', top: '12px' }} />
          </div>

          {/* Category dropdown */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="input-field"
            style={{ width: '130px', fontSize: '0.85rem' }}
          >
            <option value="">All Categories</option>
            <option value="Billing">Billing</option>
            <option value="Technical">Technical</option>
            <option value="General">General</option>
          </select>

          {/* Priority dropdown */}
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="input-field"
            style={{ width: '130px', fontSize: '0.85rem' }}
          >
            <option value="">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          {/* Status dropdown */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-field"
            style={{ width: '130px', fontSize: '0.85rem' }}
          >
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Resolved">Resolved</option>
            <option value="Escalated">Escalated</option>
          </select>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <RefreshCw size={24} className="spin" color="#3B82F6" style={{ margin: '0 auto 8px auto' }} />
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Loading tickets data...</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '10px 14px' }}>Ticket ID</th>
                <th style={{ padding: '10px 14px' }}>Created At</th>
                <th style={{ padding: '10px 14px' }}>Category</th>
                <th style={{ padding: '10px 14px' }}>Priority</th>
                <th style={{ padding: '10px 14px' }}>Status</th>
                <th style={{ padding: '10px 14px' }}>Response Time</th>
                <th style={{ padding: '10px 14px' }}>Resol Time</th>
                <th style={{ padding: '10px 14px' }}>Agent</th>
                <th style={{ padding: '10px 14px' }}>Rating</th>
                <th style={{ padding: '10px 14px' }}>Issue Summary</th>
                <th style={{ padding: '10px 14px' }}>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {displayedTickets.map((t) => (
                <tr key={t.ticket_id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#a17a74' }}>
                    {t.ticket_id}
                  </td>
                  <td style={{ padding: '10px 14px', color: '#8b8878', fontSize: '0.8rem' }}>
                    {t.created_at}
                  </td>
                  <td style={{ padding: '10px 14px' }}>{t.category}</td>
                  <td style={{ padding: '10px 14px' }}>
                    <span className={`badge badge-${t.priority?.toLowerCase()}`}>{t.priority}</span>
                  </td>
                  <td style={{ padding: '10px 14px' }}>
                    <span className={`badge badge-${t.status?.toLowerCase()}`}>{t.status}</span>
                  </td>
                  <td style={{ padding: '10px 14px' }}>{t.resp_time_hrs} hrs</td>
                  <td style={{ padding: '10px 14px' }}>
                    {t.resol_time_hrs ? `${t.resol_time_hrs} hrs` : <span style={{ color: 'var(--text-dim)' }}>--</span>}
                  </td>
                  <td style={{ padding: '10px 14px', fontWeight: 500 }}>{t.agent_id}</td>
                  <td style={{ padding: '10px 14px' }}>
                    {t.cust_rating ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '3px', color: t.cust_rating <= 2 ? '#EF4444' : '#FBBF24', fontWeight: 600 }}>
                        <Star size={12} fill="currentColor" /> {t.cust_rating}
                      </span>
                    ) : <span style={{ color: 'var(--text-dim)' }}>--</span>}
                  </td>
                  <td style={{ padding: '10px 14px', maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {t.issue_summary}
                  </td>
                  <td style={{ padding: '10px 14px', maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-muted)' }}>
                    {t.remarks || '--'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
