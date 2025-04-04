/**
 * Toggles the microphone state.
 * @param {boolean} isMicOn - Current microphone state.
 * @param {function} setIsMicOn - State updater for microphone state.
 */
export const handleMicToggle = (isMicOn, setIsMicOn) => {
    const videoElement = document.querySelector('#user-video video');
    if (videoElement && videoElement.srcObject) {
      const stream = videoElement.srcObject;
      const audioTrack = stream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled; // Toggle audio track
        setIsMicOn(audioTrack.enabled); // Update state
        console.log(`Micro ${audioTrack.enabled ? 'bật' : 'tắt'}`);
      }
    }
  };
  
  /**
   * Toggles the camera state.
   * @param {boolean} isCameraOn - Current camera state.
   * @param {function} setIsCameraOn - State updater for camera state.
   */
  export const handleCameraToggle = (isCameraOn, setIsCameraOn) => {
    const videoElement = document.querySelector('#user-video video');
    if (videoElement && videoElement.srcObject) {
      const stream = videoElement.srcObject;
      const videoTrack = stream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled; // Toggle video track
        setIsCameraOn(videoTrack.enabled); // Update state
        console.log(`Camera ${videoTrack.enabled ? 'bật' : 'tắt'}`);
      }
    }
  };
  
  /**
   * Toggles the call state.
   * @param {boolean} isCallActive - Current call state.
   * @param {function} setIsCallActive - State updater for call state.
   */
  export const handleCallToggle = (isCallActive, setIsCallActive) => {
    setIsCallActive(!isCallActive); // Toggle call state
    if (isCallActive) {
      const endCallVideo = document.querySelector('#end-call-video video');
      if (endCallVideo) {
        endCallVideo.srcObject = null; // Clear video content
        endCallVideo.removeAttribute('src'); // Remove src attribute
        endCallVideo.load(); // Reload video
      }
    }
    console.log(`Cuộc gọi ${isCallActive ? 'kết thúc' : 'bắt đầu'}`);
  };
  
  /**
   * Handles sending a message and updating the chat messages.
   * @param {string} userMessage - The message sent by the user.
   * @param {string} currentMode - The current chat mode.
   * @param {object} chatMessages - The current chat messages object.
   * @param {function} setChatMessages - The state updater function for chat messages.
   */
  export const handleSendMessage = (userMessage, currentMode, chatMessages, setChatMessages) => {
    if (userMessage.trim() !== '') {
      setChatMessages((prevMessages) => ({
        ...prevMessages,
        [currentMode]: [...prevMessages[currentMode], { sender: 'user', text: userMessage }],
      }));
  
      // Simulate a response from the system
      setTimeout(() => {
        const responseMessage = `Phản hồi cho "${userMessage}"`;
        setChatMessages((prevMessages) => ({
          ...prevMessages,
          [currentMode]: [...prevMessages[currentMode], { sender: 'server', text: responseMessage }],
        }));
      }, 1000); // Simulate delay for response
    }
  };
  
  /**
   * Handles file upload and updates the chat messages.
   * @param {File} file - The uploaded file.
   * @param {string} currentMode - The current chat mode.
   * @param {object} chatMessages - The current chat messages object.
   * @param {function} setChatMessages - The state updater function for chat messages.
   */
  export const handleFileUpload = (file, currentMode, chatMessages, setChatMessages) => {
    if (file) {
      setChatMessages((prevMessages) => ({
        ...prevMessages,
        [currentMode]: [
          ...prevMessages[currentMode],
          { sender: 'user', text: `đang phân tích "${file.name}"` },
        ],
      }));
      console.log(`File uploaded: ${file.name}`);
    }
  };
  
  /**
   * Switches the chat mode and adds an introductory message if it's the first time.
   * @param {string} newMode - The new chat mode to switch to.
   * @param {function} setCurrentMode - The state updater for the current mode.
   * @param {object} chatMessages - The current chat messages object.
   * @param {function} setChatMessages - The state updater function for chat messages.
   */
  export const handleSwitchMode = (newMode, setCurrentMode, chatMessages, setChatMessages) => {
    setCurrentMode(newMode);
  
    // Add an introductory message for the new mode if it's empty
    const modeIntroduction = {
      general: 'Bạn đang ở chế độ chat Chung.',
      cv: 'Bạn đang ở chế độ thảo luận CV.',
      tech: 'Bạn đang ở chế độ hỏi đáp Kỹ thuật.',
    };
  
    if (chatMessages[newMode].length === 0) {
      setChatMessages((prevMessages) => ({
        ...prevMessages,
        [newMode]: [{ sender: 'server', text: modeIntroduction[newMode] }],
      }));
    }
  };