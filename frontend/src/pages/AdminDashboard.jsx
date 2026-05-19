import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import '../styles/admin-dashboard.css';

/**
 * Admin Dashboard — NEXUS FOOTBALL
 * System monitoring, user management, analytics
 */

function AdminDashboard() {
  const [systemStats, setSystemStats] = useState(null);
  const [userStats, setUserStats] = useState([]);
  const [apiStats, setApiStats] = useState([]);
  const [cacheStatus, setCacheStatus] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [revenueMetrics, setRevenueMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const [stats, users, api, cache, health, revenue] = await Promise.all([
        fetch('/api/v1/admin/dashboard/system').then(r => r.json()),
        fetch('/api/v1/admin/dashboard/users').then(r => r.json()),
        fetch('/api/v1/admin/dashboard/api-stats').then(r => r.json()),
        fetch('/api/v1/admin/dashboard/cache').then(r => r.json()),
        fetch('/api/v1/admin/dashboard/health').then(r => r.json()),
        fetch('/api/v1/admin/dashboard/revenue').then(r => r.json()),
      ]);

      setSystemStats(stats);
      setUserStats(users);
      setApiStats(api);
      setCacheStatus(cache);
      setSystemHealth(health);
      setRevenueMetrics(revenue);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="admin-loading">Loading dashboard...</div>;

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <h1>⚽ NEXUS FOOTBALL — Admin Dashboard</h1>
        <p>System Monitoring & Analytics</p>
      </header>

      {/* ━━━━━ SYSTEM HEALTH CARDS ━━━━━ */}
      <section className="health-cards">
        <div className="health-card">
          <h3>System Status</h3>
          <p className={`status ${systemHealth?.status}`}>{systemHealth?.status?.toUpperCase()}</p>
          <small>Uptime: {systemHealth?.uptime_hours.toFixed(1)} hours</small>
        </div>

        <div className="health-card">
          <h3>Database</h3>
          <p className="status connected">{systemHealth?.database?.toUpperCase()}</p>
          <small>Size: {systemStats?.database_size_mb.toFixed(1)} MB</small>
        </div>

        <div className="health-card">
          <h3>Cache</h3>
          <p className="status connected">{systemHealth?.cache?.toUpperCase()}</p>
          <small>Hit Rate: {cacheStatus?.hit_rate.toFixed(1)}%</small>
        </div>

        <div className="health-card">
          <h3>Response Time</h3>
          <p className="metric">{systemHealth?.avg_response_time_ms.toFixed(1)}ms</p>
          <small>Error Rate: {systemHealth?.error_rate_percentage.toFixed(2)}%</small>
        </div>
      </section>

      {/* ━━━━━ KEY METRICS ━━━━━ */}
      <section className="metrics-grid">
        <div className="metric-card">
          <h3>Total Users</h3>
          <div className="big-number">{systemStats?.total_users}</div>
          <p>Premium: {systemStats?.premium_users} ({((systemStats?.premium_users / systemStats?.total_users) * 100).toFixed(1)}%)</p>
        </div>

        <div className="metric-card">
          <h3>Predictions Accuracy</h3>
          <div className="big-number">{(systemStats?.average_prediction_accuracy * 100).toFixed(1)}%</div>
          <p>Total Predictions: {systemStats?.total_predictions}</p>
        </div>

        <div className="metric-card">
          <h3>Tournament Progress</h3>
          <div className="big-number">{systemStats?.matches_completed}/{systemStats?.total_matches}</div>
          <p>Completed: {systemStats?.matches_completed} | Upcoming: {systemStats?.matches_upcoming}</p>
        </div>

        <div className="metric-card">
          <h3>Reports Generated</h3>
          <div className="big-number">{systemStats?.total_reports_generated}</div>
          <p>AI-powered match analysis</p>
        </div>
      </section>

      {/* ━━━━━ API PERFORMANCE ━━━━━ */}
      <section className="chart-section">
        <h2>API Endpoint Performance</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={apiStats}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="endpoint" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Bar yAxisId="left" dataKey="total_calls" fill="#ff6b6b" name="Total Calls" />
            <Bar yAxisId="right" dataKey="avg_response_time_ms" fill="#4ecdc4" name="Avg Response (ms)" />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* ━━━━━ CACHE PERFORMANCE ━━━━━ */}
      <section className="chart-section">
        <h2>Cache Health</h2>
        <div className="cache-stats">
          <div className="cache-stat">
            <span>Hit Rate</span>
            <div className="progress-bar">
              <div className="progress" style={{ width: `${cacheStatus?.hit_rate * 100}%` }} />
            </div>
            <p>{(cacheStatus?.hit_rate * 100).toFixed(1)}%</p>
          </div>
          
          <div className="cache-stat">
            <span>Memory Usage</span>
            <p>{cacheStatus?.memory_usage_mb.toFixed(1)} MB</p>
          </div>

          <div className="cache-stat">
            <span>Total Keys</span>
            <p>{cacheStatus?.total_keys}</p>
          </div>

          <div className="cache-stat">
            <span>Evictions</span>
            <p>{cacheStatus?.evictions}</p>
          </div>
        </div>
      </section>

      {/* ━━━━━ REVENUE METRICS ━━━━━ */}
      <section className="metrics-section">
        <h2>Revenue & Subscriptions</h2>
        <div className="revenue-cards">
          <div className="revenue-card">
            <h4>Monthly Recurring Revenue</h4>
            <p className="big-number">${revenueMetrics?.monthly_recurring_revenue_usd}</p>
          </div>

          <div className="revenue-card">
            <h4>Premium Conversion</h4>
            <p className="big-number">{revenueMetrics?.premium_conversion_rate.toFixed(1)}%</p>
          </div>

          <div className="revenue-card">
            <h4>Customer LTV</h4>
            <p className="big-number">${revenueMetrics?.lifetime_value_per_user_usd}</p>
          </div>

          <div className="revenue-card">
            <h4>Churn Rate</h4>
            <p className="big-number">{revenueMetrics?.churn_rate_percentage.toFixed(1)}%</p>
          </div>
        </div>
      </section>

      {/* ━━━━━ TOP USERS ━━━━━ */}
      <section className="table-section">
        <h2>Top Performers</h2>
        <div className="table-wrapper">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Username</th>
                <th>Email</th>
                <th>Points</th>
                <th>Accuracy</th>
                <th>Tier</th>
              </tr>
            </thead>
            <tbody>
              {userStats.slice(0, 10).map((user, idx) => (
                <tr key={idx}>
                  <td>#{user.tournament_rank}</td>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td className="number">{user.total_points}</td>
                  <td className="number">{user.accuracy_percentage.toFixed(1)}%</td>
                  <td><span className={`badge ${user.subscription_tier}`}>{user.subscription_tier}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ━━━━━ ADMIN ACTIONS ━━━━━ */}
      <section className="admin-actions">
        <h2>Admin Actions</h2>
        <div className="action-buttons">
          <button className="btn btn-primary" onClick={() => {
            fetch('/api/v1/admin/clear-cache', { method: 'POST' });
            alert('Cache cleared');
          }}>
            Clear All Caches
          </button>

          <button className="btn btn-primary" onClick={() => {
            fetch('/api/v1/admin/sync-data', { method: 'POST' });
            alert('Data sync triggered');
          }}>
            Sync Data Sources
          </button>

          <button className="btn btn-secondary" onClick={() => {
            fetch('/api/v1/admin/backup-database', { method: 'POST' });
            alert('Backup started');
          }}>
            Backup Database
          </button>

          <button className="btn btn-secondary" onClick={fetchDashboardData}>
            Refresh Dashboard
          </button>
        </div>
      </section>
    </div>
  );
}

export default AdminDashboard;
