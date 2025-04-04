import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Home, Tv, LogOut } from 'lucide-react';
import '../Css/Landing.css';

const Landing: React.FC = () => {
  const handleLogout = () => {
    console.log('Đăng xuất');
  };

  // State để quản lý slide hiện tại
  const [currentSlide, setCurrentSlide] = useState(0);

  // Dữ liệu cho các slide
  const slides = [
    {
      image: '', // Thay bằng đường dẫn thực tế
      title: 'Cuộc họp của bạn được bảo vệ an toàn',
      description: 'Không ai có thể tham gia cuộc họp trừ phi người tổ chức mời hoặc cho phép.',
    },
    {
      image: '', // Thay bằng đường dẫn thực tế
      title: 'Kết nối dễ dàng',
      description: 'Tham gia các cuộc họp trực tuyến chỉ với một cú nhấp chuột.',
    },
    {
      image: '', // Thay bằng đường dẫn thực tế
      title: 'Tích hợp thông minh',
      description: 'Tích hợp với các công cụ làm việc phổ biến để tăng hiệu quả.',
    },
  ];

  // Hàm chuyển slide
  const goToNextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const goToPrevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  return (
    <>
      {/* Nav chỉ dành riêng cho trang Landing */}
      <nav className="nav-landing">
        <div className="nav-container">
          {/* Chữ CoInter ở giữa */}
          <div className="text-center">
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
          {/* Left Section: Slider */}
          <section className="left-section">
            <div className="slider">
              <button className="slider-button prev" onClick={goToPrevSlide}>
                &#8249;
              </button>
              <div className="slider-content">
                <img src={slides[currentSlide].image} alt={slides[currentSlide].title} className="slider-image" />
                <h2 className="slider-title">{slides[currentSlide].title}</h2>
                <p className="slider-description">{slides[currentSlide].description}</p>
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

          {/* Right Section */}
          <section className="right-section">
            <h2 className="right-title">Bắt đầu một cuộc họp mới</h2>
            <div className="flex flex-col md:flex-row items-center justify-center gap-4 w-full">
              <button className="right-button">Cuộc họp mới</button>
            </div>
          </section>
        </div>
      </main>
    </>
  );
};

export default Landing;