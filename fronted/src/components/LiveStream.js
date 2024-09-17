// import React, { useEffect, useRef, useState } from 'react';
// import io from 'socket.io-client';

// const LiveStream = () => {
//   const videoRef = useRef(null);
//   const [personCount, setPersonCount] = useState(0);
//   const socketRef = useRef(null);
//   const peerConnectionRef = useRef(null);

//   useEffect(() => {
//     // 连接到 WebSocket 服务器
//     socketRef.current = io('http://127.0.0.1:5000');

//     // 创建 RTCPeerConnection
//     peerConnectionRef.current = new RTCPeerConnection({
//       iceServers: [
//         { urls: 'stun:stun.l.google.com:19302' },
//       ],
//     });

//     // 处理 ICE 候选
//     peerConnectionRef.current.onicecandidate = (event) => {
//       if (event.candidate) {
//         socketRef.current.emit('ice-candidate', event.candidate);
//       }
//     };

//     // 处理远程流
//     peerConnectionRef.current.ontrack = (event) => {
//       if (videoRef.current) {
//         videoRef.current.srcObject = event.streams[0];
//       }
//     };

//     // 监听 WebSocket 事件 'offer'
//     socketRef.current.on('offer', async (data) => {
//       await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(data));
//       const answer = await peerConnectionRef.current.createAnswer();
//       await peerConnectionRef.current.setLocalDescription(answer);
//       socketRef.current.emit('answer', answer);
//     });

//     // 监听 WebSocket 事件 'answer'
//     socketRef.current.on('answer', async (data) => {
//       await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(data));
//     });

//     // 监听 WebSocket 事件 'ice-candidate'
//     socketRef.current.on('ice-candidate', async (data) => {
//       try {
//         await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(data));
//       } catch (e) {
//         console.error('Error adding received ice candidate', e);
//       }
//     });

//     // 组件卸载时清理
//     return () => {
//       socketRef.current.disconnect(); // 断开 WebSocket 连接
//       peerConnectionRef.current.close(); // 关闭 RTCPeerConnection
//     };
//   }, []);

//   return (
//     <div>
//       <h1>Live Stream</h1>
//       <video ref={videoRef} width="640" height="480" autoPlay playsInline /> {/* 使用 <video> 标签来显示视频流 */}
//       <p>Person Count: {personCount}</p>
//     </div>
//   );
// };

// export default LiveStream;



import React, { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';

const LiveStream = () => {
  const videoRef = useRef(null);
  const [personCount, setPersonCount] = useState(0);
  const socketRef = useRef(null);
  const peerConnectionRef = useRef(null);

  useEffect(() => {
    // 连接到 WebSocket 服务器
    socketRef.current = io('http://127.0.0.1:5000');
    console.log('Connecting to WebSocket server...');

    socketRef.current.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    // 创建 RTCPeerConnection
    peerConnectionRef.current = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
      ],
    });

    console.log('RTCPeerConnection created');

    // 处理 ICE 候选
    peerConnectionRef.current.onicecandidate = (event) => {
      if (event.candidate) {
        console.log('Sending ICE candidate');
        socketRef.current.emit('ice-candidate', event.candidate);
      }
    };

    // 处理远程流
    peerConnectionRef.current.ontrack = (event) => {
      console.log('Receiving remote stream');
      if (videoRef.current) {
        videoRef.current.srcObject = event.streams[0];
      }
    };

    // 监听 WebSocket 事件 'offer'
    socketRef.current.on('offer', async (data) => {
      console.log('Received offer');
      await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(data));
      const answer = await peerConnectionRef.current.createAnswer();
      await peerConnectionRef.current.setLocalDescription(answer);
      socketRef.current.emit('answer', answer);
    });

    // 监听 WebSocket 事件 'answer'
    socketRef.current.on('answer', async (data) => {
      console.log('Received answer');
      await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(data));
    });

    // 监听 WebSocket 事件 'ice-candidate'
    socketRef.current.on('ice-candidate', async (data) => {
      console.log('Received ICE candidate');
      try {
        await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(data));
      } catch (e) {
        console.error('Error adding received ice candidate', e);
      }
    });

    // 监听视频帧数据
    socketRef.current.on('video_frame', (data) => {
      console.log('Received video frame');
      if (videoRef.current) {
        videoRef.current.src = `data:image/jpeg;base64,${data.frame}`;
      }
      setPersonCount(data.person_count);
    });

    // 组件卸载时清理
    return () => {
      console.log('Cleaning up...');
      socketRef.current.disconnect();
      peerConnectionRef.current.close();
    };
  }, []);

  return (
    <div>
      <h1>Live Stream</h1>
      <img ref={videoRef} width="640" height="480" autoPlay playsInline />
      <p>Person Count: {personCount}</p>
    </div>
  );
};

export default LiveStream;
