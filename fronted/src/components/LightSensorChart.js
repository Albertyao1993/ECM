import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Grid, Paper } from '@mui/material';
import axios from 'axios';

const LightSensorChart = () => {
  const [lightData, setLightData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Light Intensity (lux)',
        data: [],
        borderColor: 'rgba(255,206,86,1)',
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

        const response = await axios.get(`http://127.0.0.1:5000/data/history?start_time=${startISO}&end_time=${endISO}`);
        const data = response.data;
        console.log('Response data in Light Sensor:', data); // 打印完整的响应数据

        // 解析数据
        const lightData = data.map(item => {
          const utcDate = new Date(item.timestamp);
          const berlinDate = new Intl.DateTimeFormat('de-DE', {
            timeZone: 'Europe/Berlin',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          }).format(utcDate);
          return {
            x: berlinDate, // 使用柏林时间
            y: item.light, // 假设光照数据字段为 light
          };
        });

        setLightData({
          labels: lightData.map(d => d.x),
          datasets: [
            {
              label: 'Light Intensity (lux)',
              data: lightData.map(d => d.y),
              borderColor: 'rgba(255,206,86,1)',
              fill: false,
            },
          ],
        });
      } catch (error) {
        console.error('Error fetching light sensor data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000); // 每分钟刷新一次数据

    return () => clearInterval(interval);
  }, []);

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Paper elevation={3}>
          <Line data={lightData} />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default LightSensorChart;