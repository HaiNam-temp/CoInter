# Dynamic Company Information Feature

## Overview
Tính năng này cho phép lấy thông tin công ty động từ người dùng trong form Meets và sử dụng thông tin đó để cá nhân hóa cuộc phỏng vấn AI.

## Flow Process

### 1. User Flow (Frontend - Meets.tsx)
```
Step 1: Upload CV
  ↓
Step 2: Enter Company Information
  - Tên công ty
  - Vị trí ứng tuyển  
  - Lĩnh vực công ty
  - Sản phẩm công ty
  - Văn hóa công ty
  - Thông tin khác
  ↓
Step 3: Start Interview
```

### 2. Backend Process (app.py)
```
1. Session Reset
   - Reset company_information dict
   - Reset messages array with default personality

2. Update Company Info (/update_company_info)
   - Receive company data from frontend
   - Update global company_information dict
   - Call update_personality_with_company_info()
   - Update system prompt with company context

3. Generate Interview Questions
   - Use updated system prompt with company context
   - Create personalized questions based on company info
```

## Key Functions

### Backend (app.py)
- `company_information`: Global dict to store company data
- `update_company_info()`: API endpoint to receive company data
- `update_personality_with_company_info()`: Updates system prompt with company context
- `generate_text()`: Generates AI responses using updated context

### Frontend (Meets.tsx)
- `handleCompanyInfoSubmit()`: Sends company data to backend
- Company form fields: companyName, jobPosition, companyField, etc.

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/update_company_info` | POST | Update company information |
| `/reset_session` | POST | Reset session and company info |
| `/get_company_info` | GET | Get current company info (debug) |
| `/get_system_prompt` | GET | Get current system prompt (debug) |

## Testing

Run the test script to verify the flow:
```bash
python test_company_flow.py
```

## Example Company Context in System Prompt

When company information is provided, the system prompt will include:
```
**Current Company Information (provided by candidate):**
- Company Name: TechCorp AI Solutions
- Job Position: Senior AI Engineer
- Company Field: Artificial Intelligence & Machine Learning
- Company Products: AI-powered educational platforms
- Company Culture: Innovation-focused, collaborative
- Other Information: Series B startup with 200+ employees

**Important:** Use this company information to create relevant, personalized interview questions specific to this company and position.
```

## Benefits

1. **Personalized Questions**: AI generates questions specific to the company and role
2. **Relevant Context**: Questions match company culture and products
3. **Better Experience**: More realistic interview simulation
4. **Dynamic Content**: No more hardcoded company information

## Technical Notes

- Uses global variables (suitable for single-user demo)
- Company information persists throughout interview session
- System prompt is dynamically updated when company info changes
- All company fields are optional except name, position, and field
