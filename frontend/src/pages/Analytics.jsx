import { useState } from 'react';
import { Search } from 'lucide-react';
import api from '../services/api.js';

export default function Analytics() {
  const [slug, setSlug] = useState('');
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const load = async (e) => {
    e.preventDefault();
    setError('');
    setData(null);
    try {
      const res = await api.get(`/links/slug/${slug}/analytics`);
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analytics not found');
    }
  };

  const metricList = (title, obj) => (
    <div className="metric-box">
      <h4>{title}</h4>
      {Object.keys(obj || {}).length === 0 && <p>No data yet</p>}
      {Object.entries(obj || {}).map(([key, value]) => <div className="metric-line" key={key}><span>{key}</span><b>{value}</b></div>)}
    </div>
  );

  return (
    <section className="panel">
      <form onSubmit={load} className="search-row">
        <input value={slug} onChange={e => setSlug(e.target.value)} placeholder="Enter slug e.g. abc123" required />
        <button className="primary"><Search size={18}/> View Analytics</button>
      </form>
      {error && <div className="error-box">{error}</div>}
      {data && <>
        <div className="stats-row">
          <div className="stat-card"><span>Total Clicks</span><strong>{data.total_clicks}</strong></div>
          <div className="stat-card"><span>Short URL</span><strong className="url-text">{data.link.short_url}</strong></div>
          <div className="stat-card"><span>Original URL</span><strong className="url-text">{data.link.original_url}</strong></div>
        </div>
        <div className="analytics-grid">
          {metricList('Browsers', data.browsers)}
          {metricList('Devices', data.devices)}
          {metricList('Operating Systems', data.operating_systems)}
          {metricList('Referrers', data.referrers)}
        </div>
        <h3>Recent Clicks</h3>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Time</th><th>Browser</th><th>Device</th><th>OS</th><th>Referrer</th></tr></thead>
            <tbody>
              {data.recent_clicks.map((c, i) => <tr key={i}><td>{new Date(c.clicked_at).toLocaleString()}</td><td>{c.browser}</td><td>{c.device}</td><td>{c.os}</td><td>{c.referrer}</td></tr>)}
            </tbody>
          </table>
        </div>
      </>}
    </section>
  );
}
