import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StatsCards from './components/StatsCards';
import QueryStudio from './components/QueryStudio';
import AnomalyDashboard from './components/AnomalyDashboard';
import TicketTable from './components/TicketTable';
import { getStats, getHealth } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('studio');
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);

  const loadOverviewData = async () => {
    try {
      const [statsRes, healthRes] = await Promise.all([getStats(), getHealth()]);
      setStats(statsRes);
      setHealth(healthRes);
    } catch (err) {
      console.error("Failed to connect to backend service", err);
    }
  };

  useEffect(() => {
    loadOverviewData();
  }, []);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header activeTab={activeTab} setActiveTab={setActiveTab} healthInfo={health} onUploadSuccess={loadOverviewData} />

      <main style={{ maxWidth: '1400px', width: '100%', margin: '0 auto', padding: '24px', flex: 1 }}>
        {/* Overview Stats Bar */}
        <StatsCards stats={stats} />

        {/* Dynamic Views */}
        {activeTab === 'studio' && <QueryStudio />}
        {activeTab === 'anomalies' && <AnomalyDashboard />}
        {activeTab === 'explorer' && <TicketTable />}
      </main>

      <footer style={{ borderTop: '1px solid var(--border-color)', padding: '16px 24px', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
        AI Support Ticket System • Built for DOTMappers Assessment • 2026
      </footer>
    </div>
  );
}
