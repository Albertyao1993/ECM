import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import SensorStatus from './components/SensorStatus';
import SensorChart from './components/SensorChart';
import LiveStream from './components/LiveStream';
import LEDStats from './components/LEDStats';
import RealTimeChart from './components/RealTimeChart';
import './App.css'; // 确保您有这个文件来存放 CSS

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
              <LiveStream />
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
