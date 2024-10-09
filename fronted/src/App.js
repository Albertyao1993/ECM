import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import SensorStatus from './components/SensorStatus';
import SensorChart from './components/SensorChart';
import PersonCount from './components/LiveStream'; // 重命名组件
import LEDStats from './components/LEDStats';
import RealTimeChart from './components/RealTimeChart';
import './App.css'; // 确保您有这个文件来存放 CSS

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <Link to="/" className="nav-item">首页</Link>
          <Link to="/realtime" className="nav-item">实时图表</Link>
          <Link to="/led-stats" className="nav-item">LED 统计</Link>
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
