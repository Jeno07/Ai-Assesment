import React, { useRef, useState } from 'react';
import { Bot, ShieldAlert, Database, Sparkles, Table, Upload, CheckCircle2 } from 'lucide-react';
import { uploadCSV } from '../services/api';

export default function Header({ activeTab, setActiveTab, healthInfo, onUploadSuccess }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setUploadMsg(null);
    try {
      const res = await uploadCSV(file);
      setUploadMsg(`Uploaded ${res.total_records} rows!`);
      if (onUploadSuccess) onUploadSuccess();
      setTimeout(() => setUploadMsg(null), 4000);
    } catch (err) {
      alert(err.response?.data?.detail || "CSV upload failed");
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <header style={{
      background: 'var(--bg-header)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      padding: '14px 24px'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #a17a74, #8b8878)',
            padding: '10px',
            borderRadius: '10px',
            display: 'flex',
            boxShadow: '0 4px 14px rgba(161, 122, 116, 0.3)'
          }}>
            <Bot size={24} color="#FFF" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#2d3330' }}>
              SupportAI Analytics
            </h1>
            <p style={{ fontSize: '0.75rem', color: '#57615c' }}>
              AI Support Ticket Query & Anomaly Detection Platform
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', background: '#ffffff', padding: '4px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <button
            onClick={() => setActiveTab('studio')}
            className={activeTab === 'studio' ? 'btn-primary' : 'btn-secondary'}
            style={{ borderRadius: '8px', padding: '8px 14px', fontSize: '0.85rem' }}
          >
            <Sparkles size={16} /> AI Query Studio
          </button>
          <button
            onClick={() => setActiveTab('anomalies')}
            className={activeTab === 'anomalies' ? 'btn-primary' : 'btn-secondary'}
            style={{ borderRadius: '8px', padding: '8px 14px', fontSize: '0.85rem' }}
          >
            <ShieldAlert size={16} /> Anomaly Radar
          </button>
          <button
            onClick={() => setActiveTab('explorer')}
            className={activeTab === 'explorer' ? 'btn-primary' : 'btn-secondary'}
            style={{ borderRadius: '8px', padding: '8px 14px', fontSize: '0.85rem' }}
          >
            <Table size={16} /> Ticket Explorer
          </button>
        </nav>

        {/* Upload & Indicators */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.8rem' }}>
          <input
            type="file"
            accept=".csv"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn-secondary"
            disabled={uploading}
            style={{ fontSize: '0.8rem', padding: '6px 14px', background: '#ffffff', borderColor: '#a17a74', color: '#a17a74' }}
          >
            <Upload size={14} /> {uploading ? 'Uploading...' : 'Upload Custom CSV'}
          </button>

          {uploadMsg && (
            <span style={{ color: '#15803d', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
              <CheckCircle2 size={14} /> {uploadMsg}
            </span>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#ffffff', padding: '6px 14px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <Database size={14} color="#a17a74" />
            <span style={{ color: 'var(--text-muted)' }}>DB:</span>
            <span style={{ color: '#a17a74', fontWeight: 700 }}>
              {healthInfo?.database?.total_tickets || 500} Rows
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
