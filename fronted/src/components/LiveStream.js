import React, { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';

const LiveStream = () => {
  const imgRef = useRef(null); // 用于引用 <img> 标签
  const [personCount, setPersonCount] = useState(0);
  const socketRef = useRef(null); // 用于引用 WebSocket 实例
  const previousUrlRef = useRef(null); // 用 useRef 来存储上一个 Blob URL

  useEffect(() => {
    // 连接到 WebSocket 服务器
    socketRef.current = io('http://127.0.0.1:5000');

    // 监听 WebSocket 事件 'video_frame'
    socketRef.current.on('video_frame', (data) => {
      const { frame, person_count } = data;
      setPersonCount(person_count);

      if (imgRef.current) {
        // 创建 Blob 对象来存储图像数据
        const blob = new Blob([Uint8Array.from(atob(frame), c => c.charCodeAt(0))], { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob); // 创建新的 Blob URL
        imgRef.current.src = url; // 将 Blob URL 设置为 <img> 标签的 src

        // 释放之前的 Blob URL 以避免内存泄漏
        if (previousUrlRef.current) {
          URL.revokeObjectURL(previousUrlRef.current);
        }
        previousUrlRef.current = url; // 更新 previousUrlRef.current
      }
    });

    // 组件卸载时清理
    return () => {
      socketRef.current.disconnect(); // 断开 WebSocket 连接
      if (previousUrlRef.current) {
        URL.revokeObjectURL(previousUrlRef.current); // 释放最后一个 Blob URL
      }
    };
  }, []);

  return (
    <div>
      <h1>Live Stream</h1>
      <img ref={imgRef} width="640" height="480" alt="Live Stream" /> {/* 使用 <img> 标签来显示视频帧 */}
      <p>Person Count: {personCount}</p>
    </div>
  );
};

export default LiveStream;
