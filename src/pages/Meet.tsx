// --- START OF FILE Meet.tsx ---

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import '@fortawesome/fontawesome-free/css/all.min.css';
import '../Css/Meet.css';

// Các hàm này có thể giữ nguyên nếu bạn vẫn cần chúng
import {
  handleCameraToggle,
} from '../scripts/meetscript.js';

// Khai báo kiểu cho các hàm global từ script bên ngoài (nếu có)
declare global {
  interface Window {
    start: () => void;
    stop: () => void;
    updateSessionId: (id: string) => void;
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

// Type declarations for Web Speech API
interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onstart: () => void;
  onresult: (event: any) => void;
  onerror: (event: any) => void;
  onend: () => void;
}

const Meet: React.FC = () => {
  const navigate = useNavigate();
  const [isMicOn, setIsMicOn] = useState(true); // State này giờ chỉ mang tính hình ảnh
  const [isCameraOn, setIsCameraOn] = useState(true);
  const [lastRecording, setLastRecording] = useState<Blob | null>(null);
  const [isCallActive, setIsCallActive] = useState(true);
  const [cvAnalysis, setCvAnalysis] = useState<any>(null);
  const [isUploadingCV, setIsUploadingCV] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [sessionId, setSessionId] = useState("0");
  const greetingPlayedRef = useRef<boolean>(false); // Track if greeting has been played

  // ================= STATE VÀ REF MỚI CHO SPEECH RECOGNITION =================
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const [isRecognizing, setIsRecognizing] = useState(false);
  // Dùng ref để lưu văn bản cuối cùng, tránh re-render không cần thiết
  const finalTranscriptRef = useRef('');
  // ========================================================================

  useEffect(() => {
    const initializeMedia = async () => {
      try {
        // --- Phần khởi tạo Camera và Video (giữ nguyên) ---
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        const videoElement = document.querySelector('#user-video video') as HTMLVideoElement;
        if (videoElement) {
          videoElement.srcObject = stream;
        }

        // --- Phần khởi tạo MediaRecorder để ghi âm (giữ nguyên cho tính năng download) ---
        const audioStream = await navigator.mediaDevices.getUserMedia({ video: false, audio: true });
        const options = { mimeType: 'audio/webm;codecs=opus' };
        if (MediaRecorder.isTypeSupported(options.mimeType)) {
          mediaRecorderRef.current = new MediaRecorder(audioStream, options);
          mediaRecorderRef.current.ondataavailable = (event) => {
            if (event.data.size > 0) {
              audioChunksRef.current.push(event.data);
            }
          };
        } else {
            console.warn("MimeType audio/webm;codecs=opus không được hỗ trợ.");
        }


        window.updateSessionId = (id: string) => {
          console.log("SessionID received:", id);
          setSessionId(id);
        };

        // --- PHẦN MỚI: KHỞI TẠO WEB SPEECH API ---
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
          const recognition = new SpeechRecognition();
          recognition.continuous = false; // Dừng khi người dùng ngưng nói
          recognition.interimResults = true; // Trả kết quả tạm thời
          recognition.lang = 'vi-VN'; // Đặt ngôn ngữ nhận diện

          recognition.onstart = () => {
            setIsRecognizing(true);
            finalTranscriptRef.current = ''; // Xóa văn bản của lần nói trước
            console.log('Bắt đầu nhận diện giọng nói...');
          };

          recognition.onresult = (event) => {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
              if (event.results[i].isFinal) {
                finalTranscriptRef.current += event.results[i][0].transcript;
              } else {
                interimTranscript += event.results[i][0].transcript;
              }
            }
            // Bạn có thể hiển thị `interimTranscript` lên UI nếu muốn
          };

          recognition.onerror = (event) => {
            console.error('Lỗi Speech Recognition:', event.error);
            setIsRecognizing(false);
          };

          // Sự kiện quan trọng nhất: được kích hoạt sau khi `stop()` được gọi
          recognition.onend = () => {
            setIsRecognizing(false);
            console.log('Kết thúc nhận diện giọng nói.');
            // console.log("hello");
            const finalText = finalTranscriptRef.current.trim();
            if (finalText) {
              console.log(finalText);
              // Gọi hàm xử lý logic chính
              handleVoiceProcessing(finalText);
            }
          };

          recognitionRef.current = recognition;
        } else {
          alert('Trình duyệt của bạn không hỗ trợ nhận diện giọng nói.');
        }

      } catch (error) {
        console.error('Lỗi khi truy cập camera/micro:', error);
      }
    };

    // Function to play interview greeting audio
    const playInterviewGreeting = async () => {
      // Check if greeting has already been played
      if (greetingPlayedRef.current) {
        console.log('🎵 Interview greeting already played, skipping...');
        return;
      }

      try {
        console.log('🎵 Loading interview greeting audio...');
        greetingPlayedRef.current = true; // Mark as played immediately to prevent double calls
        
        const response = await fetch('http://localhost:5000/get_interview_greeting/interview_greeting.mp3');
        
        if (response.ok) {
          const audioBlob = await response.blob();
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          
          // Play the greeting audio
          audio.play().then(() => {
            console.log('🎵 Interview greeting audio started playing');
          }).catch((error) => {
            console.error('Error playing interview greeting audio:', error);
            greetingPlayedRef.current = false; // Reset on error to allow retry
          });
          
          // Clean up audio URL when done
          audio.onended = function() {
            URL.revokeObjectURL(audioUrl);
            console.log('🎵 Interview greeting audio finished playing');
          };
        } else {
          console.warn('Interview greeting audio not found or not ready yet');
          greetingPlayedRef.current = false; // Reset on error to allow retry
        }
      } catch (error) {
        console.error('Error loading interview greeting audio:', error);
        greetingPlayedRef.current = false; // Reset on error to allow retry
      }
    };

    const initializeAll = async () => {
      await initializeMedia();
      // Play greeting audio after media is initialized
      setTimeout(() => {
        playInterviewGreeting();
      }, 1000); // Delay to ensure everything is ready
    };

    initializeAll();
  }, []);

  // Hàm yêu cầu Model Digital Human nói (Echo)
  const makeModelSpeak = useCallback((textToSpeak: string) => {
    console.log(`Yêu cầu model nói: "${textToSpeak}"`);


    // Gọi API của Digital Human để nó nói ra văn bản
    fetch('/human', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: textToSpeak,
        type: 'echo', // Quan trọng: Đây là chế độ chỉ nói
        interrupt: true,
        sessionid: parseInt(document.getElementById('sessionid').value),
      }),
    }).catch(error => console.error('Lỗi khi yêu cầu model nói:', error));
  }, []);

  // Hàm điều phối chính: gửi text đến backend xử lý và nhận lại kết quả
  const handleVoiceProcessing = useCallback(async (text: string) => {
    try {
      console.log(`Gửi văn bản đến backend xử lý: "${text}"`);
      // Hiển thị loading hoặc thay đổi icon mic để báo hiệu đang xử lý
      // TODO: Thêm logic UI loading ở đây

      // 1. Gửi văn bản đến backend của bạn để xử lý với GPT-4
      const response = await fetch('https://192.168.1.15:5000/process_text', { // <<< THAY URL BACKEND CỦA BẠN VÀO ĐÂY
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Thêm các header khác nếu cần, ví dụ Authorization
        },
        body: JSON.stringify({
          user_message: text,
            sessionid: parseInt(document.getElementById('sessionid').value),
        }),
      });

      if (!response.ok) {
        throw new Error(`Lỗi từ backend: ${response.statusText}`);
      }

      // 2. Nhận lại văn bản phản hồi từ backend
      // const data = await response.json();
      // const gptResponseText = data.response; // Giả sử backend trả về { "response": "..." }

      // if (gptResponseText) {
      //   // 3. Yêu cầu model digital human nói ra văn bản đó
      //   makeModelSpeak(gptResponseText);
      // } else {
      //   console.warn("Backend không trả về văn bản phản hồi.");
      // }

    } catch (error) {
      console.error('Lỗi trong quá trình xử lý giọng nói:', error);
      makeModelSpeak("Tôi xin lỗi, đã có lỗi xảy ra. Bạn vui lòng thử lại nhé.");
    } finally {
        // Tắt trạng thái loading
        // TODO: Thêm logic tắt UI loading ở đây
    }
  }, []);


  // --- CÁC HÀM XỬ LÝ SỰ KIỆN ĐÃ ĐƯỢC ĐƠN GIẢN HÓA ---

  const handleMicPress = (event: React.MouseEvent | React.TouchEvent) => {
    event.preventDefault();
    if (recognitionRef.current && !isRecognizing) {
      try {
        // Bắt đầu cả ghi âm (cho download) và nhận diện giọng nói
        mediaRecorderRef.current?.start();
        console.log(mediaRecorderRef.current?.state);
        recognitionRef.current.start();
      } catch(e) {
        console.error("Lỗi khi bắt đầu nhận diện, có thể đang chạy:", e);
      }
    }
  };

  const handleMicRelease = (event: React.MouseEvent | React.TouchEvent) => {
    event.preventDefault();
    if (recognitionRef.current && isRecognizing) {
      // Dừng cả hai
      mediaRecorderRef.current?.stop();
      recognitionRef.current.stop();
    }
  };

  // --- CÁC HÀM KHÁC GIỮ NGUYÊN ---
  const handleDownloadLastRecording = () => {
    // Logic này vẫn hoạt động vì chúng ta vẫn chạy MediaRecorder
    if(mediaRecorderRef.current) {
        mediaRecorderRef.current.onstop = () => {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            if (audioBlob.size > 0) {
                const url = URL.createObjectURL(audioBlob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `recording-${new Date().toISOString()}.webm`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
            // Reset handler
            if (mediaRecorderRef.current) mediaRecorderRef.current.onstop = null;
        }
    }
    
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      console.log('Dừng ghi âm...');
    
      // Define the handler outside the event context
      const handleRecordingStopped = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
    
        try {
          console.log('🎯 Starting 3-step audio processing...');
          
          // Step 1: Convert audio to text
          console.log('📝 Step 1: Converting audio to text...');
          const audioToTextResponse = await fetch('http://localhost:5000/audio_to_text', {
            method: 'POST',
            body: formData,
          });
          
          if (!audioToTextResponse.ok) {
            throw new Error(`Audio to text failed: ${audioToTextResponse.statusText}`);
          }
          
          const audioToTextData = await audioToTextResponse.json();
          const userTranscript = audioToTextData.transcript;
          
          console.log('🎙️ User transcript:', userTranscript);
          
          // Step 2: Get AI response text
          console.log('🤖 Step 2: Getting AI response text...');
          const responseTextResponse = await fetch('http://localhost:5000/response_text', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              transcript: userTranscript
            }),
          });
          
          if (!responseTextResponse.ok) {
            throw new Error(`Response text generation failed: ${responseTextResponse.statusText}`);
          }
          
          const responseTextData = await responseTextResponse.json();
          const aiResponseText = responseTextData.response_text;
          
          console.log('💬 AI response text:', aiResponseText);
          
          // Step 3: Convert AI response text to audio and play it
          console.log('� Step 3: Converting AI response to audio...');
          const generateAudioResponse = await fetch('http://localhost:5000/generate_audio', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text: aiResponseText,
              filename: 'interview_response.mp3'
            }),
          });
          
          if (!generateAudioResponse.ok) {
            throw new Error(`Audio generation failed: ${generateAudioResponse.statusText}`);
          }
          
          // Get the audio blob and play it
          const audioBlob = await generateAudioResponse.blob();
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          
          console.log('🎵 Playing AI response audio...');
          
          // Play the audio
          audio.play().then(() => {
            console.log('✅ Audio playback started successfully');
          }).catch((error) => {
            console.error('❌ Error playing audio:', error);
          });
          
          // Clean up audio URL when done
          audio.onended = function() {
            URL.revokeObjectURL(audioUrl);
            console.log('🎵 Audio playback completed');
          };
          
          // Log summary
          console.log('✅ 3-step audio processing completed successfully!');
          console.log('📊 Processing Summary:');
          console.log(`   👤 User said: "${userTranscript}"`);
          console.log(`   🤖 AI responded: "${aiResponseText.substring(0, 100)}${aiResponseText.length > 100 ? '...' : ''}"`);
          
        } catch (error) {
          console.error('❌ Error in 3-step audio processing:', error);
          
          // Show user-friendly error message
          // You can add UI notification here
          alert('Đã có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại.');
        }
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

  const handleEndCall = () => {
    setIsCallActive(false);
    setTimeout(() => {
      navigate('/interview-rating');
    }, 1500);
  };

  // Handle CV upload and analysis
  const handleCVUpload = async (file: File | null) => {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please select a PDF file');
      return;
    }

    setIsUploadingCV(true);
    
    try {
      const formData = new FormData();
      formData.append('cv', file);

      const response = await fetch('http://localhost:5000/upload_cv', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        console.log('✅ CV uploaded and analyzed successfully');
        console.log('📄 Extracted text preview:', data.extracted_text);
        console.log('🔍 CV Analysis:', data.analysis);
        
        setCvAnalysis(data.analysis);
        
        // Update CV information in the interview system
        try {
          const updateResponse = await fetch('http://localhost:5000/update_cv_info', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              cv_analysis: data.analysis
            }),
          });

          if (updateResponse.ok) {
            console.log('✅ CV information updated in interview system');
            alert('CV uploaded and analyzed successfully! The analysis will be used in the interview.');
          } else {
            console.error('❌ Error updating CV in interview system');
            alert('CV uploaded but there was an issue updating the interview system. Please try again.');
          }
        } catch (updateError) {
          console.error('❌ Network error updating interview system:', updateError);
          alert('CV uploaded but failed to update interview system. Please try again.');
        }
      } else {
        console.error('❌ Error uploading CV:', data.error);
        alert(`Error uploading CV: ${data.error}`);
      }
    } catch (error) {
      console.error('❌ Network error uploading CV:', error);
      alert('Network error occurred while uploading CV. Please try again.');
    } finally {
      setIsUploadingCV(false);
    }
  };

  return (
    <>
      <input type="hidden" id="sessionid" value={sessionId} />
      <div id="main-content" className="full-width-video">
        <div id="video-area">
          {isCallActive ? (
            <>
              <div id="virtual-person-video">
                <video id="video" autoPlay playsInline loop muted poster="placeholder_virtual.png"></video>
                <audio id="audio" autoPlay></audio>

                {/* Nút này dùng để bắt đầu kết nối WebRTC ban đầu */}
                <button id="start" className="play-button" onClick={window.start}>
                  <i className="fas fa-play"></i>
                </button>
                <button id="stop" className="stop-button" onClick={window.stop} style={{display:"none"}}>
                  <i className="fas fa-stop"></i>
                </button>

                <i className="fas fa-volume-up speaking-indicator" id="virtual-speaking-indicator"></i>
                <span className="video-label">Ms.Lee</span>
              </div>
              <div id="user-video">
                <video autoPlay muted playsInline style={{display: isCameraOn ? 'block' : 'none'}}></video>
                {!isCameraOn && (
                  <i className="fas fa-user placeholder-icon" style={{fontSize: '3em', color: '#ccc'}}></i>
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
          <button
            type="button"
            id="mic-toggle"
            onMouseDown={handleMicPress}
            onMouseUp={handleMicRelease}
            onTouchStart={handleMicPress}
            onTouchEnd={handleMicRelease}
            // Thêm class để thay đổi hình ảnh khi đang nhận diện
            className={isRecognizing ? 'recording' : ''}
          >
            <i className={`fas ${isMicOn ? 'fa-microphone' : 'fa-microphone-slash'}`}></i>
          </button>

          <button type="button" id="camera-toggle" onClick={() => handleCameraToggle(isCameraOn, setIsCameraOn)}>
            <i className={`fas ${isCameraOn ? 'fa-video' : 'fa-video-slash'}`}></i>
          </button>
          <input 
            type="file" 
            id="cv-upload-input" 
            hidden 
            accept=".pdf"
            onChange={(e) => handleCVUpload(e.target.files?.[0] || null)} 
          />
          <button 
            type="button" 
            id="upload-cv-button" 
            onClick={() => document.getElementById('cv-upload-input')?.click()}
            disabled={isUploadingCV}
            title="Upload CV (PDF only)"
          >
            <i className={`fas ${isUploadingCV ? 'fa-spinner fa-spin' : 'fa-file-arrow-up'}`}></i>
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