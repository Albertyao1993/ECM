import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';

const SensorChart = () => {
  const [data, setData] = useState({
    labels: [],
    temperature: [],
    humidity: [],
    light: []
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/data/history');
        const historyData = response.data;
        
        setData({
          labels: historyData.map(item => new Date(item.timestamp).toLocaleTimeString()),
          temperature: historyData.map(item => item.temperature),
          humidity: historyData.map(item => item.humidity),
          light: historyData.map(item => item.light)
        });
      } catch (error) {
        console.error('Error fetching history data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // 每分钟更新一次
    return () => clearInterval(interval);
  }, []);

  const createChartData = (label, data, color) => ({
    labels: data.labels,
    datasets: [
      {
        label: label,
        data: data[label.toLowerCase()],
        borderColor: color,
        backgroundColor: color.replace(')', ', 0.5)').replace('rgb', 'rgba'),
        fill: false,
      }
    ]
  });

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Sensor Data History (Last 30 Minutes)',
      },
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  return (
    <div>
      <h2>温度、湿度和光照历史数据（最近30分钟）</h2>
      <div style={{ marginBottom: '20px' }}>
        <h3>温度</h3>
        <Line options={options} data={createChartData('Temperature', data, 'rgb(255, 99, 132)')} />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <h3>湿度</h3>
        <Line options={options} data={createChartData('Humidity', data, 'rgb(53, 162, 235)')} />
      </div>
      <div>
        <h3>光照</h3>
        <Line options={options} data={createChartData('Light', data, 'rgb(75, 192, 192)')} />
      </div>
    </div>
  );
};

export default SensorChart;