import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LEDStats = () => {
  const [ledStats, setLedStats] = useState(null);
  const [ledAnalysis, setLedAnalysis] = useState(null);
  const [isAnalysisLoading, setIsAnalysisLoading] = useState(false);
  const [shouldRefresh, setShouldRefresh] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      await fetchLEDStats();
      if (shouldRefresh) {
        await fetchLEDAnalysis();
      }
    };

    fetchData();

    let interval;
    if (shouldRefresh) {
      interval = setInterval(fetchData, 60000); // Update every minute
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [shouldRefresh]);

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
        setShouldRefresh(false); // Stop refreshing after getting analysis results
      }
    } catch (error) {
      console.error('Error getting LED analysis:', error);
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
          setShouldRefresh(false); // Stop refreshing after getting analysis results
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
      setLedAnalysis({ error: 'Analysis timeout, please try again later' });
    }, 60000); // Timeout after 60 seconds
  };

  const getEnergyInfo = (info) => {
    if (typeof info === 'string') {
      const parts = info.split(',');
      return {
        consumption: parts[0]?.split(':')[1]?.trim() || 'Unknown',
        cost: parts[1]?.split(':')[1]?.trim() || 'Unknown'
      };
    } else if (typeof info === 'object' && info !== null) {
      return {
        consumption: info.energy_consumption || 'Unknown',
        cost: info.cost || 'Unknown'
      };
    }
    return { consumption: 'Unknown', cost: 'Unknown' };
  };

  if (!ledStats) {
    return <div>Loading...</div>;
  }

  const energyInfo = ledAnalysis ? getEnergyInfo(ledAnalysis.energy_info) : { consumption: 'Unknown', cost: 'Unknown' };

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
          <p>LED Action: {ledAnalysis.led_action || 'Unknown'}</p>
          <p>Energy Consumption: {energyInfo.consumption}</p>
          <p>Cost: {energyInfo.cost}</p>
          <div>
            <label htmlFor="analysisTextarea">Analysis Result:</label>
            <textarea
              id="analysisTextarea"
              value={ledAnalysis.analysis || ''}
              readOnly
              rows={5}
              style={{ width: '100%', marginTop: '10px' }}
            />
          </div>
        </>
      ) : (
        <p>No analysis data available</p>
      )}
    </div>
  );
};

export default LEDStats;