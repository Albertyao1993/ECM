import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Grid, Paper } from '@mui/material';
import axios from 'axios';

const SensorChart = () => {
  const [temperatureData, setTemperatureData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Indoor Temperature (°C)',
        data: [],
        borderColor: 'rgba(75,192,192,1)',
        fill: false,
      },
      {
        label: 'Outdoor Temperature (°C)',
        data: [],
        borderColor: 'rgba(255,99,132,1)',
        fill: false,
      },
    ],
  });

  const [humidityData, setHumidityData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Indoor Humidity (%)',
        data: [],
        borderColor: 'rgba(153,102,255,1)',
        fill: false,
      },
      {
        label: 'Outdoor Humidity (%)',
        data: [],
        borderColor: 'rgba(54,162,235,1)',
        fill: false,
      },
    ],
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 获取当前时间和30分钟前的时间
        const endTime = new Date();
        const startTime = new Date(endTime.getTime() - 30 * 60 * 1000);

        // 格式化时间为 ISO 字符串，并去除时区信息
        const startISO = startTime.toISOString();
        const endISO = endTime.toISOString();

        // console.log(`Start Time is : ${startISO}`);

        const response = await axios.get(`http://127.0.0.1:5000/data/history?start_time=${startISO}&end_time=${endISO}`);
        const data = await response.data;

        // 解析数据
        const tempData = data.map(item => {
          const localDate = new Date(item.timestamp);
          // console.log(`Local Data is : ${localDate.toLocaleString()}`);
          return {
            x: localDate.toLocaleString(), // 使用 toLocaleString() 确保显示本地时间
            y: item.temperature,
            owY: item.ow_temperature,
          };
        });

        const humData = data.map(item => {
          const localDate = new Date(item.timestamp);
          return {
            x: localDate.toLocaleString(), // 使用 toLocaleString() 确保显示本地时间
            y: item.humidity,
            owY: item.ow_humidity,
          };
        });

        setTemperatureData({
          labels: tempData.map(d => d.x),
          datasets: [
            {
              label: 'Indoor Temperature (°C)',
              data: tempData.map(d => d.y),
              borderColor: 'rgba(75,192,192,1)',
              fill: false,
            },
            {
              label: 'Outdoor Temperature (°C)',
              data: tempData.map(d => d.owY),
              borderColor: 'rgba(255,99,132,1)',
              fill: false,
            },
          ],
        });

        setHumidityData({
          labels: humData.map(d => d.x),
          datasets: [
            {
              label: 'Indoor Humidity (%)',
              data: humData.map(d => d.y),
              borderColor: 'rgba(153,102,255,1)',
              fill: false,
            },
            {
              label: 'Outdoor Humidity (%)',
              data: humData.map(d => d.owY),
              borderColor: 'rgba(54,162,235,1)',
              fill: false,
            },
          ],
        });
      } catch (error) {
        console.error('Error fetching sensor data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // 每分钟刷新一次数据

    return () => clearInterval(interval);
  }, []);

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <Paper elevation={3}>
          <Line data={temperatureData} />
        </Paper>
      </Grid>
      <Grid item xs={12} md={6}>
        <Paper elevation={3}>
          <Line data={humidityData} />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default SensorChart;
