// src/App.js
import React from 'react';
import { Container, Grid } from '@mui/material';
import SensorChart from './components/SensorChart';
import LiveStream from './components/LiveStream';

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
      </Grid>
    </Container>
  );
}

export default App;
