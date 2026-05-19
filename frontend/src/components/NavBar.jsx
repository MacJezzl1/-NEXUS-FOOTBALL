import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/navbar.css';

function NavBar({ theme, onThemeChange, isLiveDataActive }) {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">⚽</span>
          NEXUS FOOTBALL
        </Link>

        {/* Navigation Links */}
        <div className="navbar-links">
          <Link to="/" className="nav-item">Dashboard</Link>
          <Link to="/matches" className="nav-item">Matches</Link>
          <Link to="/predictions" className="nav-item">
            <span className="badge">Predictions</span>
          </Link>
          <Link to="/players" className="nav-item">
            <span className="badge">StatPulse</span>
          </Link>
          <Link to="/reports" className="nav-item">
            <span className="badge">AI Reports</span>
          </Link>
        </div>

        {/* Right Side Controls */}
        <div className="navbar-controls">
          {/* Live Data Indicator */}
          <div className={`live-badge ${isLiveDataActive ? 'active' : 'inactive'}`}>
            <span className="pulse"></span>
            {isLiveDataActive ? 'LIVE' : 'OFFLINE'}
          </div>

          {/* Theme Toggle */}
          <button 
            className="theme-toggle"
            onClick={() => onThemeChange(theme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>

          {/* Search */}
          <input 
            type="text" 
            placeholder="Search teams, players..." 
            className="search-input"
          />
        </div>
      </div>
    </nav>
  );
}

export default NavBar;
