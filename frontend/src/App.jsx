import { useState } from 'react';
import { BarChart3, Link2, ShieldCheck, Sparkles, Settings, QrCode } from 'lucide-react';
import Home from './pages/Home.jsx';
import Analytics from './pages/Analytics.jsx';
import Admin from './pages/Admin.jsx';

export default function App() {
  const [page, setPage] = useState('home');

  return (
    <div className="app-shell">
      <div className="orb orb-one" />
      <div className="orb orb-two" />
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon"><Link2 size={28} /></div>
          <div>
            <h1>LinkShort</h1>
            <span>SMART LINKS</span>
          </div>
        </div>
        <nav>
          <button onClick={() => setPage('home')} className={page === 'home' ? 'active' : ''}><Sparkles size={16}/> Shorten</button>
          <button onClick={() => setPage('analytics')} className={page === 'analytics' ? 'active' : ''}><BarChart3 size={16}/> Analytics</button>
          <button onClick={() => setPage('admin')} className={page === 'admin' ? 'active' : ''}><Settings size={16}/> Admin</button>
        </nav>
        <a className="doc-link" href="http://localhost:5000/api/docs" target="_blank">Swagger</a>
      </header>

      <main>
        <section className="hero">
          <p className="badge"><ShieldCheck size={16}/> FastAPI + React + MongoDB</p>
          <h2>Shorten, customize and track your links with advanced analytics.</h2>
          <p className="subtitle">A complete hackathon-ready solution with QR code, password protection, expiry, custom aliases and admin controls.</p>
        </section>

        {page === 'home' && <Home />}
        {page === 'analytics' && <Analytics />}
        {page === 'admin' && <Admin />}

        <section className="feature-grid">
          <div><Link2/><h3>Custom Links</h3><p>Create memorable aliases for events and campaigns.</p></div>
          <div><ShieldCheck/><h3>Password Protection</h3><p>Protect private URLs with secure passwords.</p></div>
          <div><QrCode/><h3>QR Codes</h3><p>Download QR codes for posters and presentations.</p></div>
          <div><BarChart3/><h3>Analytics</h3><p>Track clicks by device, browser, OS and referrer.</p></div>
        </section>
      </main>
    </div>
  );
}
