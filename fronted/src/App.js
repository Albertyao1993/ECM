// src/App.js
import React from 'react';
import { Container, Grid } from '@mui/material';
import SensorChart from './components/SensorChart';
import LiveStream from './components/LiveStream';
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
import LightSensorChart from './components/LightSensorChart';

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
    <Container>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <LiveStream />
        </Grid>
        <Grid item xs={12}>
          <SensorChart />
        </Grid>
        <Grid item xs={12}>
          <LightSensorChart />
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;
