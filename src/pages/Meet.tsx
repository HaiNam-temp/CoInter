import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom'; // Add the import for useNavigate
import '@fortawesome/fontawesome-free/css/all.min.css';
import '../Css/Meet.css';

import {
  handleMicToggle,
  handleCameraToggle,
  handleFileUpload,
} from '../scripts/meetscript.js';

const Meet: React.FC = () => {
  const navigate = useNavigate(); // Initialize useNavigate hook
  const [isMicOn, setIsMicOn] = useState(true);
  const [isCameraOn, setIsCameraOn] = useState(true);
  const [isCallActive, setIsCallActive] = useState(true);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    const initializeMedia = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        const videoElement = document.querySelector('#user-video video') as HTMLVideoElement;
        if (videoElement) {
          videoElement.srcObject = stream;
        }
        mediaRecorderRef.current = new MediaRecorder(stream);

        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };
      } catch (error) {
        console.error('Lỗi khi truy cập camera/micro:', error);
      }
    };

    initializeMedia();
  }, []);

  const handleMicPress = (event: React.MouseEvent | React.TouchEvent) => {
    event.preventDefault(); // Prevent form submission
    if (mediaRecorderRef.current) {
      audioChunksRef.current = []; // Reset audio chunks
      mediaRecorderRef.current.start();
      console.log('Bắt đầu ghi âm...');
    }
  };

  const handleMicRelease = (event: React.MouseEvent | React.TouchEvent) => {
    // Prevent default behavior
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      console.log('Dừng ghi âm...');
    
      // Define the handler outside the event context
      const handleRecordingStopped = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
    
        // Use a timeout to break the event chain
        setTimeout(() => {
          // Use the older XMLHttpRequest instead of fetch
          const xhr = new XMLHttpRequest();
          xhr.open('POST', 'http://localhost:5000/process_audio', true);
          xhr.responseType = 'blob';
          
          xhr.onload = function() {
            if (xhr.status === 200) {
              const blob = xhr.response;
              const audioUrl = URL.createObjectURL(blob);
              const audio = new Audio(audioUrl);
              
              // Play the audio
              audio.play();
              
              // Clean up audio URL when done
              audio.onended = function() {
                URL.revokeObjectURL(audioUrl);
              };
            }
          };
          
          xhr.send(formData);
        }, 0);
      };
    
      // Set up the onstop handler and clear it after use
      mediaRecorderRef.current.onstop = () => {
        handleRecordingStopped();
        if (mediaRecorderRef.current) {
          mediaRecorderRef.current.onstop = null;
        }
      };
    }
    
    return false;
  };

  // Custom call toggle handler that navigates to rating page
  const handleEndCall = () => {
    setIsCallActive(false);
    
    // Navigate to the rating page after a short delay to show the "call ended" message
    setTimeout(() => {
      navigate('/interview-rating');
    }, 1500);
  };

  return (
    <>
      <div id="main-content" className="full-width-video">
        <div id="video-area">
          {isCallActive ? (
            <>
              <div id="virtual-person-video">
                <video autoPlay playsInline loop muted src="/video/test.mp4" poster="placeholder_virtual.png"></video>
                <i className="fas fa-volume-up speaking-indicator" id="virtual-speaking-indicator"></i>
                <span className="video-label">Ms.Lee</span>
              </div>
              <div id="user-video">
                <video autoPlay muted playsInline style={{ display: isCameraOn ? 'block' : 'none' }}></video>
                {!isCameraOn && (
                  <i className="fas fa-user placeholder-icon" style={{ fontSize: '3em', color: '#ccc' }}></i>
                )}
                <i className="fas fa-volume-up speaking-indicator" id="user-speaking-indicator"></i>
                <span className="video-label">Bạn</span>
              </div>
            </>
          ) : (
            <div id="end-call-video">
              <div className="call-ending-message">
                <i className="fas fa-check-circle"></i>
                <p>Cuộc gọi đã kết thúc</p>
                <p className="redirect-text">Đang chuyển đến trang đánh giá...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div id="controls">
        <div className="controls-container">
          {/* Nút mic với chức năng ghi âm */}
          <button
            type="button"
            id="mic-toggle"
            onMouseDown={handleMicPress}
            onMouseUp={handleMicRelease}
            onTouchStart={handleMicPress}
            onTouchEnd={handleMicRelease}
          >
            <i className={`fas ${isMicOn ? 'fa-microphone' : 'fa-microphone-slash'}`}></i>
          </button>

          {/* Giữ nguyên các nút khác */}
          <button type="button" id="camera-toggle" onClick={() => handleCameraToggle(isCameraOn, setIsCameraOn)}>
            <i className={`fas ${isCameraOn ? 'fa-video' : 'fa-video-slash'}`}></i>
          </button>
          <input type="file" id="cv-upload-input" hidden onChange={(e) => handleFileUpload(e.target.files?.[0])} />
          <button type="button" id="upload-cv-button" onClick={() => document.getElementById('cv-upload-input')?.click()}>
            <i className="fas fa-file-arrow-up"></i>
          </button>
          <button type="button" id="call-toggle" onClick={handleEndCall}>
            <i className="fas fa-phone-slash"></i>
          </button>
        </div>
      </div>
    </>
  );
};

export default Meet;