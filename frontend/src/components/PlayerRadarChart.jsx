import React, { useState, useMemo } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import '../styles/player-stats.css';

/**
 * Player Radar Chart — StatPulse Player Performance Visualization
 * Shows 6 key metrics normalized to 0-10 scale
 */

function PlayerRadarChart({ playerData }) {
  const radarData = useMemo(() => {
    if (!playerData) return [];
    
    return [
      {
        name: 'Shooting',
        value: playerData.shooting_rating || 0,
        fullMark: 10
      },
      {
        name: 'Passing',
        value: playerData.passing_rating || 0,
        fullMark: 10
      },
      {
        name: 'Defense',
        value: playerData.defense_rating || 0,
        fullMark: 10
      },
      {
        name: 'Physical',
        value: playerData.physical_rating || 0,
        fullMark: 10
      },
      {
        name: 'Pace',
        value: playerData.pace_rating || 0,
        fullMark: 10
      },
      {
        name: 'Technical',
        value: playerData.technical_rating || 0,
        fullMark: 10
      }
    ];
  }, [playerData]);

  return (
    <div className="player-radar-container">
      <h3>{playerData?.name} — Performance Radar</h3>
      <div className="radar-chart-wrapper">
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#444" />
            <PolarAngleAxis dataKey="name" />
            <PolarRadiusAxis angle={90} domain={[0, 10]} />
            <Radar
              name={playerData?.position}
              dataKey="value"
              stroke="#ff6b6b"
              fill="#ff6b6b"
              fillOpacity={0.6}
            />
            <Tooltip />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Player Stats Table */}
      <div className="player-stats-table">
        <h4>Detailed Statistics</h4>
        <table>
          <tbody>
            <tr>
              <td>Overall Rating</td>
              <td className="stat-value">{playerData?.overall_rating}/10</td>
            </tr>
            <tr>
              <td>Matches Played</td>
              <td className="stat-value">{playerData?.matches_played}</td>
            </tr>
            <tr>
              <td>Goals</td>
              <td className="stat-value">{playerData?.goals}</td>
            </tr>
            <tr>
              <td>Assists</td>
              <td className="stat-value">{playerData?.assists}</td>
            </tr>
            <tr>
              <td>xG (Expected Goals)</td>
              <td className="stat-value">{playerData?.xg?.toFixed(2)}</td>
            </tr>
            <tr>
              <td>Pass Accuracy</td>
              <td className="stat-value">{playerData?.pass_accuracy}%</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Comparison with Similar Players */}
      <div className="player-comparison">
        <h4>Position Comparison</h4>
        <div className="comparison-row">
          <span>Tournament Average for {playerData?.position}</span>
          <div className="comparison-bar">
            <div className="player-bar" style={{ width: `${(playerData?.overall_rating / 10) * 100}%` }} />
            <div className="avg-bar" style={{ width: '50%' }} />
          </div>
          <span>{playerData?.overall_rating}/10</span>
        </div>
      </div>
    </div>
  );
}

export default PlayerRadarChart;
