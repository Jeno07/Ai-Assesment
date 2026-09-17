import React, { useState, useEffect } from 'react';
import { ShieldAlert, AlertTriangle, Clock, UserX, TrendingDown, CheckCircle, RefreshCw } from 'lucide-react';
import { getAnomalies } from '../services/api';

export default function AnomalyDashboard() {
  const [anomaliesData, setAnomaliesData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('ALL');

  const fetchAnomalies = async () => {
    setLoading(true);
    try {
      const data = await getAnomalies();
      setAnomaliesData(data);
    } catch (err) {
      console.error("Failed to load anomalies", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnomalies();
  }, []);

  if (loading) {
    return (
      <div className="glass-card" style={{ padding: '40px', textAlign: 'center' }}>
        <RefreshCw size={24} className="spin" color="#3B82F6" style={{ margin: '0 auto 12px auto' }} />
        <p style={{ color: 'var(--text-muted)' }}>Scanning 500 support tickets for statistical & rule anomalies...</p>
      </div>
    );
  }

  if (!anomaliesData) return null;

  const { summary, anomalies } = anomaliesData;
  const filteredAnomalies = severityFilter === 'ALL' 
    ? anomalies 
    : anomalies.filter(a => a.severity === severityFilter);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header Summary Banner */}
      <div className="glass-card glow-effect" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <ShieldAlert size={24} color="#EF4444" />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Support Operations Anomaly Radar</h2>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Automated detection of resolution time outliers (Z-Score / IQR), unresolved high-priority SLA risks, and agent rating anomalies.
            </p>
          </div>

          {/* Quick Health Meter */}
          <div style={{ display: 'flex', gap: '16px', background: 'var(--bg-elevated)', padding: '12px 20px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block' }}>System Health Score</span>
              <span style={{ fontSize: '1.4rem', fontWeight: 700, color: summary.overall_health_score > 70 ? '#10B981' : '#F59E0B' }}>
                {summary.overall_health_score} / 100
              </span>
            </div>
            <div style={{ borderLeft: '1px solid var(--border-color)', paddingLeft: '16px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block' }}>Total Anomalies Flagged</span>
              <span style={{ fontSize: '1.4rem', fontWeight: 700, color: '#EF4444' }}>
                {summary.total_anomalies}
              </span>
            </div>
          </div>
        </div>

        {/* Severity Filter Buttons */}
        <div style={{ display: 'flex', gap: '10px', marginTop: '20px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>Filter Severity:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={severityFilter === sev ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '4px 12px', fontSize: '0.75rem' }}
            >
              {sev} {sev === 'CRITICAL' && `(${summary.critical_count})`} {sev === 'HIGH' && `(${summary.high_count})`} {sev === 'MEDIUM' && `(${summary.medium_count})`}
            </button>
          ))}
          <button onClick={fetchAnomalies} className="btn-secondary" style={{ marginLeft: 'auto', padding: '4px 10px', fontSize: '0.75rem' }}>
            <RefreshCw size={14} /> Refresh Scan
          </button>
        </div>
      </div>

      {/* Anomaly Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '16px' }}>
        {filteredAnomalies.map((item, index) => {
          const cardVariantClass = index % 3 === 0 ? 'card-variant-1' : index % 3 === 1 ? 'card-variant-3' : 'card-variant-4';
          return (
            <div
              key={item.id}
              className={`glass-card ${cardVariantClass}`}
              style={{
                padding: '20px',
                borderLeft: `4px solid ${
                  item.severity === 'CRITICAL' ? '#b91c1c' : item.severity === 'HIGH' ? '#d97706' : '#a17a74'
                }`
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                <span className={`badge badge-${item.severity.toLowerCase()}`}>
                  {item.severity}
                </span>
                <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: '#a17a74', fontWeight: 700 }}>
                  {item.ticket_id}
                </span>
              </div>

              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#2d3330', marginBottom: '8px' }}>
                {item.type}
              </h3>

              <p style={{ fontSize: '0.85rem', color: '#57615c', marginBottom: '12px', lineHeight: 1.4 }}>
                {item.description}
              </p>

              <div style={{
                background: '#ffffff',
                padding: '8px 12px',
                borderRadius: '6px',
                fontSize: '0.8rem',
                display: 'flex',
                justify: 'space-between',
                alignItems: 'center',
                border: '1px solid var(--border-color)'
              }}>
                <span style={{ color: '#8b8878' }}>Agent: <strong>{item.agent_id}</strong></span>
                <span style={{ color: '#b91c1c', fontWeight: 700 }}>{item.metric_value}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
