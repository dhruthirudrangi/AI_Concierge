import { NavLink } from 'react-router-dom';
import { BarChart3, CreditCard, MessageCircle, PlayCircle } from 'lucide-react';
import { isGeminiConfigured } from '../../services/geminiService';
import './Navbar.css';

export function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <CreditCard size={22} />
        <span>CardConcierge</span>
      </div>

      <div className="navbar-links">
        <NavLink to="/onboarding" className={({ isActive }) => (isActive ? 'active' : '')}>
          Preferences
        </NavLink>
        <NavLink to="/concierge" className={({ isActive }) => (isActive ? 'active' : '')}>
          <MessageCircle size={16} />
          Chat
        </NavLink>
        <NavLink to="/analytics" className={({ isActive }) => (isActive ? 'active' : '')}>
          <BarChart3 size={16} />
          Analytics
        </NavLink>
        <NavLink to="/demo" className={({ isActive }) => (isActive ? 'active' : '')}>
          <PlayCircle size={16} />
          Demo
        </NavLink>
      </div>

      <div className="navbar-status">
        <span className={`status-dot ${isGeminiConfigured() ? 'online' : 'mock'}`} />
        {isGeminiConfigured() ? 'Gemini' : 'Mock LLM'}
      </div>
    </nav>
  );
}
