import React from 'react';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import 'chartjs-adapter-date-fns';

const LineChart = ({ data, options, title }) => {
  return (
    <div style={{ width: '100%', height: '100%' }}>
      <h2>{title}</h2>
      <Line data={data} options={options} />
    </div>
  );
};

export default LineChart;