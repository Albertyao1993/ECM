// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import { Container, Grid } from '@mui/material';
import SensorChart from './components/SensorChart';
import LiveStream from './components/LiveStream';
import SensorStatus from './components/SensorStatus';
import RealTimeChart from './components/RealTimeChart';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  return (
    <Router>
      <Container>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Link to="/">Home</Link> | <Link to="/realtime">Real-Time Data</Link>
          </Grid>
          <Routes>
            <Route
              path="/"
              element={
                <Grid item xs={12}>
                  <LiveStream />
                  <SensorStatus />
                  <SensorChart />
                </Grid>
              }
            />
            <Route
              path="/realtime"
              element={
                <Grid item xs={12}>
                  <RealTimeChart />
                </Grid>
              }
            />
          </Routes>
        </Grid>
      </Container>
    </Router>
  );
}

export default App;
