import React, { useEffect, useState, useRef } from 'react';
import '@fortawesome/fontawesome-free/css/all.min.css';
import '../Css/Meet.css';

import {
  handleMicToggle,
  handleCameraToggle,
  handleCallToggle,
  handleSendMessage,
  handleFileUpload,
  handleSwitchMode,
} from '../scripts/meetscript.js';

const Meet: React.FC = () => {
  const [isMicOn, setIsMicOn] = useState(true);
  const [isCameraOn, setIsCameraOn] = useState(true);
  const [isCallActive, setIsCallActive] = useState(true);
  const [currentMode, setCurrentMode] = useState('general');
  const [chatMessages, setChatMessages] = useState<Record<string, { sender: 'user' | 'server'; text: string }[]>>({
    general: [],
    cv: [],
    tech: [],
  });
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const chatContainerRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    // Global form submission preventer
    const handleFormSubmit = (e: Event) => {
      e.preventDefault();
      return false;
    };
    
    // Find and prevent any form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      form.addEventListener('submit', handleFormSubmit);
    });
    
    // Prevent keyboard enter from submitting
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && e.target instanceof HTMLInputElement) {
        e.preventDefault();
        if (e.target.id === 'message-input') {
          handleSendMessageWrapper();
        }
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      forms.forEach(form => {
        form.removeEventListener('submit', handleFormSubmit);
      });
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const handleSendMessageWrapper = () => {
    const messageInput = document.getElementById('message-input') as HTMLInputElement;
    if (messageInput) {
      const userMessage = messageInput.value.trim();
      handleSendMessage(userMessage, currentMode, chatMessages, setChatMessages);
      messageInput.value = ''; // Clear input field
    }
  };

  const handleFileUploadWrapper = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileUpload(file, currentMode, chatMessages, setChatMessages);
    }
  };

  const handleSwitchModeWrapper = (newMode: string) => {
    handleSwitchMode(newMode, setCurrentMode, chatMessages, setChatMessages);
  };

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
              
              // When audio ends, get messages
              audio.onended = function() {
                // Use another XHR for getting messages
                const msgXhr = new XMLHttpRequest();
                msgXhr.open('GET', 'http://localhost:5000/get_last_messages', true);
                msgXhr.responseType = 'json';
                
                msgXhr.onload = function() {
                  if (msgXhr.status === 200) {
                    const data = msgXhr.response;
                    
                    // Update the React state instead of DOM manipulation
                    setChatMessages(prevMessages => ({
                      ...prevMessages,
                      general: [
                        ...prevMessages.general,
                        { sender: 'user', text: data.user_message },
                        { sender: 'server', text: data.bot_reply }
                      ]
                      // Don't modify the other chat modes
                    }));
                    
                    // If currently in general mode, scroll to bottom after React updates the DOM
                    if (currentMode === 'general') {
                      setTimeout(() => {
                        const chatMessagesDiv = document.getElementById('chat-messages');
                        if (chatMessagesDiv) {
                          chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
                        }
                      }, 100); // Give React time to update the DOM
                    }
                    
                    // Clean up audio URL
                    URL.revokeObjectURL(audioUrl);
                  }
                };
                
                msgXhr.send();
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

  return (
    <>
      <div id="main-content">
        <div id="video-area">
          {isCallActive ? (
            <>
              <div id="virtual-person-video">
                <video autoPlay playsInline loop muted poster="placeholder_virtual.png"></video>
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
              <div style={{ color: '#fff', textAlign: 'center' }}>Cuộc gọi đã kết thúc</div>
            </div>
          )}
        </div>

        <div id="chat-container">
          <div id="chat-mode-icons">
            <button
              type="button"
              className={`mode-button ${currentMode === 'general' ? 'active-mode' : ''}`}
              onClick={() => handleSwitchModeWrapper('general')}
            >
              <i className="fas fa-comments"></i>
            </button>
            <button
              type="button"
              className={`mode-button ${currentMode === 'cv' ? 'active-mode' : ''}`}
              onClick={() => handleSwitchModeWrapper('cv')}
            >
              <i className="fas fa-file-alt"></i>
            </button>
            <button
              type="button"
              className={`mode-button ${currentMode === 'tech' ? 'active-mode' : ''}`}
              onClick={() => handleSwitchModeWrapper('tech')}
            >
              <i className="fas fa-code"></i>
            </button>
          </div>

          <div id="chat-messages" ref={chatContainerRef}>
            {chatMessages[currentMode].map((message, index) => (
              <p key={index} className={message.sender === 'user' ? 'sent' : 'received'}>
                {message.text}
              </p>
            ))}
          </div>

          <div id="chat-input-area" onSubmit={(e) => e.preventDefault()}>
            <input 
              type="text" 
              id="message-input" 
              placeholder="Nhập tin nhắn chung..." 
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleSendMessageWrapper();
                }
              }}
            />
            <button type="button" id="send-button" onClick={handleSendMessageWrapper}>
              <i className="fas fa-paper-plane"></i>
            </button>
          </div>
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
          <input type="file" id="cv-upload-input" hidden onChange={handleFileUploadWrapper} />
          <button type="button" id="upload-cv-button" onClick={() => document.getElementById('cv-upload-input')?.click()}>
            <i className="fas fa-file-arrow-up"></i>
          </button>
          <button type="button" id="call-toggle" onClick={() => handleCallToggle(isCallActive, setIsCallActive)}>
            <i className={`fas ${isCallActive ? 'fa-phone' : 'fa-phone-slash'}`}></i>
          </button>
        </div>
      </div>
    </>
  );
};

export default Meet;