// src/components/SensorChart.js
import React from 'react';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';


const SensorChart = ({ chartData }) => {
  const chartOptions = {
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'second',
        },
        title: {
          display: true,
          text: '时间',
        },
      },
      y1: {
        type: 'linear',
        position: 'left',
        min: 15,
        max: 35,
        title: {
          display: true,
          text: '温度 (°C)',
        },
      },
      y2: {
        type: 'linear',
        position: 'right',
        min: 20,
        max: 80,
        title: {
          display: true,
          text: '湿度 (%)',
        },
        grid: {
          drawOnChartArea: false, // only want the grid lines for one axis to show up
        },
      },
    },
  };

  return (
    <div>
      <h3>实时温湿度数据展示</h3>
      <Line data={chartData} options={chartOptions} />
    </div>
  );
};

export default SensorChart;
