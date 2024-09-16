import React, { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';

const LiveStream = () => {
  const videoRef = useRef(null);
  const [personCount, setPersonCount] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = io('http://127.0.0.1:5000');

    socketRef.current.on('video_frame', (data) => {
      const { frame, person_count } = data;
      setPersonCount(person_count);

      if (videoRef.current) {
        const blob = new Blob([frame], { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob);
        videoRef.current.src = url;
      }
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, []);

  const handlePlay = () => {
    setIsPlaying(true);
  };

  return (
    <div>
      <h1>Live Stream</h1>
      <video ref={videoRef} width="640" height="480" controls autoPlay />
      <p>Person Count: {personCount}</p>
      {!isPlaying && <button onClick={handlePlay}>Start Live Stream</button>}
    </div>
  );
};

export default LiveStream;