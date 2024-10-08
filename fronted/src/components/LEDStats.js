import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LEDStats = () => {
  const [ledStats, setLedStats] = useState(null);
  const [ledAnalysis, setLedAnalysis] = useState(null);
  const [isAnalysisLoading, setIsAnalysisLoading] = useState(false);

  useEffect(() => {
    fetchLEDStats();
    fetchLEDAnalysis();

    const interval = setInterval(() => {
      fetchLEDStats();
      fetchLEDAnalysis();
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  const fetchLEDStats = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/data/led_stats');
      setLedStats(response.data);
    } catch (error) {
      console.error('Error fetching LED stats:', error);
    }
  };

  const fetchLEDAnalysis = async () => {
    setIsAnalysisLoading(true);
    try {
      const response = await axios.get('http://127.0.0.1:5000/data/led_analysis');
      if (response.status === 202) {
        // Start polling
        pollAnalysisResult(response.data.task_id);
      } else {
        setLedAnalysis(response.data);
        setIsAnalysisLoading(false);
      }
    } catch (error) {
      console.error('Error fetching LED analysis:', error);
      setIsAnalysisLoading(false);
    }
  };

  const pollAnalysisResult = async (taskId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/data/led_analysis?task_id=${taskId}`);
        if (response.status === 200) {
          setLedAnalysis(response.data);
          setIsAnalysisLoading(false);
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Error polling analysis result:', error);
      }
    }, 2000); // Poll every 2 seconds

    // Set timeout to prevent infinite polling
    setTimeout(() => {
      clearInterval(pollInterval);
      setIsAnalysisLoading(false);
      setLedAnalysis({ error: 'Analysis timed out, please try again later' });
    }, 60000); // Timeout after 60 seconds
  };

  if (!ledStats) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>LED Statistics</h2>
      <p>Total On Time: {ledStats.total_on_time.toFixed(2)} seconds</p>
      <p>On Count: {ledStats.on_count}</p>
      
      <h3>AI Analysis</h3>
      {isAnalysisLoading ? (
        <p>Generating analysis...</p>
      ) : ledAnalysis ? (
        <>
          <p>LED Action: {ledAnalysis.led_action}</p>
          <p>Energy Consumption: {ledAnalysis.energy_info?.energy_consumption} kWh</p>
          <p>Cost: {ledAnalysis.energy_info?.cost} currency units</p>
          <p>Analysis: {ledAnalysis.analysis}</p>
        </>
      ) : (
        <p>No analysis data available</p>
      )}
    </div>
  );
};

export default LEDStats;