/**
 * Meets page scripts for enhanced functionality
 */

// Set up drag and drop file upload
function setupDragAndDrop() {
  const uploadArea = document.querySelector('.file-upload-area');
  const fileInput = document.querySelector('.file-input');
  
  if (!uploadArea || !fileInput) return;
  
  // Prevent default browser behavior
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
  });
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  // Add visual feedback
  ['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, highlight, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, unhighlight, false);
  });
  
  function highlight() {
    uploadArea.classList.add('highlight');
  }
  
  function unhighlight() {
    uploadArea.classList.remove('highlight');
  }
  
  // Handle the file drop
  uploadArea.addEventListener('drop', handleDrop, false);
  
  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length) {
      fileInput.files = files;
      // Trigger change event
      const event = new Event('change', { bubbles: true });
      fileInput.dispatchEvent(event);
    }
  }
}

// Form validation for company information
function setupFormValidation() {
  const companyForm = document.querySelector('.company-form');
  const companyName = document.getElementById('companyName');
  const jobPosition = document.getElementById('jobPosition');
  
  if (!companyForm || !companyName || !jobPosition) return;
  
  function validateForm() {
    let isValid = true;
    
    // Check company name
    if (!companyName.value.trim()) {
      showError(companyName, 'Vui lòng nhập tên công ty');
      isValid = false;
    } else {
      removeError(companyName);
    }
    
    // Check job position
    if (!jobPosition.value.trim()) {
      showError(jobPosition, 'Vui lòng nhập vị trí ứng tuyển');
      isValid = false;
    } else {
      removeError(jobPosition);
    }
    
    return isValid;
  }
  
  function showError(input, message) {
    const formGroup = input.closest('.form-group');
    let errorElement = formGroup.querySelector('.validation-error');
    
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.className = 'validation-error error-message';
      formGroup.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    input.classList.add('error-input');
  }
  
  function removeError(input) {
    const formGroup = input.closest('.form-group');
    const errorElement = formGroup.querySelector('.validation-error');
    
    if (errorElement) {
      errorElement.remove();
    }
    
    input.classList.remove('error-input');
  }
  
  // Add input event listeners
  companyName.addEventListener('input', () => {
    if (companyName.value.trim()) {
      removeError(companyName);
    }
  });
  
  jobPosition.addEventListener('input', () => {
    if (jobPosition.value.trim()) {
      removeError(jobPosition);
    }
  });
  
  // Submit form validation
  companyForm.addEventListener('submit', function(e) {
    if (!validateForm()) {
      e.preventDefault();
    }
  });
}

// Validate file size and type
function setupFileValidation() {
  const fileInput = document.querySelector('.file-input');
  if (!fileInput) return;
  
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const fileSize = file.size / 1024 / 1024; // in MB
    const fileType = file.type;
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    // Check size
    if (fileSize > 5) {
      showFileError('File vượt quá kích thước cho phép (5MB)');
      fileInput.value = '';
      return;
    }
    
    // Check type
    if (!validTypes.includes(fileType)) {
      showFileError('Định dạng file không hỗ trợ. Vui lòng sử dụng PDF, DOC hoặc DOCX');
      fileInput.value = '';
      return;
    }
    
    // Clear error if all good
    clearFileError();
  });
  
  function showFileError(message) {
    const container = document.querySelector('.file-upload-container');
    clearFileError();
    
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message file-error';
    errorElement.textContent = message;
    container.appendChild(errorElement);
  }
  
  function clearFileError() {
    const errorElement = document.querySelector('.file-error');
    if (errorElement) {
      errorElement.remove();
    }
  }
}

// Progress bar animation
function setupProgressBar() {
  const progressFill = document.querySelector('.progress-line-fill');
  const steps = document.querySelectorAll('.progress-step');
  
  if (!progressFill || !steps.length) return;
  
  // This would normally be controlled by your React component
  // This is just for demonstration of animation
  
  function animateProgress(step) {
    const width = (step - 1) * (100 / (steps.length - 1));
    
    progressFill.style.width = '0%';
    setTimeout(() => {
      progressFill.style.width = `${width}%`;
    }, 100);
    
    steps.forEach((stepEl, index) => {
      if (index + 1 <= step) {
        stepEl.classList.add('active');
      } else {
        stepEl.classList.remove('active');
      }
    });
  }
  
  // Example usage (would be controlled by your React component)
  // animateProgress(2); // Move to step 2
}

// Initialize all scripts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  setupDragAndDrop();
  setupFormValidation();
  setupFileValidation();
  setupProgressBar();
  
  // Add CSS class for Font Awesome if it's not already included
  if (!document.querySelector('[href*="font-awesome"]')) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
    document.head.appendChild(link);
  }
});

// Export functions for direct use in React components
export {
  setupDragAndDrop,
  setupFormValidation,
  setupFileValidation,
  setupProgressBar
};