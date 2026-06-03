import { useEffect, useState } from 'react';
import { Lock, Trash2, ShieldAlert } from 'lucide-react';
import api from '../services/api.js';

export default function Admin() {
  const [email, setEmail] = useState('admin@linkshort.com');
  const [password, setPassword] = useState('admin123');
  const [token, setToken] = useState(localStorage.getItem('adminToken'));
  const [links, setLinks] = useState([]);
  const [stats, setStats] = useState(null);
  const [domain, setDomain] = useState('');
  const [blocked, setBlocked] = useState([]);
  const [error, setError] = useState('');

  const login = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const { data } = await api.post('/auth/login', { email, password });
      localStorage.setItem('adminToken', data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  const loadAdmin = async () => {
    try {
      const [linksRes, statsRes, blockedRes] = await Promise.all([
        api.get('/links'), api.get('/admin/stats'), api.get('/admin/blocked-domains')
      ]);
      setLinks(linksRes.data);
      setStats(statsRes.data);
      setBlocked(blockedRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Please login again');
    }
  };

  useEffect(() => { if (token) loadAdmin(); }, [token]);

  const deleteLink = async (id) => {
    if (!confirm('Delete this link?')) return;
    await api.delete(`/links/${id}`);
    loadAdmin();
  };

  const blockDomain = async (e) => {
    e.preventDefault();
    await api.post('/admin/blocked-domains', { domain, reason: 'Unsafe domain' });
    setDomain('');
    loadAdmin();
  };

  const logout = () => {
    localStorage.removeItem('adminToken');
    setToken(null);
    setLinks([]);
  };

  if (!token) return (
    <section className="panel small-panel">
      <form onSubmit={login}>
        <h3><Lock size={20}/> Admin Login</h3>
        <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Admin email" />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />
        <button className="primary">Login</button>
        {error && <div className="error-box">{error}</div>}
      </form>
    </section>
  );

  return (
    <section className="panel">
      <div className="admin-head"><h3>Admin Dashboard</h3><button onClick={logout}>Logout</button></div>
      {stats && <div className="stats-row">
        <div className="stat-card"><span>Total Links</span><strong>{stats.total_links}</strong></div>
        <div className="stat-card"><span>Active Links</span><strong>{stats.active_links}</strong></div>
        <div className="stat-card"><span>Total Clicks</span><strong>{stats.total_clicks}</strong></div>
        <div className="stat-card"><span>Blocked Domains</span><strong>{stats.blocked_domains}</strong></div>
      </div>}

      <form className="search-row" onSubmit={blockDomain}>
        <input value={domain} onChange={e => setDomain(e.target.value)} placeholder="Block domain e.g. spam.com" required />
        <button className="danger"><ShieldAlert size={18}/> Block Domain</button>
      </form>
      <p className="small">Blocked: {blocked.map(b => b.domain).join(', ') || 'None'}</p>

      <div className="table-wrap">
        <table>
          <thead><tr><th>Short URL</th><th>Original URL</th><th>Clicks</th><th>Password</th><th>Action</th></tr></thead>
          <tbody>
            {links.map(link => <tr key={link.id}>
              <td><a href={link.short_url} target="_blank">{link.slug}</a></td>
              <td className="truncate">{link.original_url}</td>
              <td>{link.click_count}</td>
              <td>{link.has_password ? 'Yes' : 'No'}</td>
              <td><button className="icon-danger" onClick={() => deleteLink(link.id)}><Trash2 size={16}/></button></td>
            </tr>)}
          </tbody>
        </table>
      </div>
    </section>
  );
}
