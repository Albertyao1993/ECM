import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import SensorStatus from './components/SensorStatus';
import SensorChart from './components/SensorChart';
import PersonCount from './components/LiveStream'; // Renamed component
import LEDStats from './components/LEDStats';
import RealTimeChart from './components/RealTimeChart';
import './App.css'; // Make sure you have this file for CSS

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <Link to="/" className="nav-item">Home</Link>
          <Link to="/realtime" className="nav-item">Real-time Chart</Link>
          <Link to="/led-stats" className="nav-item">LED Statistics</Link>
        </nav>

        <Routes>
          <Route path="/" element={
            <>
              <PersonCount />
              <SensorStatus />
              <SensorChart />
            </>
          } />
          <Route path="/led-stats" element={<LEDStats />} />
          <Route path="/realtime" element={<RealTimeChart />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
