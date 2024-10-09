import React, { useEffect, useState } from 'react';
import axios from 'axios';

const LiveStream = () => {
  const [personCount, setPersonCount] = useState(0);

  useEffect(() => {
    const fetchPersonCount = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/data/realtime');
        console.log('Realtime data:', response.data);  // 添加这行日志
        setPersonCount(response.data.person_count);
      } catch (error) {
        console.error('获取人数数据失败:', error);
      }
    };

    // 初始获取
    fetchPersonCount();

    // 每分钟更新一次
    const interval = setInterval(fetchPersonCount, 60000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Person Count Detection in Real time</h1>
      <p>Current Persons: {personCount}</p>
    </div>
  );
};

export default LiveStream;
