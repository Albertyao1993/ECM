// src/components/SensorChart.js
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import 'chartjs-adapter-date-fns';

const SensorChart = () => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/data');
        const data = await response.json();
        setChartData(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 5000); // Fetch data every 5 seconds
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  const chartOptions = {
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'second',
        },
        title: {
          display: true,
          text: 'Time',
        },
      },
      y1: {
        type: 'linear',
        position: 'left',
        min: 15,
        max: 35,
        title: {
          display: true,
          text: 'Temperature (°C)',
        },
      },
      y2: {
        type: 'linear',
        position: 'right',
        min: 0,
        max: 100,
        title: {
          display: true,
          text: 'Humidity (%)',
        },
      },
    },
  };

  const data = {
    labels: chartData.map((entry) => new Date(entry.timestamp)),
    datasets: [
      {
        label: 'Temperature (°C)',
        data: chartData.map((entry) => entry.temperature),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        yAxisID: 'y1',
      },
      {
        label: 'Humidity (%)',
        data: chartData.map((entry) => entry.humidity),
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        yAxisID: 'y2',
      },
    ],
  };

  return <Line data={data} options={chartOptions} />;
};

export default SensorChart;
