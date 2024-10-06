import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const SensorStatus = () => {
  const [acState, setAcState] = useState(false);
  const [windowState, setWindowState] = useState(false);
  const [lightStatus, setLightStatus] = useState('OFF');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const acStateResponse = await axios.get('http://127.0.0.1:5000/data/ac_state');
        const lightStatusResponse = await axios.get('http://127.0.0.1:5000/data/led_status');
        
        setAcState(acStateResponse.data.ac_state);
        setWindowState(acStateResponse.data.window_state);
        setLightStatus(lightStatusResponse.data.led_status);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();

    const interval = setInterval(fetchData, 5000); // Update data every 5 seconds
    return () => clearInterval(interval); // Clear interval on component unmount
  }, []);

  return (
    <div>
      <h2>Sensor Status</h2>
      <p>AC State: {acState ? 'On' : 'Off'}</p>
      <p>Window State: {windowState ? 'Open' : 'Closed'}</p>
      <p>Light Status: <Link to="/led-stats">{lightStatus}</Link></p>
    </div>
  );
};

export default SensorStatus;