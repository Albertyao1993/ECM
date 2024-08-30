// import logo from './logo.svg';
// import './App.css';

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }


import React, { useState, useEffect } from 'react';
import socketIOClient from 'socket.io-client';

const App = () => {
  const [temperature, setTemperature] = useState(null);

  useEffect(() => {
    const socket = socketIOClient("http://localhost:5000", {
      transports: ["websocket"],
      upgrade: false
    });
    socket.on("connect", () => {
      console.log("Connected to server");
    });
    socket.on("connect_error", (err) => {
      console.error("Connection error:", err);
    });
    
    socket.on("temperature_update", (data) => {	
      console.log("Received temperature data: ", data);
      setTemperature(data.temperature);
    });
    // socket.on("disconnect", () => {
    //   console.log("Disconnected from server");
    // });
    
    return () => {
      socket.off("temperature_update");
      socket.disconnect();
    };
    }, []);

  return (
	<div>
	  <h1>Temperature: {temperature}</h1>
	</div>
  );
};

export default App;
