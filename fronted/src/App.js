// src/App.js
import React, { useEffect, useState } from 'react';
// import { io } from 'socket.io-client';
import SensorChart from './components/SensorChart';  // 导入新的组件
import 'chartjs-adapter-date-fns';
import axios from 'axios';

// const socket = io('http://127.0.0.1:5000'); // 连接到后端 WebSocket 服务器

const App = () => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: '温度 (°C)',
        data: [],
        borderColor: 'rgba(255,99,132,1)',
        backgroundColor: 'rgba(255,99,132,0.2)',
        fill: false,
        yAxisID: 'y1',
      },
      {
        label: '湿度 (%)',
        data: [],
        borderColor: 'rgba(54,162,235,1)',
        backgroundColor: 'rgba(54,162,235,0.2)',

        fill: false,
        yAxisID: 'y2',
      },
    ],
  });

useEffect(() => {
  const fetchData = async () => {
    try {
      const response = await axios.get('http://localhost:5000/data');
      const data = response.data;
      console.log(data);
      const labels = data.map(item => new Date(item.timestamp));
      console.log(labels);
      const temperatureData = data.map(item => item.temperature);
      console.log(temperatureData);
      const humidityData = data.map(item => item.humidity);

      setChartData({
        labels: labels,
        datasets: [
          {
            label: '温度 (°C)',
            data: temperatureData,
            borderColor: 'rgba(255,99,132,1)',
            backgroundColor: 'rgba(255,99,132,0.2)',
            fill: false,
            yAxisID: 'y1',
          },
          {
            label: '湿度 (%)',
            data: humidityData,
            borderColor: 'rgba(54,162,235,1)',
            backgroundColor: 'rgba(54,162,235,0.2)',
            fill: false,
            yAxisID: 'y2',
          },
        ],
      });
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  fetchData();
  const intervalId = setInterval(fetchData, 5000); // 每5秒更新一次数据
  return () => {
    clearInterval(intervalId);
  };
}, []);

  return (
    <div className="App">
      <SensorChart chartData={chartData} /> {/* 使用新的组件 */}
    </div>
  );
};

export default App;
