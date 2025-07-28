import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../Css/Meets.css';
import { setupDragAndDrop, setupFileValidation } from '../scripts/meetsScript';

const Meets: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [fileName, setFileName] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [companyName, setCompanyName] = useState<string>('');
  const [jobPosition, setJobPosition] = useState<string>('');
  const [companyField, setCompanyField] = useState<string>('');
  const [companyProducts, setCompanyProducts] = useState<string>('');
  const [companyCulture, setCompanyCulture] = useState<string>('');
  const [otherInfo, setOtherInfo] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [isAnimating, setIsAnimating] = useState<boolean>(false);
  const [animationDirection, setAnimationDirection] = useState<'next' | 'prev'>('next');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const uploadAreaRef = useRef<HTMLDivElement>(null);

  // Initialize drag and drop functionality
  useEffect(() => {
    if (currentStep === 1) {
      // Add Font Awesome if not already included
      if (!document.querySelector('[href*="font-awesome"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        document.head.appendChild(link);
      }
      
      // Small delay to ensure DOM is ready
      const timer = setTimeout(() => {
        setupDragAndDrop();
        setupFileValidation();
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [currentStep]);

  // Reset session when component mounts
  useEffect(() => {
    const resetSession = async () => {
      try {
        const response = await fetch('http://localhost:5000/reset_session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          console.log('Session reset successfully');
        }
      } catch (error) {
        console.error('Error resetting session:', error);
      }
    };
    
    resetSession();
  }, []);

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const fileSize = selectedFile.size / 1024 / 1024; // in MB
      const fileType = selectedFile.type;
      const validTypes = [
        'application/pdf', 
        'application/msword', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      
      // Validate file size
      if (fileSize > 5) {
        setError('File vượt quá kích thước cho phép (5MB)');
        return;
      }
      
      // Validate file type
      if (!validTypes.includes(fileType)) {
        setError('Định dạng file không hỗ trợ. Vui lòng sử dụng PDF, DOC hoặc DOCX');
        return;
      }
      
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError('');
    }
  };

  // Navigate to the next step with animation
  const goToNextStep = () => {
    if (isAnimating) return;
    
    setAnimationDirection('next');
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentStep(prev => prev + 1);
      setIsAnimating(false);
    }, 500);
  };

  // Navigate to the previous step with animation
  const goToPrevStep = () => {
    if (isAnimating) return;
    
    setAnimationDirection('prev');
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentStep(prev => prev - 1);
      setIsAnimating(false);
    }, 500);
  };

  // Handle resume submission
  const handleResumeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Vui lòng chọn file CV để tiếp tục');
      return;
    }
    
    setIsLoading(true);
    
    // Simulating API call with a timeout
    setTimeout(() => {
      setIsLoading(false);
      goToNextStep();
    }, 1500);
  };

  // Handle company info submission
  const handleCompanyInfoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!companyName || !jobPosition || !companyField) {
      setError('Vui lòng điền đầy đủ thông tin công ty và vị trí ứng tuyển');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      // Log dữ liệu sẽ được gửi để debug
      const companyData = {
        companyName,
        jobPosition,
        companyField,
        companyProducts,
        companyCulture,
        otherInfo
      };
      console.log('Sending company data to backend:', companyData);
      
      // Gửi thông tin công ty đến backend và cập nhật personality chatbot
      const response = await fetch('http://localhost:5000/update_company_info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(companyData),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        console.log('✅ Company information updated successfully:', data.company_info);
        console.log('✅ Chatbot personality updated for interview with:', companyName);
        
        // Gọi API để cập nhật personality chatbot
        try {
          const personalityResponse = await fetch('http://localhost:5000/update_personality_with_company_info', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
          });
          
          const personalityData = await personalityResponse.json();
          
          if (personalityResponse.ok && personalityData.success) {
            console.log('✅ Chatbot personality updated successfully via API');
          } else {
            console.warn('⚠️ Warning: Personality update failed, but continuing...');
          }
        } catch (personalityError) {
          console.error('❌ Error calling personality update API:', personalityError);
          // Không throw error để không block flow chính
        }
        
        // Thêm delay nhỏ để đảm bảo backend đã xử lý xong
        setTimeout(() => {
          goToNextStep();
        }, 500);
      } else {
        setError(data.error || 'Có lỗi xảy ra khi cập nhật thông tin công ty');
      }
    } catch (error) {
      console.error('❌ Error updating company info:', error);
      setError('Không thể kết nối đến server. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  };

  // Start the meeting
  const handleStartMeeting = () => {
    setIsLoading(true);
    
    // Navigate to meeting page after a short delay
    setTimeout(() => {
      navigate('/meet');
    }, 1000);
  };

  // Get animation classes based on direction and step state
  const getAnimationClasses = () => {
    if (isAnimating) {
      return 'fade-out';
    } else {
      return 'fade-in';
    }
  };

  // Render step 1: Resume upload (updated design)
  const renderResumeUpload = () => {
    return (
      <div className={`split-container ${getAnimationClasses()}`}>
        <div className="left-panel">
          <img src="/src/image/CV.gif" alt="Resume upload" className="cv-illustration" />
          
          <div className="social-links">
            <a href="#" className="social-link"><i className="fab fa-facebook-f"></i></a>
            <a href="#" className="social-link"><i className="fab fa-linkedin-in"></i></a>
            <a href="#" className="social-link"><i className="fab fa-instagram"></i></a>
          </div>
          
          <div className="copyright">
            ©FriendlyCOINTER
            <br />
            Tất cả quyền được bảo lưu
          </div>
        </div>
        
        <div className="right-panel">
          <div className="panel-header">
            {/* Logo text removed */}
          </div>
          
          <div className="form-container">
            <form onSubmit={handleResumeSubmit}>
              <div className="file-upload-container">
                <div 
                  className="file-upload-area new-design"
                  ref={uploadAreaRef}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className={`upload-illustration ${fileName ? 'has-file' : ''}`}>
                    <div className="upload-icon-container">
                      <div className="document-icons">
                        <i className="fa fa-file-alt"></i>
                        <i className="fa fa-file-image"></i>
                        <i className="fa fa-file-pdf"></i>
                      </div>
                    </div>
                    <h2 className="drag-drop-title">Tải <span className="highlight">CV</span> của bạn tại đây</h2>
                    <div className="drag-drop-subtitle">để chúng tôi  <span className="browse-text">phân tích</span> và chuẩn bị phỏng vấn cho bạn tốt nhất</div>
                    
                    {fileName && (
                      <div className="selected-file">
                        <i className="fa fa-file-alt file-icon"></i>
                        <span className="file-name" title={fileName}>{fileName}</span>
                      </div>
                    )}
                  </div>
                  
                  <input 
                    type="file" 
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx"
                    className="file-input"
                  />
                </div>
              </div>
              
              {error && <div className="error-message">{error}</div>}
              
              <div className="form-buttons step-1-buttons">
                <button 
                  type="submit" 
                  className="primary-button upload-button"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="loading-spinner">
                      <i className="fas fa-spinner fa-spin"></i> Đang xử lý...
                    </span>
                  ) : (
                    <span>Tiếp tục</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // Render step 2: Company information with two-column layout
  const renderCompanyInfo = () => {
    return (
      <div className={`split-container ${getAnimationClasses()}`}>
        <div className="left-panel company-info-panel">
          <img src="/src/image/infos.gif" alt="Company information" className="info-illustration" />
          
          <div className="social-links">
            <a href="#" className="social-link"><i className="fab fa-facebook-f"></i></a>
            <a href="#" className="social-link"><i className="fab fa-linkedin-in"></i></a>
            <a href="#" className="social-link"><i className="fab fa-instagram"></i></a>
          </div>
          
          <div className="copyright">
            ©FriendlyCOINTER
            <br />
            Tất cả quyền được bảo lưu
          </div>
        </div>
        
        <div className="right-panel needs-scroll">
          <div className="panel-header">
            {/* Logo text removed */}
          </div>
          
          <div className="form-container">
            <form onSubmit={handleCompanyInfoSubmit}>
              <h2 className="form-section-title">Thông tin về công ty</h2>
              
              <div className="form-group">
                <label htmlFor="companyName">Tên công ty <span className="required">*</span></label>
                <input
                  type="text"
                  id="companyName"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="Ví dụ: Công ty ABC"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="companyField">Lĩnh vực của công ty <span className="required">*</span></label>
                <input
                  type="text"
                  id="companyField"
                  value={companyField}
                  onChange={(e) => setCompanyField(e.target.value)}
                  placeholder="Ví dụ: Công nghệ thông tin"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="companyProducts">Sản phẩm của công ty</label>
                <input
                  type="text"
                  id="companyProducts"
                  value={companyProducts}
                  onChange={(e) => setCompanyProducts(e.target.value)}
                  placeholder="Ví dụ: Ứng dụng di động, Website"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="companyCulture">Văn hóa công ty</label>
                <input
                  type="text"
                  id="companyCulture"
                  value={companyCulture}
                  onChange={(e) => setCompanyCulture(e.target.value)}
                  placeholder="Ví dụ: Đổi mới, sáng tạo, làm việc nhóm"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="jobPosition">Ngành nghề ứng tuyển <span className="required">*</span></label>
                <input
                  type="text"
                  id="jobPosition"
                  value={jobPosition}
                  onChange={(e) => setJobPosition(e.target.value)}
                  placeholder="Ví dụ: Frontend Developer"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="otherInfo">Thông tin khác</label>
                <input
                  type="text"
                  id="otherInfo"
                  value={otherInfo}
                  onChange={(e) => setOtherInfo(e.target.value)}
                  placeholder="Thông tin bổ sung về công ty"
                />
              </div>
              
              {error && <div className="error-message">{error}</div>}
              
              <div className="form-buttons">
                <button 
                  type="button" 
                  className="back-button"
                  onClick={() => {
                    setError('');
                    goToPrevStep();
                  }}
                  disabled={isLoading}
                >
                  Quay lại
                </button>
                <button 
                  type="submit" 
                  className="primary-button"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="loading-spinner">
                      <i className="fas fa-spinner fa-spin"></i> Đang xử lý...
                    </span>
                  ) : (
                    <span>Tiếp tục</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // Render step 3: Start meeting with split-panel layout
  const renderStartMeeting = () => {
    return (
      <div className={`split-container ${getAnimationClasses()}`}>
        <div className="left-panel start-meeting-panel">
          <img src="/src/image/startmeet.gif" alt="Start Meeting" className="startmeet-illustration" />
          
          <div className="social-links">
            <a href="#" className="social-link"><i className="fab fa-facebook-f"></i></a>
            <a href="#" className="social-link"><i className="fab fa-linkedin-in"></i></a>
            <a href="#" className="social-link"><i className="fab fa-instagram"></i></a>
          </div>
          
          <div className="copyright">
            ©FriendlyCOINTER
            <br />
            Tất cả quyền được bảo lưu
          </div>
        </div>
        
        <div className="right-panel needs-scroll">
          <div className="panel-header">
            {/* Logo text removed */}
          </div>
          
          <div className="form-container">
            <h2 className="form-section-title">Sẵn sàng để bắt đầu</h2>
            <p className="step-description reduced-margin">
              Chúng tôi đã chuẩn bị sẵn sàng cho buổi phỏng vấn của bạn với {companyName} cho vị trí {jobPosition}
            </p>
            
            <div className="meeting-info">
              <div className="info-item">
                <i className="info-icon fa fa-file-alt"></i>
                <div className="info-content">
                  <h3>CV đã tải lên</h3>
                  <p>{fileName}</p>
                </div>
              </div>
              
              <div className="info-item">
                <i className="info-icon fa fa-building"></i>
                <div className="info-content">
                  <h3>Thông tin công ty</h3>
                  <p>
                    <strong>Tên công ty:</strong> {companyName}<br />
                    <strong>Lĩnh vực:</strong> {companyField}<br />
                    <strong>Vị trí ứng tuyển:</strong> {jobPosition}
                    {companyCulture && (
                      <><br /><strong>Văn hóa công ty:</strong> {companyCulture}</>
                    )}
                    {otherInfo && (
                      <><br /><strong>Thông tin khác:</strong> {otherInfo}</>
                    )}
                  </p>
                </div>
              </div>
              
              <div className="info-item">
                <i className="info-icon fa fa-info-circle"></i>
                <div className="info-content">
                  <h3>Buổi phỏng vấn</h3>
                  <p>Thời gian: 30-45 phút<br/>Hình thức: Trực tuyến</p>
                </div>
              </div>
            </div>
            
            <div className="meeting-tips">
              <h3>Lưu ý trước khi bắt đầu:</h3>
              <ul>
                <li>Đảm bảo kết nối internet ổn định</li>
                <li>Kiểm tra camera và microphone hoạt động tốt</li>
                <li>Chọn không gian yên tĩnh, ánh sáng tốt</li>
                <li>Chuẩn bị giấy bút để ghi chép nếu cần</li>
              </ul>
            </div>
            
            <div className="start-meeting-buttons">
              <button 
                type="button" 
                className="back-button"
                onClick={() => {
                  setError('');
                  goToPrevStep();
                }}
                disabled={isLoading}
              >
                Quay lại
              </button>
              <button 
                type="button" 
                className="start-button"
                onClick={handleStartMeeting}
                disabled={isLoading}
              >
                {isLoading ? 'Đang khởi tạo...' : 'Bắt đầu phỏng vấn'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Render the current step with animation
  const renderCurrentStep = () => {
    // Only apply the entrance animation when not animating (after previous animation completes)
    if (!isAnimating) {
      switch (currentStep) {
        case 1:
          return <div className="fade-in">{renderResumeUpload()}</div>;
        case 2:
          return <div className="fade-in">{renderCompanyInfo()}</div>;
        case 3:
          return <div className="fade-in">{renderStartMeeting()}</div>;
        default:
          return null;
      }
    }
    
    // During animation, show the current step with exit animation
    switch (currentStep) {
      case 1:
        return <div className="fade-out">{renderResumeUpload()}</div>;
      case 2:
        return <div className="fade-out">{renderCompanyInfo()}</div>;
      case 3:
        return <div className="fade-out">{renderStartMeeting()}</div>;
      default:
        return null;
    }
  };

  // Render the main component based on current step
  return (
    <div className="meets-container">
      <div className={`meets-content ${currentStep === 3 ? 'full-page' : ''}`}>
        <div className="step-transition-container">
          {renderCurrentStep()}
        </div>
      </div>
    </div>
  );
};

export default Meets;