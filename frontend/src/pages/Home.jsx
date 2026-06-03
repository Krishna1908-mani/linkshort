import { useState } from 'react';
import { CalendarDays, Copy, Download, KeyRound, Link2, QrCode, Wand2 } from 'lucide-react';
import api from '../services/api.js';

export default function Home() {
  const [form, setForm] = useState({
    original_url: '',
    custom_alias: '',
    password: '',
    expires_at: '',
    redirect_type: 302,
    slug_length: 7,
    generate_qr: true
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const update = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const payload = {
        ...form,
        custom_alias: form.custom_alias || null,
        password: form.password || null,
        expires_at: form.expires_at ? new Date(form.expires_at).toISOString() : null,
        redirect_type: Number(form.redirect_type),
        slug_length: Number(form.slug_length),
      };
      const { data } = await api.post('/links/shorten', payload);
      setResult(data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'object') {
        setError(detail.message || 'Something went wrong');
      } else {
        setError(detail || 'Something went wrong. Check backend and MongoDB.');
      }
    } finally {
      setLoading(false);
    }
  };

  const copy = async (text) => {
    await navigator.clipboard.writeText(text);
    alert('Copied!');
  };

  const downloadQr = () => {
    if (!result?.qr_code) return;
    const a = document.createElement('a');
    a.href = result.qr_code;
    a.download = `${result.slug}-qr.png`;
    a.click();
  };

  return (
    <section className="panel">
      <form onSubmit={submit}>
        <label>Long URL</label>
        <div className="input-row">
          <input value={form.original_url} onChange={e => update('original_url', e.target.value)} placeholder="https://example.com/very/long/link" required />
          <button className="primary" disabled={loading}>{loading ? 'Shortening...' : <><Wand2 size={18}/> Shorten Now</>}</button>
        </div>

        <div className="two-col">
          <div>
            <label><Link2 size={16}/> Custom Alias</label>
            <input value={form.custom_alias} onChange={e => update('custom_alias', e.target.value)} placeholder="my-custom-link" />
          </div>
          <div>
            <label><KeyRound size={16}/> Password Protection</label>
            <input type="password" value={form.password} onChange={e => update('password', e.target.value)} placeholder="Optional password" />
          </div>
        </div>

        <div className="two-col">
          <div>
            <label><CalendarDays size={16}/> Expiration Date</label>
            <input type="datetime-local" value={form.expires_at} onChange={e => update('expires_at', e.target.value)} />
          </div>
          <div>
            <label>Redirect Type</label>
            <select value={form.redirect_type} onChange={e => update('redirect_type', e.target.value)}>
              <option value="302">302 Temporary</option>
              <option value="301">301 Permanent</option>
            </select>
          </div>
        </div>

        <div className="two-col">
          <div>
            <label>Auto Slug Length</label>
            <select value={form.slug_length} onChange={e => update('slug_length', e.target.value)}>
              {[5,6,7,8,9,10,11,12].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>
          <label className="check-card">
            <input type="checkbox" checked={form.generate_qr} onChange={e => update('generate_qr', e.target.checked)} /> Generate QR Code
          </label>
        </div>
      </form>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className="result-card">
          <h3>Your Short Link is Ready</h3>
          <div className="short-url">
            <a href={result.short_url} target="_blank">{result.short_url}</a>
            <button onClick={() => copy(result.short_url)}><Copy size={16}/> Copy</button>
          </div>
          {result.qr_code && <div className="qr-wrap"><img src={result.qr_code} alt="QR Code"/><button onClick={downloadQr}><Download size={16}/> Download QR</button></div>}
          <p className="small">Slug: {result.slug} | Redirect: {result.redirect_type} | Password: {result.has_password ? 'Enabled' : 'No'}</p>
        </div>
      )}
    </section>
  );
}
