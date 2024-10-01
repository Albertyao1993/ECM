import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SensorStatus = () => {
  const [acState, setAcState] = useState(false);
  const [windowState, setWindowState] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/data/ac_state');
        const data = response.data;
        setAcState(data.ac_state);
        setWindowState(data.window_state);
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
    </div>
  );
};

export default SensorStatus;