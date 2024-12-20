import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

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
    const interval = setInterval(fetchData, 60000); // Update every minute
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
        label: 'Light Threshold',
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
      <h2>Temperature, Humidity, and Light Historical Data (Last 30 Minutes)</h2>
      <div style={{ marginBottom: '20px' }}>
        <h3>Temperature</h3>
        <Line options={options} data={createChartData('Temperature', data, 'rgb(255, 99, 132)', true)} />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <h3>Humidity</h3>
        <Line options={options} data={createChartData('Humidity', data, 'rgb(53, 162, 235)', true)} />
      </div>
      <div>
        <h3>Light</h3>
        <Line options={options} data={createChartData('Light', data, 'rgb(75, 192, 192)', false, true)} />
      </div>
    </div>
  );
};

export default SensorChart;