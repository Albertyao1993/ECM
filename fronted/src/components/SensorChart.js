import React, { useEffect, useState } from 'react';
import { Grid, Paper } from '@mui/material';
import LineChart from './LineChart';

const SensorChart = () => {
  const [temperatureData, setTemperatureData] = useState([]);
  const [humidityData, setHumidityData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 获取当前时间和30分钟前的时间
        const endTime = new Date();
        const startTime = new Date(endTime.getTime() - 30 * 60 * 1000);

        // 格式化时间为 ISO 字符串，并去除时区信息
        const startISO = startTime.toISOString();
        const endISO = endTime.toISOString();

        // console.log('startISO:', startISO);
        // console.log('endISO:', endISO);
        
        // 构建请求URL，包含时间范围参数
        const response = await fetch(`http://127.0.0.1:5000/data/history?start_time=${startISO}&end_time=${endISO}`);
        const data = await response.json();

        // 解析数据
        const tempData = data.map(item => {
          // 将时间字符串转换为 Date 对象
          const utcDate = new Date(item.timestamp);
          // 获取本地时间的毫秒数
          const localTime = utcDate.getTime() + (utcDate.getTimezoneOffset() * 60000);
          // 创建新的本地 Date 对象
          const localDate = new Date(localTime);

          return {
            x: localDate,
            y: item.temperature,
            owY: item.ow_temperature,
          };
        });

        const humData = data.map(item => {
          const utcDate = new Date(item.timestamp);
          const localTime = utcDate.getTime() + (utcDate.getTimezoneOffset() * 60000);
          const localDate = new Date(localTime);

          return {
            x: localDate,
            y: item.humidity,
            owY: item.ow_humidity,
          };
        });

        setTemperatureData(tempData);
        setHumidityData(humData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 5000); // 每5秒刷新一次数据
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  const chartOptions = {
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'minute',
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

  // 构建温度图表数据
  const temperatureChartData = {
    datasets: [
      {
        label: 'Sensor Temperature',
        data: temperatureData.map(item => ({ x: item.x, y: item.y })),
        borderColor: 'rgba(255, 99, 132, 1)', // 红色
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        fill: false,
      },
      {
        label: 'OpenWeather Temperature',
        data: temperatureData.map(item => ({ x: item.x, y: item.owY })),
        borderColor: 'rgba(255, 159, 64, 1)', // 橙色
        backgroundColor: 'rgba(255, 159, 64, 0.2)',
        fill: false,
      },
    ],
  };

  // 构建湿度图表数据
  const humidityChartData = {
    datasets: [
      {
        label: 'Sensor Humidity',
        data: humidityData.map(item => ({ x: item.x, y: item.y })),
        borderColor: 'rgba(54, 162, 235, 1)', // 蓝色
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        fill: false,
      },
      {
        label: 'OpenWeather Humidity',
        data: humidityData.map(item => ({ x: item.x, y: item.owY })),
        borderColor: 'rgba(75, 192, 192, 1)', // 绿色
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: false,
      },
    ],
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <Paper elevation={3} style={{ padding: '16px' }}>
          <LineChart data={temperatureChartData} options={chartOptions} title="Temperature Chart" />
        </Paper>
      </Grid>
      <Grid item xs={12} md={6}>
        <Paper elevation={3} style={{ padding: '16px' }}>
          <LineChart data={humidityChartData} options={chartOptions} title="Humidity Chart" />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default SensorChart;
