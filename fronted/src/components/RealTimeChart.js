import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';
import { Link } from 'react-router-dom';

const RealTimeChart = () => {
  const [data, setData] = useState({
    labels: [],
    temperature: [],
    humidity: [],
    light: []
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/data/realtime');
        const newData = response.data;
        
        setData(prevData => {
          const newLabels = [...prevData.labels, new Date().toLocaleTimeString()].slice(-20);
          return {
            labels: newLabels,
            temperature: [...prevData.temperature, newData.temperature].slice(-20),
            humidity: [...prevData.humidity, newData.humidity].slice(-20),
            light: [...prevData.light, newData.light].slice(-20)
          };
        });
      } catch (error) {
        console.error('Error fetching real-time data:', error);
      }
    };

    const interval = setInterval(fetchData, 2000);
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
        text: 'Real-time Sensor Data',
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
      <h2>Real-time Temperature, Humidity, and Light Data</h2>
      <div style={{ marginBottom: '20px' }}>
        <h3>Temperature</h3>
        <Line options={options} data={createChartData('Temperature', data, 'rgb(255, 99, 132)')} />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <h3>Humidity</h3>
        <Line options={options} data={createChartData('Humidity', data, 'rgb(53, 162, 235)')} />
      </div>
      <div>
        <h3>Light</h3>
        <Line options={options} data={createChartData('Light', data, 'rgb(75, 192, 192)')} />
      </div>
      <Link to="/">Return to Home</Link>
    </div>
  );
};

export default RealTimeChart;