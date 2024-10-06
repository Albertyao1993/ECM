import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';

const SensorChart = () => {
  const [data, setData] = useState({
    labels: [],
    temperature: [],
    humidity: [],
    light: [],
    ow_temperature: [],
    ow_humidity: []
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
          light: historyData.map(item => item.light),
          ow_temperature: historyData.map(item => item.ow_temperature),
          ow_humidity: historyData.map(item => item.ow_humidity)
        });
      } catch (error) {
        console.error('Error fetching history data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // 每分钟更新一次
    return () => clearInterval(interval);
  }, []);

  const createChartData = (label, data, color, includeOW = false, isLight = false) => {
    const datasets = [
      {
        label: label,
        data: data[label.toLowerCase()],
        borderColor: color,
        backgroundColor: color.replace(')', ', 0.5)').replace('rgb', 'rgba'),
        fill: false,
      }
    ];

    if (includeOW) {
      datasets.push({
        label: `OpenWeather ${label}`,
        data: data[`ow_${label.toLowerCase()}`],
        borderColor: color.replace(')', ', 0.7)').replace('rgb', 'rgba'),
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        fill: false,
      });
    }

    if (isLight) {
      datasets.push({
        label: '光照阈值',
        data: new Array(data.labels.length).fill(100),
        borderColor: 'rgb(255, 0, 0)',
        backgroundColor: 'transparent',
        borderDash: [10, 5],
        fill: false,
      });
    }

    return {
      labels: data.labels,
      datasets: datasets
    };
  };

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
        <Line options={options} data={createChartData('Temperature', data, 'rgb(255, 99, 132)', true)} />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <h3>湿度</h3>
        <Line options={options} data={createChartData('Humidity', data, 'rgb(53, 162, 235)', true)} />
      </div>
      <div>
        <h3>光照</h3>
        <Line options={options} data={createChartData('Light', data, 'rgb(75, 192, 192)', false, true)} />
      </div>
    </div>
  );
};

export default SensorChart;