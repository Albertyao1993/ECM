import React, { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';

const LiveStream = () => {
  // const canvasRef = useRef(null);
  const [personCount, setPersonCount] = useState(0);
  const socketRef = useRef(null);

  useEffect(() => {
    // WebSocket连接到后端
    socketRef.current = io('http://127.0.0.1:5000');

    // 监听后端发送的帧
    socketRef.current.on('video_frame', (data) => {
      const { frame, person_count, boxes } = data;
      setPersonCount(person_count);

      // // 创建图像对象
      // const img = new Image();
      // img.src = `data:image/jpeg;base64,${frame}`;

      // img.onload = () => {
      //   const canvas = canvasRef.current;
      //   const ctx = canvas.getContext('2d');
      //   ctx.clearRect(0, 0, canvas.width, canvas.height);  // 清除上一次绘制的内容

      //   // 调整canvas大小
      //   canvas.width = img.width;
      //   canvas.height = img.height;
        
      //   // 绘制接收到的帧
      //   ctx.drawImage(img, 0, 0);

      //   // 绘制检测框
      //   boxes.forEach(box => {
      //     const [x, y, width, height] = box;
      //     ctx.strokeStyle = 'red';
      //     ctx.lineWidth = 2;
      //     ctx.strokeRect(x, y, width, height);
      //   });
      // };
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  return (
    <div>
      <h1>Live Stream with Person Detection</h1>
      {/* <canvas ref={canvasRef} style={{ width: '640px', height: '480px' }} /> */}
      <p>Person Count: {personCount}</p>
    </div>
  );
};

export default LiveStream;
