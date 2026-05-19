import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './styles/globals.css';

// ━━━━━ Pages ━━━━━
import Dashboard from './pages/Dashboard';
import MatchBrowser from './pages/MatchBrowser';
import PredictionsPage from './pages/PredictionsPage';
import PlayersPage from './pages/PlayersPage';
import ReportsPage from './pages/ReportsPage';
import NavBar from './components/NavBar';

// ━━━━━ Query Client Setup ━━━━━
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10,    // 10 minutes
      retry: 1,
    },
  },
});

/**
 * ⚽ NEXUS FOOTBALL — Main React Application
 * 
 * Three integrated systems:
 * 1. PitchOracle — Match predictions
 * 2. StatPulse — Player ratings
 * 3. MatchMind AI — AI-powered reports
 */
function App() {
  const [theme, setTheme] = useState('dark');
  const [isLiveDataActive, setIsLiveDataActive] = useState(true);

  useEffect(() => {
    // Initialize theme
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="app-container" data-theme={theme}>
          <NavBar 
            theme={theme} 
            onThemeChange={setTheme}
            isLiveDataActive={isLiveDataActive}
          />
          
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/matches" element={<MatchBrowser />} />
              <Route path="/predictions" element={<PredictionsPage />} />
              <Route path="/players" element={<PlayersPage />} />
              <Route path="/reports" element={<ReportsPage />} />
            </Routes>
          </main>

          {/* Live data indicator */}
          <div className="live-indicator">
            <span className={`status-dot ${isLiveDataActive ? 'active' : 'inactive'}`} />
            {isLiveDataActive ? 'Live' : 'Offline'}
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
