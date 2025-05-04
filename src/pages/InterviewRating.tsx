import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../Css/InterviewRating.css';

const InterviewRating: React.FC = () => {
  const navigate = useNavigate();
  const [rating, setRating] = useState<number>(0);
  const [feedbackText, setFeedbackText] = useState<string>('');
  const [aspectRatings, setAspectRatings] = useState({
    clarity: 0,
    relevance: 0,
    difficulty: 0,
    interviewer: 0
  });
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitSuccess, setSubmitSuccess] = useState<boolean>(false);

  // Handler for aspect rating changes
  const handleAspectRatingChange = (aspect: string, value: number) => {
    setAspectRatings(prev => ({
      ...prev,
      [aspect]: value
    }));
  };

  // Handler for overall rating changes
  const handleRatingChange = (value: number) => {
    setRating(value);
  };

  // Handler for feedback text changes
  const handleFeedbackChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFeedbackText(e.target.value);
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Here you would typically send the data to your backend
      console.log({
        overallRating: rating,
        aspectRatings,
        feedback: feedbackText
      });
      
      // Simulate API call with timeout
      setTimeout(() => {
        setSubmitSuccess(true);
        setIsSubmitting(false);
        
        // Navigate back to landing page after showing success message
        setTimeout(() => {
          navigate('/');
        }, 2000);
      }, 1500);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setIsSubmitting(false);
    }
  };

  // Rating stars component for reuse
  const RatingStars = ({ 
    currentRating, 
    onChange, 
    name 
  }: { 
    currentRating: number, 
    onChange: (value: number) => void, 
    name: string 
  }) => {
    return (
      <div className="rating-stars">
        {[1, 2, 3, 4, 5].map(value => (
          <span 
            key={`${name}-${value}`}
            className={`star ${value <= currentRating ? 'active' : ''}`}
            onClick={() => onChange(value)}
          >
            <i className="fas fa-star"></i>
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="interview-rating-container">
      <div className="rating-content">
        <h1 className="rating-title">Đánh giá buổi phỏng vấn</h1>
        
        {submitSuccess ? (
          <div className="success-message">
            <i className="fas fa-check-circle"></i>
            <p>Cảm ơn bạn đã đánh giá! Phản hồi của bạn đã được ghi nhận.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="rating-form">
            <div className="rating-section">
              <h2>Đánh giá tổng thể</h2>
              <p className="rating-description">Bạn đánh giá thế nào về buổi phỏng vấn này?</p>
              <div className="overall-rating">
                <RatingStars 
                  currentRating={rating} 
                  onChange={handleRatingChange}
                  name="overall" 
                />
                <span className="rating-label">
                  {rating > 0 ? (
                    rating >= 4 ? 'Rất hài lòng' : 
                    rating >= 3 ? 'Hài lòng' : 
                    rating >= 2 ? 'Bình thường' : 'Chưa hài lòng'
                  ) : ''}
                </span>
              </div>
            </div>

            <div className="rating-section">
              <h2>Đánh giá chi tiết</h2>
              
              <div className="aspect-rating">
                <div className="aspect-label">Độ rõ ràng của câu hỏi</div>
                <RatingStars 
                  currentRating={aspectRatings.clarity} 
                  onChange={(value) => handleAspectRatingChange('clarity', value)}
                  name="clarity" 
                />
              </div>
              
              <div className="aspect-rating">
                <div className="aspect-label">Độ liên quan đến vị trí ứng tuyển</div>
                <RatingStars 
                  currentRating={aspectRatings.relevance} 
                  onChange={(value) => handleAspectRatingChange('relevance', value)}
                  name="relevance" 
                />
              </div>
              
              <div className="aspect-rating">
                <div className="aspect-label">Độ khó của câu hỏi</div>
                <RatingStars 
                  currentRating={aspectRatings.difficulty} 
                  onChange={(value) => handleAspectRatingChange('difficulty', value)}
                  name="difficulty" 
                />
              </div>
              
              <div className="aspect-rating">
                <div className="aspect-label">Thái độ của người phỏng vấn</div>
                <RatingStars 
                  currentRating={aspectRatings.interviewer} 
                  onChange={(value) => handleAspectRatingChange('interviewer', value)}
                  name="interviewer" 
                />
              </div>
            </div>

            <div className="rating-section">
              <h2>Góp ý của bạn</h2>
              <p className="rating-description">Bạn có góp ý gì để chúng tôi cải thiện hệ thống phỏng vấn?</p>
              <textarea
                className="feedback-text"
                placeholder="Nhập góp ý của bạn ở đây..."
                value={feedbackText}
                onChange={handleFeedbackChange}
                rows={4}
              />
            </div>

            <div className="rating-actions">
              <button 
                type="submit" 
                className="submit-button" 
                disabled={isSubmitting || rating === 0}
              >
                {isSubmitting ? 'Đang gửi...' : 'Gửi đánh giá'}
              </button>
              <button 
                type="button" 
                className="skip-button"
                onClick={() => navigate('/')}
              >
                Bỏ qua
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default InterviewRating;