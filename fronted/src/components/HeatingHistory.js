import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import './HeatingHistory.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const HeatingHistory = () => {
  const [historyData, setHistoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistoryData();
  }, []);

  const fetchHistoryData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://127.0.0.1:5000/data/heating-history');
      // 对数据进行排序，确保时间顺序从早到晚
      const sortedData = response.data.sort((a, b) => 
        new Date(a.timestamp) - new Date(b.timestamp)
      );
      setHistoryData(sortedData);
      setError(null);
    } catch (err) {
      setError('Failed to fetch history data');
      console.error('Error fetching heating history:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading history data...</div>;
  if (error) return <div>{error}</div>;
  if (!historyData) return <div>No history data available</div>;

  const formatDateTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const chartData = {
    labels: historyData.map(item => formatDateTime(item.timestamp)),
    datasets: [
      {
        label: 'Predicted Value',
        data: historyData.map(item => item.prediction_value),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.1,
        pointRadius: 3,
        pointHoverRadius: 5
      },
      {
        label: 'Actual Value',
        data: historyData.map(item => item.actual_value),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.1,
        pointRadius: 3,
        pointHoverRadius: 5
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Heating Prediction History',
        font: {
          size: 16
        }
      },
      tooltip: {
        callbacks: {
          title: (tooltipItems) => {
            return formatDateTime(historyData[tooltipItems[0].dataIndex].timestamp);
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Energy Usage (kWh)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Time'
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45
        }
      }
    },
    interaction: {
      intersect: false,
      mode: 'index'
    }
  };

  return (
    <div className="heating-history">
      <h2>Heating Prediction History</h2>
      <div className="chart-container">
        <Line data={chartData} options={options} />
      </div>
      <button className="back-button" onClick={() => window.history.back()}>
        Back to Prediction
      </button>
    </div>
  );
};

export default HeatingHistory;