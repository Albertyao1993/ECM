// src/components/SensorChart.js
import React, { useEffect, useState } from 'react';
import { Grid, Paper } from '@mui/material';
import LineChart from './LineChart';

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

  const temperatureData = chartData.map(item => ({ x: item.timestamp, y: item.temperature }));
  const humidityData = chartData.map(item => ({ x: item.timestamp, y: item.humidity }));

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
      y: {
        title: {
          display: true,
          text: 'Value',
        },
      },
    },
  };

  const temperatureChartData = {
    datasets: [
      {
        label: 'Temperature',
        data: temperatureData,
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        fill: false,
      },
    ],
  };

  const humidityChartData = {
    datasets: [
      {
        label: 'Humidity',
        data: humidityData,
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        fill: false,
      },
    ],
  };

  return (

    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <Paper elevation={3}>
          <LineChart data={temperatureChartData} options={chartOptions} title="Temperature Chart" />
        </Paper>
      </Grid>
      <Grid item xs={12} md={6}>
        <Paper elevation={3}>
          <LineChart data={humidityChartData} options={chartOptions} title="Humidity Chart" />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default SensorChart;
