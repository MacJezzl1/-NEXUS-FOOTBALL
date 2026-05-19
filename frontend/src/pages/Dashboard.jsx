import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import PredictionCard from '../components/PredictionCard';
import PlayerLeaderboard from '../components/PlayerLeaderboard';
import '../styles/dashboard.css';

/**
 * Dashboard — Main overview of NEXUS FOOTBALL
 * Shows:
 * - Upcoming matches with PitchOracle predictions
 * - Top-rated players from StatPulse
 * - Latest AI reports from MatchMind
 */
function Dashboard() {
  const [selectedGroup, setSelectedGroup] = useState('all');

  // Fetch predictions
  const { data: predictions, isLoading: predictionsLoading } = useQuery({
    queryKey: ['predictions'],
    queryFn: () => fetch('/api/v1/pitchoracle/leaderboard').then(r => r.json()),
  });

  // Fetch player rankings
  const { data: leaderboard, isLoading: leaderboardLoading } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: () => fetch('/api/v1/statpulse/leaderboard').then(r => r.json()),
  });

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>⚽ NEXUS FOOTBALL</h1>
        <p>World Cup 2026 Intelligence Platform</p>
        <p className="subtitle">Three AI systems. Real-time insights. Every match.</p>
      </header>

      <div className="dashboard-grid">
        {/* ━━━━━ UPCOMING MATCHES ━━━━━ */}
        <section className="dashboard-section upcoming-matches">
          <h2>🔵 PitchOracle — Upcoming Matches</h2>
          <div className="group-filter">
            {['all', 'A', 'B', 'C', 'D'].map(g => (
              <button
                key={g}
                className={`filter-btn ${selectedGroup === g ? 'active' : ''}`}
                onClick={() => setSelectedGroup(g)}
              >
                {g === 'all' ? 'All Matches' : `Group ${g}`}
              </button>
            ))}
          </div>
          
          <div className="predictions-list">
            {predictionsLoading ? (
              <p>Loading predictions...</p>
            ) : (
              predictions?.matches?.slice(0, 5).map((match, idx) => (
                <PredictionCard key={idx} match={match} />
              ))
            )}
          </div>
        </section>

        {/* ━━━━━ TOP PLAYERS ━━━━━ */}
        <section className="dashboard-section top-players">
          <h2>🟢 StatPulse — Top Players</h2>
          <div className="leaderboard-preview">
            {leaderboardLoading ? (
              <p>Loading players...</p>
            ) : (
              <PlayerLeaderboard 
                players={leaderboard?.leaderboard?.slice(0, 10)} 
                compact={true}
              />
            )}
          </div>
        </section>

        {/* ━━━━━ AI REPORTS ━━━━━ */}
        <section className="dashboard-section ai-reports">
          <h2>🔴 MatchMind AI — Latest Reports</h2>
          <div className="reports-preview">
            <div className="report-card">
              <h4>Match Analysis</h4>
              <p>Pre-match tactical breakdowns updated in real-time</p>
              <button className="btn-secondary">View Report</button>
            </div>
            <div className="report-card">
              <h4>Live Commentary</h4>
              <p>In-match AI insights as events unfold</p>
              <button className="btn-secondary">Watch Live</button>
            </div>
            <div className="report-card">
              <h4>Post-Match Analysis</h4>
              <p>Full analyst reports within 30 minutes of final whistle</p>
              <button className="btn-secondary">Read Analysis</button>
            </div>
          </div>
        </section>

        {/* ━━━━━ SYSTEM STATUS ━━━━━ */}
        <section className="dashboard-section system-status">
          <h2>⚙️ System Status</h2>
          <div className="status-grid">
            <div className="status-item">
              <span>PitchOracle Model Accuracy</span>
              <div className="progress-bar">
                <div className="progress" style={{ width: '59%' }}></div>
              </div>
              <p>59.2%</p>
            </div>
            <div className="status-item">
              <span>Players Rated</span>
              <p className="large-stat">1,104</p>
            </div>
            <div className="status-item">
              <span>AI Models Active</span>
              <p className="large-stat">20+</p>
            </div>
            <div className="status-item">
              <span>Real-time Data Sources</span>
              <p className="large-stat">7</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
