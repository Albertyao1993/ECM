import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const LEDStats = () => {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [energyStats, setEnergyStats] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsResponse = await axios.get('http://127.0.0.1:5000/data/led_stats');
        setStats(statsResponse.data);

        const historyResponse = await axios.get('http://127.0.0.1:5000/data/led_history');
        setHistory(historyResponse.data);

        const energyResponse = await axios.get('http://127.0.0.1:5000/data/energy_stats');
        setEnergyStats(energyResponse.data);
      } catch (error) {
        console.error('Error fetching LED data:', error);
      }
    };

    fetchData();
  }, []);

  if (!stats || !energyStats) {
    return <div>Loading LED statistics...</div>;
  }

  return (
    <div>
      <h2>LED Usage Statistics</h2>
      <p>Total usage time: {stats.total_on_time !== undefined ? stats.total_on_time.toFixed(2) : 'N/A'} seconds</p>
      <p>Number of activations: {stats.on_count !== undefined ? stats.on_count : 'N/A'} times</p>
      
      <h3>Energy Consumption Statistics</h3>
      <p>Total energy consumption: {energyStats.total_energy.toFixed(4)} kWh</p>
      <p>Total cost: {energyStats.total_cost.toFixed(2)} yuan</p>
      
      <h3>Recent Status History</h3>
      <ul>
        {history.map((item, index) => (
          <li key={index}>
            {item.timestamp} - Status: {item.status}, 
            Duration: {item.duration !== undefined ? item.duration.toFixed(2) : 'N/A'} seconds
          </li>
        ))}
      </ul>
      
      <Link to="/">Return to Home</Link>
    </div>
  );
};

export default LEDStats;