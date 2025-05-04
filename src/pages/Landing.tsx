import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Home, Tv, LogOut, Video } from 'lucide-react';
import '../Css/Landing.css';

// At the top of your file, import the GIFs
import slide1 from '../image/slide1.gif';
import slide2 from '../image/slide2.gif';
import slide3 from '../image/slide3.gif';
import slide4 from '../image/slide4.gif';
import slide5 from '../image/slide5.gif';

const Landing: React.FC = () => {
  const handleLogout = () => {
    console.log('Đăng xuất');
  };

  // State để quản lý slide hiện tại
  const [currentSlide, setCurrentSlide] = useState(0);
  // Add a new state to track if we're transitioning
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Dữ liệu cho các slide
  const slides = [
    {
      image: slide1,
      title: 'Cuộc họp của bạn được bảo vệ an toàn',
      description: 'Không ai có thể tham gia cuộc họp trừ phi người tổ chức mời hoặc cho phép.',
    },
    {
      image: slide2,
      title: 'Kết nối dễ dàng',
      description: 'Tham gia các cuộc họp trực tuyến chỉ với một cú nhấp chuột.',
    },
    {
      image: slide3,
      title: 'Tích hợp thông minh',
      description: 'Tích hợp với các công cụ làm việc phổ biến để tăng hiệu quả.',
    },
    {
      image: slide4,
      title: 'Trải nghiệm phỏng vấn thực tế',
      description: 'Luyện tập trước các câu hỏi phỏng vấn với môi trường mô phỏng AI.',
    },
    {
      image: slide5,
      title: 'Phân tích và đánh giá',
      description: 'Nhận phản hồi chi tiết về câu trả lời và biểu hiện của bạn sau mỗi buổi.',
    },
  ];

  // Hàm chuyển slide
  const goToNextSlide = () => {
    if (isTransitioning) return;
    
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
      setIsTransitioning(false);
    }, 500); // Match this with your animation duration
  };

  const goToPrevSlide = () => {
    if (isTransitioning) return;
    
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
      setIsTransitioning(false);
    }, 500);
  };

  return (
    <>
      {/* Nav chỉ dành riêng cho trang Landing */}
      <nav className="nav-landing">
        <div className="nav-container">
          {/* Move CoInter to the left */}
          <div className="text-left flex-1">
            <h1 className="nav-title">CoInter</h1>
          </div>

          {/* Nút Đăng Xuất */}
          <button
            onClick={handleLogout}
            className="flex items-center justify-center w-12 h-12 rounded-full text-gray-600 hover:bg-gray-200 hover:text-red-600"
          >
            <LogOut className="w-7 h-7" />
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-landing">
        <div className="grid-container">
          {/* Left Section (Now contains meeting creation) */}
          <section className="left-section">
            {/* Remove centering and add top alignment */}
            <div className="flex flex-col items-start w-full">
              <h2 className="left-title">Tính năng luyện tập phỏng vấn dành cho tất cả ứng viên</h2>
              <p className="left-subtitle">Tập luyện với AI, ghi điểm với HR cùng với CoInter</p>

              {/* Create horizontal layout container */}
              <div className="flex flex-wrap gap-4 items-center mt-4 w-full">
                {/* Meeting button - Now first (left) - with underline */}
                <div className="meeting-button-container">
                  <button className="right-button">
                    <Video className="w-6 h-6 mr-2 inline-block align-middle transform -translate-y-0.5" /> Cuộc họp mới
                  </button>
                  <div className="button-underline"></div>
                </div>
                
                {/* Resume Upload Section - Now second (right) */}
                <div className="resume-upload-container">    
                  <div className="resume-form">
                    <div className="input-container" onClick={() => document.getElementById('resume-file-input').click()}>
                      {/* File upload icon on the left */}
                      <label className="file-upload-label">
                        <span className="file-icon"><i className="fas fa-file-upload"></i></span>
                      </label>
                      
                      {/* Filename display instead of input */}
                      <div className="filename-display">
                        <span id="filename-text">Nhấp để chọn CV của bạn</span>
                      </div>
                      
                      {/* Hidden file input */}
                      <input 
                        type="file" 
                        id="resume-file-input"
                        className="file-input" 
                        accept=".pdf,.doc,.docx" 
                        onChange={(e) => {
                          const fileName = e.target.files?.[0]?.name || "Nhấp để chọn CV của bạn";
                          document.getElementById('filename-text').textContent = fileName;
                        }}
                      />
                    </div>
                    <button className="submit-button">Nộp ngay</button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Right Section (Now contains slider) */}
          <section className="right-section">
            <div className="slider">
              <button className="slider-button prev" onClick={goToPrevSlide}>
                &#8249;
              </button>
              <div className={`slider-content ${isTransitioning ? 'slide-exit' : ''}`}>
                <img 
                  src={slides[currentSlide].image} 
                  alt={slides[currentSlide].title} 
                  className="slider-image" 
                />
                <div className="slider-text-container">
                  <h2 className="slider-title">{slides[currentSlide].title}</h2>
                  <p className="slider-description">{slides[currentSlide].description}</p>
                </div>
              </div>
              <button className="slider-button next" onClick={goToNextSlide}>
                &#8250;
              </button>
            </div>
            <div className="slider-dots">
              {slides.map((_, index) => (
                <span
                  key={index}
                  className={`dot ${index === currentSlide ? 'active' : ''}`}
                  onClick={() => setCurrentSlide(index)}
                ></span>
              ))}
            </div>
          </section>
        </div>
      </main>
    </>
  );
};

export default Landing;