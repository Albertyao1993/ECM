import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const LEDStats = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/data/led_stats');
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching LED stats:', error);
      }
    };

    fetchStats();
  }, []);

  if (!stats) {
    return <div>Loading LED stats...</div>;
  }

  return (
    <div>
      <h2>LED Usage Statistics</h2>
      <p>Total Usage Time: {stats.total_usage}</p>
      <p>Average Usage Time: {stats.average_usage}</p>
      <p>Number of Times Used: {stats.usage_count}</p>
      <Link to="/">返回主页</Link>
    </div>
  );
};

export default LEDStats;