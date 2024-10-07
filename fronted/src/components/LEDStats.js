import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const LEDStats = () => {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsResponse = await axios.get('http://127.0.0.1:5000/data/led_stats');
        setStats(statsResponse.data);

        const historyResponse = await axios.get('http://127.0.0.1:5000/data/led_history');
        setHistory(historyResponse.data);
      } catch (error) {
        console.error('获取LED数据时出错:', error);
      }
    };

    fetchData();
  }, []);

  if (!stats) {
    return <div>正在加载LED统计信息...</div>;
  }

  return (
    <div>
      <h2>LED使用统计</h2>
      <p>总使用时间: {stats.total_on_time !== undefined ? stats.total_on_time.toFixed(2) : 'N/A'} 秒</p>
      <p>开启次数: {stats.on_count !== undefined ? stats.on_count : 'N/A'} 次</p>
      
      <h3>最近状态历史</h3>
      <ul>
        {history.map((item, index) => (
          <li key={index}>
            {new Date(item.timestamp).toLocaleString()} - 状态: {item.status}, 
            持续时间: {item.duration !== undefined ? item.duration.toFixed(2) : 'N/A'}秒
          </li>
        ))}
      </ul>
      
      <Link to="/">返回主页</Link>
    </div>
  );
};

export default LEDStats;