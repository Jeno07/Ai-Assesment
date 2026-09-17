import React from 'react';
import { Ticket, AlertCircle, CheckCircle2, Clock, Star, Flame } from 'lucide-react';

export default function StatsCards({ stats }) {
  if (!stats) return null;

  const cardItems = [
    {
      title: 'Total Ingested Tickets',
      value: stats.total_tickets || 500,
      sub: '500 records indexed',
      icon: <Ticket size={22} color="#8b8878" />,
      bgClass: 'card-variant-1',
      iconBg: '#f0ede6'
    },
    {
      title: 'Active Open / Escalated',
      value: stats.open_tickets || 0,
      sub: `${stats.critical_tickets || 0} Critical priority`,
      icon: <AlertCircle size={22} color="#d97706" />,
      bgClass: 'card-variant-2',
      iconBg: '#fff7ed'
    },
    {
      title: 'Resolved Tickets',
      value: stats.resolved_tickets || 0,
      sub: `${Math.round(((stats.resolved_tickets || 0)/(stats.total_tickets || 1))*100)}% resolution rate`,
      icon: <CheckCircle2 size={22} color="#a17a74" />,
      bgClass: 'card-variant-3',
      iconBg: '#faf0ee'
    },
    {
      title: 'Avg Resolution Time',
      value: `${stats.avg_resol_time_hrs || 0} hrs`,
      sub: `Avg Response: ${stats.avg_resp_time_hrs || 0} hrs`,
      icon: <Clock size={22} color="#8b8878" />,
      bgClass: 'card-variant-4',
      iconBg: '#f5f0eb'
    },
    {
      title: 'Avg Customer Rating',
      value: `${stats.avg_rating || 0} / 5.0`,
      sub: 'Post-resolution CSAT',
      icon: <Star size={22} color="#a17a74" />,
      bgClass: 'card-variant-1',
      iconBg: '#faf0ee'
    }
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
      gap: '16px',
      marginBottom: '24px'
    }}>
      {cardItems.map((item, idx) => (
        <div key={idx} className={`glass-card ${item.bgClass}`} style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', color: '#57615c', fontWeight: 600 }}>
              {item.title}
            </span>
            <div style={{ background: item.iconBg, padding: '8px', borderRadius: '8px' }}>
              {item.icon}
            </div>
          </div>
          <div style={{ fontSize: '1.7rem', fontWeight: 800, color: '#2d3330', marginBottom: '4px' }}>
            {item.value}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#8b8878', fontWeight: 500 }}>
            {item.sub}
          </div>
        </div>
      ))}
    </div>
  );
}
