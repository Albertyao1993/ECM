// src/App.js
import React from 'react';
import SensorChart from './components/SensorChart';
import LiveStream from './components/LiveStream';

const App = () => {
  return (
    <div className="App">
      <h1>Sensor Data</h1>
      <SensorChart />
      <LiveStream />
    </div>
  );
};

export default App;
