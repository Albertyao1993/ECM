import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './HeatingPrediction.css';

const HeatingPrediction = () => {
  const [predictionData, setPredictionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPredictionData();
    // 每15分钟更新一次预测
    const interval = setInterval(fetchPredictionData, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchPredictionData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://127.0.0.1:5000/data/heating-prediction');
      setPredictionData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch prediction data');
      console.error('Error fetching heating prediction:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading prediction data...</div>;
  }

  if (error) {
    return (
      <div>
        <p>{error}</p>
        <button onClick={fetchPredictionData}>Retry</button>
      </div>
    );
  }

  return (
    <div className="heating-prediction">
      <h2>15-Minute Heating Prediction</h2>
      
      {predictionData && (
        <div className="prediction-content">
          <div className="prediction-card">
            <h3>Next 15 Minutes Prediction</h3>
            <div className="prediction-value">
              <div className="usage">
                <span className="label">Estimated Usage:</span>
                <span className="value">{predictionData.prediction.estimated_usage.toFixed(2)} kWh</span>
              </div>
              <div className="cost">
                <span className="label">Estimated Cost:</span>
                <span className="value">€{predictionData.prediction.estimated_cost.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div className="prediction-tips">
            <h3>Energy Saving Tips</h3>
            <ul>
              {predictionData.tips.map((tip, index) => (
                <li key={index}>{tip}</li>
              ))}
            </ul>
          </div>

          <div className="prediction-features">
            <h3>Current Conditions</h3>
            <div className="features-grid">
              {Object.entries(predictionData.features).map(([key, value]) => (
                <div key={key} className="feature-item">
                  <span className="feature-label">{key}:</span>
                  <span className="feature-value">{typeof value === 'number' ? value.toFixed(2) : value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HeatingPrediction;