# app.py
import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError # Thêm các loại lỗi cụ thể
from flask import Flask, render_template, request, jsonify, send_file, abort, Response
from flask_cors import CORS
from pydub import AudioSegment  # Thêm thư viện này để chuyển đổi định dạng âm thanh
from pydub.utils import which
import fitz  # PyMuPDF for PDF text extraction
import json
import os
import whisper  # Thêm thư viện whisper local
import time  # Thêm để sử dụng trong streaming
import torch  # Thêm để kiểm tra GPU
from TTS.api import TTS  # Thêm Coqui TTS

AudioSegment.converter = which("ffmpeg")  # Đảm bảo `pydub` sử dụng đúng `ffmpeg`

# --- Khởi tạo Whisper Model ---
# Load model một lần khi khởi động ứng dụng để tránh delay
try:
    whisper_model = whisper.load_model("base")  # Có thể dùng "small", "medium", "large" cho độ chính xác cao hơn
    print("Whisper model loaded successfully")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    whisper_model = None

# --- Khởi tạo Coqui TTS Model ---
# Load TTS model một lần khi khởi động ứng dụng
try:
    # Get device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device for TTS: {device}")
    
    # Initialize TTS với model nhanh hơn cho tiếng Anh
    # Sử dụng model FastSpeech2 cho độ trễ thấp hơn
    try:
        tts_model = TTS("tts_models/en/ljspeech/fast_pitch").to(device)
        print("Coqui TTS FastPitch model loaded successfully")
    except:
        # Fallback về model tacotron2 nếu FastPitch không có
        tts_model = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
        print("Coqui TTS Tacotron2 model loaded successfully")
except Exception as e:
    print(f"Error loading Coqui TTS model: {e}")
    tts_model = None

app = Flask(__name__)

# Simple CORS configuration
CORS(app, origins=["http://localhost:5173", "https://localhost:5173"], supports_credentials=True, 
     expose_headers=['X-Transcript', 'X-AI-Response', 'X-Model-Used', 'X-Response-Text', 'X-Company-Name', 'X-Job-Position'])

load_dotenv()
api_key = os.getenv("OPEN_AI_KEY")
# --- Khởi Tạo Flask App ---
# Sử dụng thư mục templates và static mặc định


# --- Khởi Tạo OpenAI Client ---
client = OpenAI(api_key="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")

# --- Dữ Liệu CV và Job Details ---
company_information = {
    "company_name": "",
    "job_position": "",
    "company_field": "",
    "company_products": "",
    "company_culture": "",
    "other_info": ""
}
# !!! Trong ứng dụng thực tế, dữ liệu này nên được lấy từ DB hoặc nguồn khác
cv = """[
  {
    "thoi_gian": "T1/2024 - Hiện tại",
    "du_an": "Nghiên cứu và phát triển sản phẩm – PTIT Lab",
    "mo_ta": [
      "Xây dựng mô hình phát hiện bệnh u não qua ảnh chụp cắt lớp MRI:",
      "Trích xuất dữ liệu của bệnh nhân từ file DICOM",
      "Tiền xử lý dữ liệu, gán nhãn và transform dữ liệu",
      "Xây dựng mô hình object detection khối u sử dụng Faster R-CNN",
      "Nghiên cứu kiến trúc KAN và áp dụng vào mạng UNET cho bài toán phân đoạn:",
      "Phân tích đánh giá kiến trúc KAN so với kiến trúc MLP đang phổ biến hiện nay",
      "Xây dựng mô hình và kiểm thử trên với BUSI dataset và MRI dataset."
    ]
  },
  {
    "thoi_gian": "T9 - T11/2024", # Lưu ý: Tháng 11/2024 trong tương lai? Có thể là 2023?
    "du_an": "Thành viên đội thi - AI Contest 2024 (Game Tetris)",
    "mo_ta": [
      "Xây dựng mô hình CNN trích xuất đặc trưng của trò chơi.",
      "Sử dụng thuật toán DeepQLearning trong Reinforment Learning xây dựng Agent."
    ]
  },
  {
    "du_an": "Một số dự án Kaggle tự học (có GitHub)",
    "mo_ta": [
      "Wheat Detection: Bài toán xác định hình ảnh hạt lúa mì.",
      "Lyft 3D Object Detection for Autonomous: Bài toán phát hiện ô tô trên đường cho xe tự lái.",
      "Quora Insincere Questions: Phát nội dung toxic trong các cuộc hội thoại.",
      "Ultrasound Nerve Segmentation: Xác định cấu trúc thần kinh trong hình ảnh siêu âm cổ."
    ]
  }
]"""
job_details = """{
  "company_context": {
    "growth_stage_focus": "During the Growth Stage, focusing on building AI solutions is crucial due to:",
    "reasons": [
      "Enhanced competitiveness",
      "Improved learning experiences",
      "Optimized work processes",
      "Advanced data analysis",
      "Continuous innovation"
    ],
    "hiring_need": "Therefore, Step Up requires individuals with AI expertise and the ability to apply it to real-world problems to build and deploy AI solutions, aiding the company's strong growth during this phase."
  },
  "role_description": {
    "title": "AI-Powered Educational Solutions",
    "tasks": [
      "Develop an AI module for scoring IELTS Speaking assessments.",
      "Create an AI system for analyzing and evaluating user pronunciation in speaking lessons.",
      "Build an AI chatbot capable of answering frequently asked questions about English grammar.",
      "Design a personalized learning path recommendation system based on user performance and goals.",
      "Develop an AI tool to analyze and provide improvement suggestions for IELTS Writing assessments.",
      "Create an AI tool for automatically generating reading comprehension exercises tailored to user interests and proficiency.",
      "Design an AI system to analyze and evaluate English communication skills through simulated video calls."
    ],
    "title_operation_optimization":"AI Applications for Company Operational Optimization",
    "tasks_operation":[
      "Design and develop an AI-Agent and AI-Workflow system to enhance employee productivity.",
      "Optimize customer interaction activities to boost sales team efficiency and customer satisfaction."
    ]
  },
  "candidate_requirements": {
    "work_hours": "8:30 AM - 6:00 PM, 1.5-hour lunch break, Monday to Friday.",
    "experience": "Minimum 2-3 years of experience as an AI Engineer or Machine Learning Engineer, with a track record of developing and deploying AI projects in a production environment.",
    "key_skills_and_experience": {
      "ai_ml_expertise": "Proficiency in foundational machine learning models, deep understanding of current LLMs, and ability to fine-tune and optimize them.",
      "ai_solution_design": "Experience designing AI solutions for real-world problems and translating product requirements into feasible AI solutions.",
      "production_deployment": "Experience building and deploying AI systems at production scale, proficiency in MLOps, ability to optimize performance (high-throughput, low-latency), and experience with cloud platforms.",
      "soft_skills": {
        "problem_solving": "Strong problem-solving skills, capable of providing accurate and optimized solutions.",
        "critical_thinking": "Effective critical thinking and strong advocacy for accuracy.",
        "communication": "Ability to communicate complex technical ideas to non-technical stakeholders, including teachers and learning content developers.",
        "continuous_learning": "Ability to stay updated on the latest trends in AI and EdTech and apply them to product improvement."
      },
      "ethics": "Commitment to user data security and adherence to privacy regulations in education."
    },
    "company_culture": "Step Up offers an opportunity to shape the future of society and oneself. During our growth phase, we need hands to tackle increasing challenges. We believe in rewarding those who solve difficult problems. Welcome to Step Up! :D"
  }
}"""

# --- Định Nghĩa "Tính Cách" Chatbot ---
def get_personality():
    return f"""
  You are a chatbot acting as a professional interviewer for a company.
  **Context:**
You are interviewing a candidate for the position of "{company_information.get('job_position', 'a role')}" at {company_information.get('company_name', 'this company')}.

**Company Details (provided by candidate):**
- Company Name: {company_information.get('company_name', 'Not specified')}
- Job Position: {company_information.get('job_position', 'Not specified')}
- Company Field: {company_information.get('company_field', 'Not specified')}
- Company Products/Services: {company_information.get('company_products', 'Not specified')}
- Company Culture: {company_information.get('company_culture', 'Not specified')}
- Additional Information: {company_information.get('other_info', 'Not specified')}

**Important Personality Rule**: After receiving each user response, you must:
1. Implicitly score the answer internally (never reveal numerical scores during rounds 1-3)
2. Generate smooth connecting commentary and evaluation
3. Provide constructive feedback that relates to the role requirements
4. Ask the next question in sequence according to the defined round structure
5. Maintain natural conversation flow while strictly following the question count per round

**Interview Structure:**
**Interview Process (STRICTLY follow this structure):**

1.  **Round 1: Personal Introduction (EXACTLY 2 questions)**
    * Begin with a warm, personalized introduction focusing on the {company_information.get('job_position', 'position')} role at the {company_information.get('company_name', 'company')}.
    * Ask EXACTLY 2 questions covering these key areas:
        - Personal introduction and background (encourage them to share about themselves)
        - Understanding of their strengths and areas for growth
    **After each answer**: 
        - Provide encouraging, specific feedback that connects their responses to the role
        - Implicitly score the answer internally (do not reveal scores to candidate)
        - Generate smooth transition commentary and evaluation
    **Analysis Process**: Evaluate how their introduction and self-assessment relate to the {company_information.get('job_position', 'job position')} requirements.
    **Transition Rule**: After EXACTLY 2 questions and responses, naturally transition to Round 2 with connecting commentary.


2.  **Round 2: Professional Knowledge & Company Fit (3 questions)**
    * Ask exactly 3 questions about professional knowledge specifically related to:
        - {company_information.get('company_field', 'the industry')} industry
        - Skills needed for {company_information.get('job_position', 'this position')}
        - Experience with {company_information.get('company_products', 'relevant products/services')}
    * Test depth of understanding and evaluate how their skills match {company_information.get('company_name', 'the company')}'s needs.
    * Provide feedback and advice for improvement after each answer.
    * After 3 questions, move to Round 3.

3.  **Round 3: Project Experience & Technical Deep Dive (4 questions)**
    * Ask exactly 4 questions about projects and technical experience relevant to {company_information.get('company_field', 'this field')}.
    * Focus on how their experience applies to {company_information.get('job_position', 'this position')}.
    * Ask specific questions about:
        - Technical expertise relevant to {company_information.get('company_products', 'the company\'s products')}
        - Problem-solving approaches that would work at {company_information.get('company_name', 'this company')}
        - Team collaboration and project management experience
        - Challenges faced and solutions implemented in previous projects
    * Provide detailed feedback and suggestions after each answer.
    * After 4 questions, move to Round 4.

4.  **Round 4: Summary & Scoring**
    * Provide an implicit summary by naturally discussing the candidate's overall performance and fit for {company_information.get('job_position', 'the position')} at {company_information.get('company_name', 'the company')}.
    * Give only a single overall score: **SCORE: X/10**
    * Briefly mention key strengths and areas for improvement.
    * Thank them for applying and inform about next steps.

**Requirements:**
* STRICTLY follow the question count for each round (2-3-4 questions).
* Always reference {company_information.get('company_name', 'the company')} and {company_information.get('job_position', 'the position')} in your questions.
* Tailor ALL technical questions to {company_information.get('company_field', 'the industry')}.
* Evaluate cultural fit based on: {company_information.get('company_culture', 'the stated company culture')}.
* Keep track of question count and announce when moving to next round.
* Maintain a professional, friendly tone throughout.
* Provide constructive feedback after each answer.
* At the end, give a single overall score out of 10.

  **Additional Information:**

  * Candidate CV: {cv}

  Note: Additional company-specific information may be provided during the interview process to create more personalized questions.

  Please begin the interview with a greeting and start Round 1 with the first personal introduction question!
"""

# --- Lịch Sử Hội Thoại ---
# !!! Cảnh báo: Biến global, không phù hợp cho nhiều người dùng đồng thời.
messages = [{"role": "system", "content": get_personality()}]
# --- Hàm Lưu/Tải Lịch Sử Chat (Tùy chọn sử dụng) ---
HISTORY_FILE = "history.json"

def save_history_to_json(history, file_path=HISTORY_FILE):
    """Lưu lịch sử chat vào file JSON."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving chat history to {file_path}: {e}")
    except TypeError as e:
        print(f"Error serializing chat history to JSON: {e}")

def load_history_from_json(file_path=HISTORY_FILE):
    """Tải lịch sử chat từ file JSON."""
    try:
        if Path(file_path).is_file():
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            print(f"History file {file_path} not found. Starting new history.")
            return [] # Trả về list rỗng nếu file không tồn tại
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading chat history from {file_path}: {e}. Starting new history.")
        return [] # Trả về list rỗng nếu có lỗi

# --- Hàm Helper ---

def process_speech_to_text(audio_file_path):
    """Chuyển đổi file audio thành text sử dụng Whisper local hoặc OpenAI API."""
    try:
        if whisper_model is None:
            print("Whisper model not loaded, falling back to OpenAI API")
            # Fallback về OpenAI API nếu model local không load được
            with open(audio_file_path, "rb") as audio_data:
                transcript_response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_data
                )
            transcript = transcript_response.text
        else:
            # Sử dụng Whisper local
            print("Using local Whisper model for transcription")
            result = whisper_model.transcribe(str(audio_file_path))
            transcript = result["text"]
        
        print(f"Transcription successful: {transcript}")
        return transcript
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise Exception("Failed to transcribe audio")

def generate_audio(text, filename="speech_output.mp3"):
    """Chuyển text thành audio (Text-to-Speech) sử dụng local TTS model hoặc OpenAI API."""
    speech_file_path = Path(__file__).parent / filename
    
    try:
        if tts_model is None:
            print("Coqui TTS model not loaded, falling back to OpenAI API")
            # Fallback về OpenAI API nếu model local không load được
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova", # Bạn có thể thử các giọng khác: alloy, echo, fable, onyx, shimmer
                input=text
            )
            response.stream_to_file(speech_file_path)
            print(f"Audio generated using OpenAI TTS: {speech_file_path}")
        else:
            # Sử dụng Coqui TTS local
            print("Using local Coqui TTS model for audio generation")
            
            # Đảm bảo file extension phù hợp với Coqui TTS (thường là .wav)
            if not str(speech_file_path).endswith('.wav') and not str(speech_file_path).endswith('.mp3'):
                speech_file_path = speech_file_path.with_suffix('.wav')
            
            # Tạo audio với Coqui TTS
            tts_model.tts_to_file(text=text, file_path=str(speech_file_path))
            print(f"Audio generated using Coqui TTS: {speech_file_path}")
        
        return speech_file_path
    except APIError as e:
        print(f"OpenAI API Error during TTS generation: {e}")
        return None
    except Exception as e:
        print(f"Error during TTS generation: {e}")
        return None

def generate_text():
    """Tạo phản hồi text từ OpenAI, cập nhật lịch sử messages."""
    global messages, company_information # Sử dụng biến global (cần cẩn thận)
    try:
        # Log company information status for debugging
        if company_information.get('company_name'):
            print(f"Generating response with company context: {company_information['company_name']} - {company_information['job_position']}")
        else:
            print("Generating response with default context (no company info)")
            
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages
        )
        bot_response = response.choices[0].message.content


        messages.append({"role": "assistant", "content": bot_response})
        print("Bot response generated and added to history.")
        return bot_response
    except RateLimitError as e:
        print(f"OpenAI Rate Limit Error during chat completion: {e}")
        return "Sorry, I'm currently experiencing high traffic. Please try again later."
    except APIError as e:
        print(f"OpenAI API Error during chat completion: {e}")
        return "Sorry, I encountered an error trying to process your request. Please try again."
    except Exception as e:
        print(f"An unexpected error occurred during chat completion: {e}")
        return "An unexpected error occurred. Please try again."


# --- Các Route Flask ---

@app.route('/')
def index():
    """API status endpoint."""
    return jsonify({
        'status': 'CoInter Interview API is running',
        'version': '1.0',
        'endpoints': [
            '/process_audio_local',
            '/audio_to_text',
            '/response_text', 
            '/update_company_info',
            '/generate_init_text',
            '/generate_audio',
            '/update_personality_with_company_info',
            '/reset_session',
            '/get_company_info'
        ]
    })

@app.route('/chat/text')
def text_chat():
    """API status for text chat."""
    return jsonify({'status': 'Text chat API endpoint available'})

@app.route('/chat/speech')
def speech_chat():
    """API status for speech chat."""
    return jsonify({'status': 'Speech chat API endpoint available'})

@app.route('/get_last_messages')
def get_last_messages():
    if messages:
        user_message = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), None)
        bot_reply = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'assistant'), None)
        return jsonify({'user_message': user_message, 'bot_reply': bot_reply})
    return jsonify({'user_message': '', 'bot_reply': ''})
@app.route('/send_message', methods=['POST'])
def send_message():
    """Nhận tin nhắn text từ user, gửi đến OpenAI, trả về phản hồi."""
    global messages
    try:
        user_input = request.json['message']
        if not user_input:
            return jsonify({'reply': "Please provide a message."}), 400

        # Thêm tin nhắn user vào history
        messages.append({"role": "user", "content": user_input})
        print("User message added to history.")

        # Gọi OpenAI để lấy phản hồi (hàm này đã tự thêm bot reply vào messages)
        bot_response = generate_text()

        # Lưu lịch sử (tùy chọn)
        save_history_to_json(messages)

        return jsonify({'reply': bot_response})

    except KeyError:
        return jsonify({'error': "Missing 'message' key in JSON payload."}), 400
    except Exception as e:
        print(f"Error in /send_message endpoint: {e}")
        # Trả về lỗi chung cho client
        return jsonify({'reply': "An internal server error occurred."}), 500


@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    """Chỉ thực hiện speech-to-text và trả về transcript ngay lập tức."""
    temp_audio_path = None
    converted_audio_path = None

    try:
        # Bước 1: Validate và xử lý file audio
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file part in the request"}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No selected audio file"}), 400

        # Lưu file âm thanh tạm thời
        temp_audio_path = Path(__file__).parent / f"temp_voice_{os.urandom(8).hex()}.webm"
        audio_file.save(temp_audio_path)

        # Chuyển đổi file âm thanh sang định dạng mp3
        converted_audio_path = temp_audio_path.with_suffix('.mp3')
        try:
            audio = AudioSegment.from_file(temp_audio_path)
            audio.export(converted_audio_path, format="mp3")
        except Exception as e:
            print(f"Error converting audio: {e}")
            return jsonify({"error": "Failed to convert audio file."}), 500
        finally:
            # Xóa file âm thanh tạm thời ban đầu
            if temp_audio_path.exists():
                temp_audio_path.unlink()

        # Bước 2: Chỉ thực hiện Speech-to-Text
        try:
            transcript = process_speech_to_text(converted_audio_path)
            print(f"Transcription completed: {transcript}")
            
            # Trả về transcript ngay lập tức để frontend log
            return jsonify({
                'transcript': transcript,
                'status': 'success',
                'message': 'Speech-to-text completed successfully'
            })
        except Exception as e:
            return jsonify({"error": "Failed to transcribe audio.", "details": str(e)}), 500

    except Exception as e:
        print(f"Error in /transcribe_audio endpoint: {e}")
        return jsonify({'error': "An internal server error occurred."}), 500
    finally:
        # Dọn dẹp file âm thanh tạm thời
        if converted_audio_path and converted_audio_path.exists():
            try:
                converted_audio_path.unlink()
                print(f"Deleted converted audio file: {converted_audio_path}")
            except OSError as e:
                print(f"Error deleting converted file {converted_audio_path}: {e}")

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """Nhận file audio, chuyển thành text, gửi đến OpenAI, tạo audio phản hồi - LEGACY VERSION."""
    global messages
    temp_audio_path = None
    converted_audio_path = None
    response_audio_path = None

    try:
        # Bước 1: Validate và xử lý file audio
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file part in the request"}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No selected audio file"}), 400

        # Lưu file âm thanh tạm thời
        temp_audio_path = Path(__file__).parent / f"temp_voice_{os.urandom(8).hex()}.webm"
        audio_file.save(temp_audio_path)

        # Chuyển đổi file âm thanh sang định dạng mp3
        converted_audio_path = temp_audio_path.with_suffix('.mp3')
        try:
            audio = AudioSegment.from_file(temp_audio_path)
            audio.export(converted_audio_path, format="mp3")
        except Exception as e:
            print(f"Error converting audio: {e}")
            return jsonify({"error": "Failed to convert audio file."}), 500
        finally:
            # Xóa file âm thanh tạm thời ban đầu
            if temp_audio_path.exists():
                temp_audio_path.unlink()

        # Bước 2: Chuyển đổi audio sang text (Speech-to-Text)
        try:
            transcript = process_speech_to_text(converted_audio_path)
            print(f"Speech-to-text completed: {transcript}")
        except Exception as e:
            return jsonify({"error": "Failed to transcribe audio."}), 500

        # Bước 3: Tạo response text từ user input
        try:
            # Thêm tin nhắn user vào history
            messages.append({"role": "user", "content": transcript})
            print("User message added to history.")
            
            # Gọi OpenAI để lấy phản hồi
            bot_response_text = generate_text()
        except Exception as e:
            return jsonify({"error": "Failed to generate text response."}), 500

        # Bước 4: Chuyển đổi text response thành audio
        try:
            # Tạo filename unique để tránh conflict
            filename = f"response_{os.urandom(4).hex()}.mp3"
            response_audio_path = generate_audio(bot_response_text, filename)
            
            if not response_audio_path:
                raise Exception("Failed to generate audio")
        except Exception as e:
            # Nếu tạo audio lỗi, vẫn trả về text với transcript để frontend log
            print("Failed to generate response audio, returning text reply.")
            save_history_to_json(messages)  # Lưu history trước khi trả về
            return jsonify({
                'reply_text': bot_response_text, 
                'transcript': transcript,  # Thêm transcript để frontend log
                'error': 'Could not generate audio response.'
            }), 500

        # Lưu lịch sử
        save_history_to_json(messages)

        # Gửi file audio phản hồi về client với header chứa transcript
        response = send_file(response_audio_path, as_attachment=True, download_name='response.mp3', mimetype='audio/mpeg')
        response.headers['X-Transcript'] = transcript  # Thêm transcript vào header để frontend có thể đọc
        return response

    except Exception as e:
        print(f"Error in /process_audio endpoint: {e}")
        return jsonify({'error': "An internal server error occurred."}), 500
    finally:
        # Dọn dẹp file âm thanh tạm thời
        if converted_audio_path and converted_audio_path.exists():
            try:
                converted_audio_path.unlink()
                print(f"Deleted converted audio file: {converted_audio_path}")
            except OSError as e:
                print(f"Error deleting converted file {converted_audio_path}: {e}")

@app.route('/streaming-demo')
def streaming_demo():
    """Demo page for streaming audio processing."""
    return jsonify({'status': 'Streaming demo endpoint available'})

@app.route('/tts-stt-test')
def tts_stt_test():
    """Demo page for testing local TTS/STT models."""
    return jsonify({'status': 'TTS/STT test endpoint available'})

@app.route('/download_audio/<filename>')
def download_audio(filename):
    """Download audio file được tạo."""
    try:
        file_path = Path(__file__).parent / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=True, download_name='response.mp3', mimetype='audio/mpeg')
        else:
            return jsonify({"error": "Audio file not found"}), 404
    except Exception as e:
        print(f"Error downloading audio file: {e}")
        return jsonify({"error": "Failed to download audio file"}), 500

@app.route('/get_interview_greeting/<filename>')
def get_interview_greeting(filename):
    """Get interview greeting audio file."""
    try:
        file_path = Path(__file__).parent / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=False, download_name=filename, mimetype='audio/mpeg')
        else:
            return jsonify({"error": "Greeting audio file not found"}), 404
    except Exception as e:
        print(f"Error serving greeting audio file: {e}")
        return jsonify({"error": "Failed to serve greeting audio file"}), 500

@app.route('/get_response_audio')
def get_response_audio():
    """Get the latest response audio file for auto-playing."""
    try:
        file_path = Path(__file__).parent / "response_audio.wav"
        if file_path.exists():
            return send_file(file_path, as_attachment=False, download_name='response_audio.wav', mimetype='audio/wav')
        else:
            return jsonify({"error": "Response audio file not found"}), 404
    except Exception as e:
        print(f"Error serving response audio file: {e}")
        return jsonify({"error": "Failed to serve response audio file"}), 500

@app.route('/test_local_tts_stt', methods=['POST'])
def test_local_tts_stt():
    """API test cho TTS và STT local - không sử dụng OpenAI API."""
    temp_audio_path = None
    converted_audio_path = None
    response_audio_path = None

    try:
        # Bước 1: Validate và xử lý file audio
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file part in the request"}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No selected audio file"}), 400

        # Lưu file âm thanh tạm thời
        temp_audio_path = Path(__file__).parent / f"temp_voice_{os.urandom(8).hex()}.webm"
        audio_file.save(temp_audio_path)

        # Chuyển đổi file âm thanh sang định dạng mp3
        converted_audio_path = temp_audio_path.with_suffix('.mp3')
        try:
            audio = AudioSegment.from_file(temp_audio_path)
            audio.export(converted_audio_path, format="mp3")
        except Exception as e:
            print(f"Error converting audio: {e}")
            return jsonify({"error": "Failed to convert audio file."}), 500
        finally:
            # Xóa file âm thanh tạm thời ban đầu
            if temp_audio_path.exists():
                temp_audio_path.unlink()

        # Bước 2: Chuyển đổi audio sang text (Speech-to-Text) - CHỈ DÙNG LOCAL
        try:
            if whisper_model is None:
                return jsonify({"error": "Local Whisper model not available. Cannot proceed without OpenAI API."}), 500
            
            # Sử dụng Whisper local
            print("Using local Whisper model for transcription")
            result = whisper_model.transcribe(str(converted_audio_path))
            transcript = result["text"]
            print(f"Local STT completed: {transcript}")
        except Exception as e:
            return jsonify({"error": "Failed to transcribe audio with local model.", "details": str(e)}), 500

        # Bước 3: Chuyển đổi transcript thành audio (Text-to-Speech) - CHỈ DÙNG LOCAL
        try:
            if tts_model is None:
                return jsonify({"error": "Local TTS model not available. Cannot proceed without OpenAI API."}), 500
            
            # Tạo filename unique để tránh conflict
            filename = f"test_tts_response_{os.urandom(4).hex()}.wav"
            response_audio_path = Path(__file__).parent / filename
            
            # Sử dụng Coqui TTS local
            print("Using local Coqui TTS model for audio generation")
            tts_model.tts_to_file(text=transcript, file_path=str(response_audio_path))
            print(f"Local TTS completed: {response_audio_path}")
            
        except Exception as e:
            return jsonify({
                "error": "Failed to generate audio with local TTS model.", 
                "transcript": transcript,  # Vẫn trả về transcript để user biết
                "details": str(e)
            }), 500

        # Gửi file audio phản hồi về client với thông tin transcript
        response = send_file(response_audio_path, as_attachment=True, download_name='test_response.wav', mimetype='audio/wav')
        response.headers['X-Transcript'] = transcript  # Thêm transcript vào header
        response.headers['X-Model-Used'] = 'Local-STT-TTS'  # Thông báo model được sử dụng
        return response

    except Exception as e:
        print(f"Error in /test_local_tts_stt endpoint: {e}")
        return jsonify({'error': "An internal server error occurred."}), 500
    finally:
        # Dọn dẹp file âm thanh tạm thời
        if converted_audio_path and converted_audio_path.exists():
            try:
                converted_audio_path.unlink()
                print(f"Deleted converted audio file: {converted_audio_path}")
            except OSError as e:
                print(f"Error deleting converted file {converted_audio_path}: {e}")

@app.route('/test_local_tts_stt_stream', methods=['POST'])
def test_local_tts_stt_stream():
    """API test streaming cho TTS và STT local - không sử dụng OpenAI API."""
    
    def generate_streaming_test_response():
        temp_audio_path = None
        converted_audio_path = None
        response_audio_path = None
        
        try:
            # Bước 1: Validate và xử lý file audio
            if 'audio' not in request.files:
                yield f"data: {json.dumps({'error': 'No audio file part in the request'})}\n\n"
                return

            audio_file = request.files['audio']
            if audio_file.filename == '':
                yield f"data: {json.dumps({'error': 'No selected audio file'})}\n\n"
                return

            # Gửi thông báo bắt đầu
            yield f"data: {json.dumps({'step': 'start', 'message': 'Testing local TTS/STT models', 'status': 'processing'})}\n\n"

            # Lưu file âm thanh tạm thời
            temp_audio_path = Path(__file__).parent / f"temp_voice_{os.urandom(8).hex()}.webm"
            audio_file.save(temp_audio_path)

            # Chuyển đổi file âm thanh sang định dạng mp3
            converted_audio_path = temp_audio_path.with_suffix('.mp3')
            try:
                audio = AudioSegment.from_file(temp_audio_path)
                audio.export(converted_audio_path, format="mp3")
            except Exception as e:
                print(f"Error converting audio: {e}")
                yield f"data: {json.dumps({'error': 'Failed to convert audio file'})}\n\n"
                return
            finally:
                # Xóa file âm thanh tạm thời ban đầu
                if temp_audio_path and temp_audio_path.exists():
                    temp_audio_path.unlink()

            # Bước 2: Chuyển đổi audio sang text (Speech-to-Text) - CHỈ DÙNG LOCAL
            try:
                if whisper_model is None:
                    yield f"data: {json.dumps({'error': 'Local Whisper model not available'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'step': 'stt', 'message': 'Converting speech to text using local Whisper', 'status': 'processing'})}\n\n"
                
                # Sử dụng Whisper local
                result = whisper_model.transcribe(str(converted_audio_path))
                transcript = result["text"]
                print(f"Local STT completed: {transcript}")
                
                # Gửi transcript ngay lập tức đến frontend
                yield f"data: {json.dumps({'step': 'stt_result', 'transcript': transcript, 'model': 'Local Whisper', 'status': 'completed'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': 'Failed to transcribe audio with local model'})}\n\n"
                return

            # Bước 3: Chuyển đổi transcript thành audio (Text-to-Speech) - CHỈ DÙNG LOCAL
            try:
                if tts_model is None:
                    yield f"data: {json.dumps({'error': 'Local TTS model not available'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'step': 'tts', 'message': 'Converting text to speech using local Coqui TTS', 'status': 'processing'})}\n\n"
                
                # Tạo filename unique để tránh conflict
                filename = f"test_tts_response_{os.urandom(4).hex()}.wav"
                response_audio_path = Path(__file__).parent / filename
                
                # Sử dụng Coqui TTS local
                tts_model.tts_to_file(text=transcript, file_path=str(response_audio_path))
                print(f"Local TTS completed: {response_audio_path}")
                
                # Gửi đường dẫn audio file
                yield f"data: {json.dumps({'step': 'tts_result', 'audio_file': filename, 'model': 'Local Coqui TTS', 'status': 'completed'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'step': 'tts_error', 'error': 'Failed to generate audio with local TTS', 'transcript': transcript})}\n\n"
                return

            # Gửi signal hoàn thành
            yield f"data: {json.dumps({'step': 'completed', 'message': 'Local TTS/STT test completed successfully', 'transcript': transcript, 'audio_file': filename, 'status': 'finished'})}\n\n"

        except Exception as e:
            print(f"Error in /test_local_tts_stt_stream endpoint: {e}")
            yield f"data: {json.dumps({'error': 'An internal server error occurred'})}\n\n"
        finally:
            # Dọn dẹp file âm thanh tạm thời
            if converted_audio_path and converted_audio_path.exists():
                try:
                    converted_audio_path.unlink()
                    print(f"Deleted converted audio file: {converted_audio_path}")
                except OSError as e:
                    print(f"Error deleting converted file {converted_audio_path}: {e}")

@app.route('/process_audio_local', methods=['POST'])
def process_audio_local():
    """
    Production endpoint for interview audio processing.
    This endpoint converts audio to text using local STT, generates AI interview response using OpenAI, 
    then converts the AI response to audio using local TTS.
    """
    global messages  # Access global messages for interview conversation
    temp_audio_path = None
    converted_audio_path = None
    response_audio_path = None
    
    try:
        # Bước 1: Validate và xử lý file audio
        print(f"DEBUG: Received request with files: {list(request.files.keys())}")
        if 'audio' not in request.files:
            print("DEBUG: No 'audio' key in request.files")
            return jsonify({"error": "No audio file part in the request"}), 400

        audio_file = request.files['audio']
        print(f"DEBUG: Audio file name: {audio_file.filename}")
        if audio_file.filename == '':
            print("DEBUG: Empty audio file name")
            return jsonify({"error": "No selected audio file"}), 400

        # Lưu file âm thanh tạm thời
        temp_audio_path = Path(__file__).parent / f"temp_voice_{os.urandom(8).hex()}.webm"
        audio_file.save(temp_audio_path)
        print(f"DEBUG: Saved temp audio file: {temp_audio_path} (size: {temp_audio_path.stat().st_size} bytes)")

        # Chuyển đổi file âm thanh sang định dạng mp3
        converted_audio_path = temp_audio_path.with_suffix('.mp3')
        try:
            audio = AudioSegment.from_file(temp_audio_path)
            print(f"DEBUG: Audio duration: {len(audio)}ms, sample rate: {audio.frame_rate}Hz")
            audio.export(converted_audio_path, format="mp3")
            print(f"DEBUG: Converted audio file: {converted_audio_path} (size: {converted_audio_path.stat().st_size} bytes)")
        except Exception as e:
            print(f"Error converting audio: {e}")
            return jsonify({"error": "Failed to convert audio file."}), 500
        finally:
            # Xóa file âm thanh tạm thời ban đầu
            if temp_audio_path.exists():
                temp_audio_path.unlink()

        # Bước 2: Chuyển đổi audio sang text (Speech-to-Text) sử dụng hàm process_speech_to_text
        try:
            print("DEBUG: Starting transcription process...")
            transcript = process_speech_to_text(converted_audio_path)
            transcript = transcript.strip()
            print(f"DEBUG: Raw transcript: '{transcript}' (length: {len(transcript)})")
            
            if not transcript:
                print("DEBUG: Empty transcript detected")
                # Instead of returning 400, let's return a helpful message and continue with a default prompt
                transcript = "I'm sorry, I couldn't hear what you said clearly. Could you please repeat that?"
                print(f"DEBUG: Using fallback transcript: '{transcript}'")
            
            print(f"STT completed: {transcript}")
        except Exception as e:
            print(f"DEBUG: Exception during transcription: {e}")
            return jsonify({"error": "Failed to transcribe audio.", "details": str(e)}), 500

        # Bước 3: Tạo response text từ OpenAI (Interview AI response)
        try:
            # Thêm tin nhắn user vào history
            messages.append({"role": "user", "content": transcript})
            print("User message added to history for interview processing.")
            
            # Gọi OpenAI để lấy phản hồi interview
            bot_response_text = generate_text()
            print(f"AI Interview response generated: {bot_response_text[:100]}...")
        except Exception as e:
            return jsonify({"error": "Failed to generate AI interview response.", "details": str(e)}), 500

        # Bước 4: Chuyển AI response text thành audio (Text-to-Speech) sử dụng hàm generate_audio
        try:
            print("🔊 Converting AI response to audio...")
            # Tạo filename cụ thể
            filename = "response_audio.wav"
            response_audio_path = generate_audio(bot_response_text, filename)
            
            if not response_audio_path:
                print("❌ Failed to generate audio for AI response")
                return jsonify({
                    "error": "Failed to generate audio response.", 
                    "transcript": transcript,
                    "ai_response": bot_response_text,
                    "audio_error": "TTS generation failed"
                }), 500
            
            print(f"✅ AI response audio generated: {response_audio_path}")
            
        except Exception as e:
            print(f"❌ Error generating audio for AI response: {e}")
            return jsonify({
                "error": "Failed to generate audio with TTS model.", 
                "transcript": transcript,
                "ai_response": bot_response_text,
                "details": str(e)
            }), 500

        # Lưu lịch sử chat
        save_history_to_json(messages)

        # Trả về audio file với thông tin trong header
        response = send_file(response_audio_path, as_attachment=True, download_name='response_audio.wav', mimetype='audio/wav')
        response.headers['X-Transcript'] = transcript
        response.headers['X-AI-Response'] = bot_response_text[:500] + "..." if len(bot_response_text) > 500 else bot_response_text  # Truncate if too long
        response.headers['X-Model-Used'] = 'STT-OpenAI-TTS'  # Updated model info
        response.headers['X-Audio-File'] = 'response_audio.wav'  # Thêm header để frontend biết tên file
        return response

    except Exception as e:
        print(f"Error in process_audio_local: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        # Dọn dẹp file âm thanh tạm thời
        if converted_audio_path and converted_audio_path.exists():
            try:
                converted_audio_path.unlink()
                print(f"Deleted converted audio file: {converted_audio_path}")
            except OSError as e:
                print(f"Error deleting converted file {converted_audio_path}: {e}")
        
        # Không xóa response_audio_path ngay để frontend có thể truy cập
        # File sẽ được overwrite ở lần chạy tiếp theo

@app.route('/audio_to_text', methods=['POST'])
def audio_to_text():
    """API endpoint to convert audio to text (Steps 1-2 from process_audio_local)."""
    temp_audio_path = None
    converted_audio_path = None
    
    try:
        # Bước 1: Validate và xử lý file audio
        print(f"DEBUG: Received audio_to_text request with files: {list(request.files.keys())}")
        if 'audio' not in request.files:
            print("DEBUG: No 'audio' key in request.files")
            return jsonify({"error": "No audio file part in the request"}), 400

        audio_file = request.files['audio']
        print(f"DEBUG: Audio file name: {audio_file.filename}")
        if audio_file.filename == '':
            print("DEBUG: Empty audio file name")
            return jsonify({"error": "No selected audio file"}), 400

        # Lưu file âm thanh tạm thời
        temp_audio_path = Path(__file__).parent / f"temp_voice_{os.urandom(8).hex()}.webm"
        audio_file.save(temp_audio_path)
        print(f"DEBUG: Saved temp audio file: {temp_audio_path} (size: {temp_audio_path.stat().st_size} bytes)")

        # Chuyển đổi file âm thanh sang định dạng mp3
        converted_audio_path = temp_audio_path.with_suffix('.mp3')
        try:
            audio = AudioSegment.from_file(temp_audio_path)
            print(f"DEBUG: Audio duration: {len(audio)}ms, sample rate: {audio.frame_rate}Hz")
            audio.export(converted_audio_path, format="mp3")
            print(f"DEBUG: Converted audio file: {converted_audio_path} (size: {converted_audio_path.stat().st_size} bytes)")
        except Exception as e:
            print(f"Error converting audio: {e}")
            return jsonify({"error": "Failed to convert audio file."}), 500
        finally:
            # Xóa file âm thanh tạm thời ban đầu
            if temp_audio_path.exists():
                temp_audio_path.unlink()

        # Bước 2: Chuyển đổi audio sang text (Speech-to-Text)
        try:
            print("DEBUG: Starting transcription process...")
            transcript = process_speech_to_text(converted_audio_path)
            transcript = transcript.strip()
            print(f"DEBUG: Raw transcript: '{transcript}' (length: {len(transcript)})")
            
            if not transcript:
                print("DEBUG: Empty transcript detected")
                # Return a helpful message for empty transcript
                transcript = "I'm sorry, I couldn't hear what you said clearly. Could you please repeat that?"
                print(f"DEBUG: Using fallback transcript: '{transcript}'")
            
            print(f"STT completed: {transcript}")
            
            # Return transcript as JSON
            return jsonify({
                'success': True,
                'transcript': transcript,
                'message': 'Audio to text conversion completed successfully'
            })
            
        except Exception as e:
            print(f"DEBUG: Exception during transcription: {e}")
            return jsonify({"error": "Failed to transcribe audio.", "details": str(e)}), 500

    except Exception as e:
        print(f"Error in audio_to_text: {str(e)}")
        return jsonify({'error': 'Internal server error during audio processing'}), 500
    
    finally:
        # Dọn dẹp file âm thanh tạm thời
        if converted_audio_path and converted_audio_path.exists():
            try:
                converted_audio_path.unlink()
                print(f"Deleted converted audio file: {converted_audio_path}")
            except OSError as e:
                print(f"Error deleting converted file {converted_audio_path}: {e}")

@app.route('/response_text', methods=['POST'])
def response_text():
    """API endpoint to generate AI response text from user transcript (Step 3 from process_audio_local)."""
    global messages  # Access global messages for interview conversation
    
    try:
        data = request.get_json()
        if not data or 'transcript' not in data:
            return jsonify({'error': 'No transcript provided'}), 400
        
        transcript = data['transcript'].strip()
        if not transcript:
            return jsonify({'error': 'Empty transcript provided'}), 400
        
        print(f"📝 Generating AI response for transcript: {transcript[:100]}...")
        
        # Bước 3: Tạo response text từ OpenAI (Interview AI response)
        try:
            # Thêm tin nhắn user vào history
            messages.append({"role": "user", "content": transcript})
            print("User message added to history for interview processing.")
            
            # Gọi OpenAI để lấy phản hồi interview
            bot_response_text = generate_text()
            print(f"AI Interview response generated: {bot_response_text[:100]}...")
            
            # Lưu lịch sử chat
            save_history_to_json(messages)
            
            return jsonify({
                'success': True,
                'response_text': bot_response_text,
                'transcript': transcript,
                'message': 'AI response text generated successfully'
            })
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return jsonify({"error": "Failed to generate AI interview response.", "details": str(e)}), 500

    except Exception as e:
        print(f"Error in response_text: {str(e)}")
        return jsonify({'error': 'Internal server error during text generation'}), 500

@app.route('/generate_audio', methods=['POST'])
def generate_audio_api():
    """API endpoint to convert text to audio and return audio file."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        filename = data.get('filename', 'generated_audio.mp3')  # Allow custom filename
        
        print(f"🔊 Converting text to audio: {text[:50]}...")
        
        # Use the existing generate_audio function
        audio_path = generate_audio(text, filename)
        
        if not audio_path:
            return jsonify({
                'error': 'Failed to generate audio',
                'details': 'TTS generation failed'
            }), 500
        
        print(f"✅ Audio generated: {audio_path}")
        
        # Return audio file
        response = send_file(audio_path, as_attachment=True, download_name=filename, mimetype='audio/mpeg')
        response.headers['X-Audio-File'] = filename
        response.headers['X-Text-Source'] = text[:100] + "..." if len(text) > 100 else text
        response.headers['X-Text-Length'] = str(len(text))
        return response
        
    except Exception as e:
        print(f"Error in generate_audio API: {e}")
        return jsonify({'error': 'Failed to generate audio', 'details': str(e)}), 500

@app.route('/update_company_info', methods=['POST'])
def update_company_info():
    """Update company information from frontend form."""
    global company_information, messages
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update company information
        company_information.update({
            'company_name': data.get('companyName', ''),
            'job_position': data.get('jobPosition', ''),
            'company_field': data.get('companyField', ''),
            'company_products': data.get('companyProducts', ''),
            'company_culture': data.get('companyCulture', ''),
            'other_info': data.get('otherInfo', '')
        })

        print(f"Company information updated: {company_information}")
        
        return jsonify({
            'success': True,
            'message': 'Company information updated successfully',
            'company_info': company_information
        })
        
    except Exception as e:
        print(f"Error updating company info: {e}")
        return jsonify({'error': 'Failed to update company information'}), 500

@app.route('/generate_init_text', methods=['POST'])
def generate_init_text():
    """Generate initial greeting text based on company information."""
    global messages, company_information, cv
    
    try:
        # Update personality with company information first
        if company_information.get('company_name'):
            # Create completely new personality with dynamic company data
            updated_personality = f"""
You are a chatbot acting as a professional interviewer for {company_information.get('company_name', 'the company')}.

**Context:**
You are interviewing a candidate for the position of "{company_information.get('job_position', 'a role')}" at {company_information.get('company_name', 'this company')}.

**Company Details (provided by candidate):**
- Company Name: {company_information.get('company_name', 'Not specified')}
- Job Position: {company_information.get('job_position', 'Not specified')}
- Company Field: {company_information.get('company_field', 'Not specified')}
- Company Products/Services: {company_information.get('company_products', 'Not specified')}
- Company Culture: {company_information.get('company_culture', 'Not specified')}
- Additional Information: {company_information.get('other_info', 'Not specified')}

**Important Personality Rule**: After receiving each user response, you must:
1. Implicitly score the answer internally (never reveal numerical scores during rounds 1-3)
2. Generate smooth connecting commentary and evaluation
3. Provide constructive feedback that relates to the role requirements
4. Ask the next question in sequence according to the defined round structure
5. Maintain natural conversation flow while strictly following the question count per round

**Interview Structure:**
**Interview Process (STRICTLY follow this structure):**

1.  **Round 1: Personal Introduction (EXACTLY 2 questions)**
    * Begin with a warm, personalized introduction focusing on the {company_information.get('job_position', 'position')} role at the {company_information.get('company_name', 'company')}.
    * Ask EXACTLY 2 questions covering these key areas:
        - Personal introduction and background (encourage them to share about themselves)
        - Understanding of their strengths and areas for growth
    * **After each answer**: 
        - Provide encouraging, specific feedback that connects their responses to the role
        - Implicitly score the answer internally (do not reveal scores to candidate)
        - Generate smooth transition commentary and evaluation
    * **Analysis Process**: Evaluate how their introduction and self-assessment relate to the {company_information.get('job_position', 'job position')} requirements.
    * **Transition Rule**: After EXACTLY 2 questions and responses, naturally transition to Round 2 with connecting commentary.

2.  **Round 2: Professional Knowledge & Company Fit (3 questions)**
    * Ask exactly 3 questions about professional knowledge specifically related to:
        - {company_information.get('company_field', 'the industry')} industry
        - Skills needed for {company_information.get('job_position', 'this position')}
        - Experience with {company_information.get('company_products', 'relevant products/services')}
    * Test depth of understanding and evaluate how their skills match {company_information.get('company_name', 'the company')}'s needs.
    * Provide feedback and advice for improvement after each answer.
    * After 3 questions, move to Round 3.

3.  **Round 3: Project Experience & Technical Deep Dive (4 questions)**
    * Ask exactly 4 questions about projects and technical experience relevant to {company_information.get('company_field', 'this field')}.
    * Focus on how their experience applies to {company_information.get('job_position', 'this position')}.
    * Ask specific questions about:
        - Technical expertise relevant to {company_information.get('company_products', 'the company\'s products')}
        - Problem-solving approaches that would work at {company_information.get('company_name', 'this company')}
        - Team collaboration and project management experience
        - Challenges faced and solutions implemented in previous projects
    * Provide detailed feedback and suggestions after each answer.
    * After 4 questions, move to Round 4.

4.  **Round 4: Summary & Scoring**
    * Provide an implicit summary by naturally discussing the candidate's overall performance and fit for {company_information.get('job_position', 'the position')} at {company_information.get('company_name', 'the company')}.
    * Give only a single overall score: **SCORE: X/10**
    * Briefly mention key strengths and areas for improvement.
    * Thank them for applying and inform about next steps.

**Requirements:**
* STRICTLY follow the question count for each round (2-3-4 questions).
* Always reference {company_information.get('company_name', 'the company')} and {company_information.get('job_position', 'the position')} in your questions.
* Tailor ALL technical questions to {company_information.get('company_field', 'the industry')}.
* Evaluate cultural fit based on: {company_information.get('company_culture', 'the stated company culture')}.
* Keep track of question count and announce when moving to next round.
* Maintain a professional, friendly tone throughout.
* Provide constructive feedback after each answer.
* At the end, give a single overall score out of 10.

**Candidate CV:** {cv}

Please begin the interview with a warm greeting for the {company_information.get('job_position', 'position')} role at {company_information.get('company_name', 'the company')} and start Round 1 with the first personal introduction question!
"""
            
            # Update the system message in the messages list
            if messages and messages[0]['role'] == 'system':
                messages[0]['content'] = updated_personality
            else:
                messages.insert(0, {"role": "system", "content": updated_personality})
                
            print("✅ Personality updated with dynamic company information:")
            print(f"   Company: {company_information['company_name']}")
            print(f"   Position: {company_information['job_position']}")
            print(f"   Field: {company_information['company_field']}")
            print(f"   Culture: {company_information['company_culture']}")
        else:
            # Reset to default personality if no company info
            if messages and messages[0]['role'] == 'system':
                messages[0]['content'] = get_personality()
            else:
                messages.insert(0, {"role": "system", "content": get_personality()})
        
        # Generate initial greeting text
        print("🤖 Generating initial interview greeting text...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        initial_greeting = response.choices[0].message.content
        print(f"📝 Initial greeting generated: {initial_greeting[:100]}...")
        
        # Add bot response to messages
        messages.append({"role": "assistant", "content": initial_greeting})
        
        return jsonify({
            'success': True,
            'greeting_text': initial_greeting,
            'message': 'Initial greeting text generated successfully'
        })
        
    except Exception as e:
        print(f"Error generating initial text: {e}")
        return jsonify({'error': 'Failed to generate initial greeting text', 'details': str(e)}), 500

@app.route('/process_init_audio', methods=['POST'])
def process_init_audio():
    """Convert greeting text to audio and return audio file."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        greeting_text = data['text']
        
        print("🔊 Converting greeting text to audio...")
        
        # Generate audio file
        audio_filename = "interview_greeting.mp3"
        audio_path = generate_audio(greeting_text, audio_filename)
        
        if not audio_path:
            return jsonify({
                'error': 'Failed to generate audio',
                'details': 'TTS generation failed'
            }), 500
        
        print(f"✅ Greeting audio generated: {audio_path}")
        
        # Return audio file
        response = send_file(audio_path, as_attachment=True, download_name=audio_filename, mimetype='audio/mpeg')
        response.headers['X-Audio-File'] = audio_filename
        response.headers['X-Text-Source'] = greeting_text[:100] + "..." if len(greeting_text) > 100 else greeting_text
        return response
        
    except Exception as e:
        print(f"Error processing init audio: {e}")
        return jsonify({'error': 'Failed to process audio', 'details': str(e)}), 500

@app.route('/update_personality_with_company_info', methods=['POST'])
def update_personality_api():
    """API endpoint to update chatbot personality with current company information and generate initial greeting."""
    try:
        # Call the personality update function (now includes OpenAI call and audio generation)
        result = update_personality_with_company_info()
        
        if result.get('success'):
            print("✅ Chatbot personality updated via API call with initial greeting")
            
            return jsonify({
                'success': True,
                'message': 'Chatbot personality updated successfully with initial greeting',
                'company_info': company_information,
                'has_company_info': bool(company_information.get('company_name')),
                'greeting_text': result.get('greeting_text'),
                'audio_file': result.get('audio_file'),
                'audio_path': result.get('audio_path'),
                'audio_error': result.get('audio_error')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
        
    except Exception as e:
        print(f"Error updating personality: {e}")
        return jsonify({'error': 'Failed to update chatbot personality'}), 500

@app.route('/reset_session', methods=['POST'])
def reset_session():
    """Reset chat session and company information."""
    global messages, company_information
    
    try:
        # Reset company information to empty state
        company_information = {
            'company_name': '',
            'job_position': '',
            'company_field': '',
            'company_products': '',
            'company_culture': '',
            'other_info': ''
        }
        
        # Reset messages to initial state with system prompt
        messages = [{"role": "system", "content": get_personality()}]
        
        print("Session reset successfully")
        
        return jsonify({
            'success': True,
            'message': 'Session reset successfully'
        })
        
    except Exception as e:
        print(f"Error resetting session: {e}")
        return jsonify({'error': 'Failed to reset session'}), 500

@app.route('/get_company_info', methods=['GET'])
def get_company_info():
    """Get current company information status."""
    global company_information
    
    try:
        return jsonify({
            'success': True,
            'company_info': company_information,
            'has_company_info': bool(company_information.get('company_name'))
        })
        
    except Exception as e:
        print(f"Error getting company info: {e}")
        return jsonify({'error': 'Failed to get company information'}), 500

@app.route('/get_system_prompt', methods=['GET'])
def get_system_prompt():
    """Get current system prompt for debugging."""
    global messages
    
    try:
        system_prompt = ""
        if messages and messages[0]['role'] == 'system':
            system_prompt = messages[0]['content']
        
        return jsonify({
            'success': True,
            'system_prompt': system_prompt,
            'total_messages': len(messages)
        })
        
    except Exception as e:
        print(f"Error getting system prompt: {e}")
        return jsonify({'error': 'Failed to get system prompt'}), 500

def update_personality_with_company_info():
    """Update the personality prompt with current company information and generate initial greeting with audio."""
    global messages, cv
    
    # Create dynamic personality based on company information
    if company_information.get('company_name'):
        # Create completely new personality with dynamic company data
        updated_personality = f"""
You are a chatbot acting as a professional interviewer for {company_information.get('company_name', 'the company')}.

**Context:**
You are interviewing a candidate for the position of "{company_information.get('job_position', 'a role')}" at {company_information.get('company_name', 'this company')}.

**Company Details (provided by candidate):**
- Company Name: {company_information.get('company_name', 'Not specified')}
- Job Position: {company_information.get('job_position', 'Not specified')}
- Company Field: {company_information.get('company_field', 'Not specified')}
- Company Products/Services: {company_information.get('company_products', 'Not specified')}
- Company Culture: {company_information.get('company_culture', 'Not specified')}
- Additional Information: {company_information.get('other_info', 'Not specified')}

**Important Personality Rule**: After receiving each user response, you must:
1. Implicitly score the answer internally (never reveal numerical scores during rounds 1-3)
2. Generate smooth connecting commentary and evaluation
3. Provide constructive feedback that relates to the role requirements
4. Ask the next question in sequence according to the defined round structure
5. Maintain natural conversation flow while strictly following the question count per round

**Interview Structure:**
**Interview Process (STRICTLY follow this structure):**

1.  **Round 1: Personal Introduction (EXACTLY 2 questions)**
    * Begin with a warm, personalized introduction focusing on the {company_information.get('job_position', 'position')} role at the {company_information.get('company_name', 'company')}.
    * Ask EXACTLY 2 questions covering these key areas:
        - Personal introduction and background (encourage them to share about themselves)
        - Understanding of their strengths and areas for growth
    * **After each answer**: 
        - Provide encouraging, specific feedback that connects their responses to the role
        - Implicitly score the answer internally (do not reveal scores to candidate)
        - Generate smooth transition commentary and evaluation
    * **Analysis Process**: Evaluate how their introduction and self-assessment relate to the {company_information.get('job_position', 'job position')} requirements.
    * **Transition Rule**: After EXACTLY 2 questions and responses, naturally transition to Round 2 with connecting commentary.


2.  **Round 2: Professional Knowledge & Company Fit (3 questions)**
    * Ask exactly 3 questions about professional knowledge specifically related to:
        - {company_information.get('company_field', 'the industry')} industry
        - Skills needed for {company_information.get('job_position', 'this position')}
        - Experience with {company_information.get('company_products', 'relevant products/services')}
    * Test depth of understanding and evaluate how their skills match {company_information.get('company_name', 'the company')}'s needs.
    * Provide feedback and advice for improvement after each answer.
    * After 3 questions, move to Round 3.

3.  **Round 3: Project Experience & Technical Deep Dive (4 questions)**
    * Ask exactly 4 questions about projects and technical experience relevant to {company_information.get('company_field', 'this field')}.
    * Focus on how their experience applies to {company_information.get('job_position', 'this position')}.
    * Ask specific questions about:
        - Technical expertise relevant to {company_information.get('company_products', 'the company\'s products')}
        - Problem-solving approaches that would work at {company_information.get('company_name', 'this company')}
        - Team collaboration and project management experience
        - Challenges faced and solutions implemented in previous projects
    * Provide detailed feedback and suggestions after each answer.
    * After 4 questions, move to Round 4.

4.  **Round 4: Summary & Scoring**
    * Provide an implicit summary by naturally discussing the candidate's overall performance and fit for {company_information.get('job_position', 'the position')} at {company_information.get('company_name', 'the company')}.
    * Give only a single overall score: **SCORE: X/10**
    * Briefly mention key strengths and areas for improvement.
    * Thank them for applying and inform about next steps.

**Requirements:**
* STRICTLY follow the question count for each round (2-3-4 questions).
* Always reference {company_information.get('company_name', 'the company')} and {company_information.get('job_position', 'the position')} in your questions.
* Tailor ALL technical questions to {company_information.get('company_field', 'the industry')}.
* Evaluate cultural fit based on: {company_information.get('company_culture', 'the stated company culture')}.
* Keep track of question count and announce when moving to next round.
* Maintain a professional, friendly tone throughout.
* Provide constructive feedback after each answer.
* At the end, give a single overall score out of 10.

**Candidate CV:** {cv}

Please begin the interview with a warm greeting for the {company_information.get('job_position', 'position')} role at {company_information.get('company_name', 'the company')} and start Round 1 with the first personal introduction question!
"""
        
        # Update the system message in the messages list
        if messages and messages[0]['role'] == 'system':
            messages[0]['content'] = updated_personality
        else:
            messages.insert(0, {"role": "system", "content": updated_personality})
            
        print("✅ Personality updated with dynamic company information:")
        print(f"   Company: {company_information['company_name']}")
        print(f"   Position: {company_information['job_position']}")
        print(f"   Field: {company_information['company_field']}")
        print(f"   Culture: {company_information['company_culture']}")
        
        # Gọi OpenAI để tạo câu chào đầu tiên và chuyển thành audio
        try:
            print("🤖 Generating initial interview greeting...")
            
            # Gọi OpenAI để tạo câu chào đầu tiên
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            
            initial_greeting = response.choices[0].message.content
            print(f"📝 Initial greeting generated: {initial_greeting[:100]}...")
            
            # Thêm phản hồi của bot vào messages
            messages.append({"role": "assistant", "content": initial_greeting})
            
            # Chuyển text thành audio sử dụng local TTS model
            try:
                print("🔊 Converting greeting to audio using local TTS...")
                audio_filename = "interview_greeting.mp3"
                audio_path = generate_audio(initial_greeting, audio_filename)
                
                if audio_path:
                    print(f"✅ Interview greeting audio generated: {audio_path}")
                    return {
                        'greeting_text': initial_greeting,
                        'audio_file': audio_filename,
                        'audio_path': str(audio_path),
                        'success': True
                    }
                else:
                    print("❌ Failed to generate audio for greeting")
                    return {
                        'greeting_text': initial_greeting,
                        'audio_file': None,
                        'success': True,
                        'audio_error': 'Failed to generate audio'
                    }
                    
            except Exception as e:
                print(f"❌ Error generating audio for greeting: {e}")
                return {
                    'greeting_text': initial_greeting,
                    'audio_file': None,
                    'success': True,
                    'audio_error': str(e)
                }
                
        except Exception as e:
            print(f"❌ Error generating initial greeting: {e}")
            return {
                'success': False,
                'error': f'Failed to generate initial greeting: {str(e)}'
            }
            
    else:
        print("❌ No company information available - using default personality")
        # Reset to default personality if no company info
        if messages and messages[0]['role'] == 'system':
            messages[0]['content'] = get_personality()
        else:
            messages.insert(0, {"role": "system", "content": get_personality()})
            
        # Tạo câu chào mặc định cho trường hợp không có thông tin công ty
        try:
            print("🤖 Generating default interview greeting...")
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            
            initial_greeting = response.choices[0].message.content
            print(f"📝 Default greeting generated: {initial_greeting[:100]}...")
            
            # Thêm phản hồi của bot vào messages
            messages.append({"role": "assistant", "content": initial_greeting})
            
            # Chuyển text thành audio
            try:
                print("🔊 Converting default greeting to audio...")
                audio_filename = "interview_greeting.mp3"
                audio_path = generate_audio(initial_greeting, audio_filename)
                
                if audio_path:
                    print(f"✅ Default greeting audio generated: {audio_path}")
                    return {
                        'greeting_text': initial_greeting,
                        'audio_file': audio_filename,
                        'audio_path': str(audio_path),
                        'success': True
                    }
                else:
                    return {
                        'greeting_text': initial_greeting,
                        'audio_file': None,
                        'success': True,
                        'audio_error': 'Failed to generate audio'
                    }
                    
            except Exception as e:
                print(f"❌ Error generating audio for default greeting: {e}")
                return {
                    'greeting_text': initial_greeting,
                    'audio_file': None,
                    'success': True,
                    'audio_error': str(e)
                }
                
        except Exception as e:
            print(f"❌ Error generating default greeting: {e}")
            return {
                'success': False,
                'error': f'Failed to generate default greeting: {str(e)}'
            }

@app.route('/debug_company_info', methods=['GET'])
def debug_company_info():
    """Debug endpoint to check current company information and system prompt."""
    global company_information, messages
    
    try:
        system_prompt = ""
        if messages and messages[0]['role'] == 'system':
            system_prompt = messages[0]['content'][:800] + "..." if len(messages[0]['content']) > 800 else messages[0]['content']
        
        return jsonify({
            'success': True,
            'company_information': company_information,
            'has_company_info': bool(company_information.get('company_name')),
            'system_prompt_preview': system_prompt,
            'total_messages': len(messages),
            'personality_contains_company': company_information.get('company_name', '') in system_prompt if system_prompt else False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add this after your other route definitions
if __name__ == '__main__':
    # !!! Chế độ debug không phù hợp cho production
    # Trong production, sử dụng WSGI server như Gunicorn hoặc Waitress
    # Ví dụ: gunicorn -w 4 app:app
    # Load lịch sử khi khởi động (Tùy chọn)
    # initial_history = load_history_from_json()
    # if initial_history:
    #     messages = initial_history # Ghi đè messages mặc định
    # else:
    #     # Nếu không load được hoặc file rỗng, đảm bảo messages có system prompt
    #     if not any(msg['role'] == 'system' for msg in messages):
    #          messages.insert(0, {"role": "system", "content": personality})

    print("Starting Flask app in debug mode...")
    app.run(debug=True, host='0.0.0.0', port=5000) # Chạy trên tất cả interface, port 5000

# --- Hàm Extract CV từ PDF ---

def extract_text_from_pdf(pdf_file_path):
    """Extract text from PDF file using PyMuPDF."""
    try:
        doc = fitz.open(pdf_file_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        
        doc.close()
        print(f"Successfully extracted text from PDF: {len(text)} characters")
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise Exception("Failed to extract text from PDF")

def analyze_cv_with_gpt(cv_text):
    """Analyze CV text using GPT and return structured JSON."""
    try:
        prompt = f"""Analyze this CV into a JSON structure with three main sections: strengths and weaknesses, work experience (if available) or personal projects, and extracurricular activities.

CV Content:
{cv_text}

Please provide a detailed analysis in the following JSON format:
{{
    "strengths_and_weaknesses": {{
        "strengths": ["list of identified strengths"],
        "weaknesses": ["list of potential areas for improvement"]
    }},
    "work_experience_or_projects": {{
        "work_experience": [
            {{
                "position": "job title",
                "company": "company name",
                "duration": "time period",
                "responsibilities": ["list of key responsibilities"],
                "achievements": ["list of achievements"]
            }}
        ],
        "personal_projects": [
            {{
                "project_name": "name",
                "description": "brief description",
                "technologies": ["technologies used"],
                "outcomes": ["results or achievements"]
            }}
        ]
    }},
    "extracurricular_activities": [
        {{
            "activity": "activity name",
            "role": "role or position",
            "description": "brief description",
            "skills_gained": ["skills or experiences gained"]
        }}
    ]
}}

Ensure the analysis is thorough, objective, and focuses on professional development potential."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis_result = response.choices[0].message.content
        print("CV analysis completed successfully")
        return analysis_result
        
    except Exception as e:
        print(f"Error analyzing CV: {e}")
        raise Exception("Failed to analyze CV")

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    """Upload CV PDF file, extract text, and analyze with GPT."""
    temp_pdf_path = None
    
    try:
        # Validate file upload
        if 'cv' not in request.files:
            return jsonify({"error": "No CV file part in the request"}), 400

        cv_file = request.files['cv']
        if cv_file.filename == '':
            return jsonify({"error": "No selected CV file"}), 400

        # Check if file is PDF
        if not cv_file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400

        # Save temporary PDF file
        temp_pdf_path = Path(__file__).parent / f"temp_cv_{os.urandom(8).hex()}.pdf"
        cv_file.save(temp_pdf_path)
        
        # Extract text from PDF
        try:
            cv_text = extract_text_from_pdf(temp_pdf_path)
            
            if not cv_text.strip():
                return jsonify({"error": "No text could be extracted from the PDF. Please ensure the PDF contains readable text."}), 400
                
        except Exception as e:
            return jsonify({"error": "Failed to extract text from PDF", "details": str(e)}), 500

        # Analyze CV with GPT
        try:
            analysis_result = analyze_cv_with_gpt(cv_text)
            
            # Try to parse as JSON to validate structure
            try:
                analysis_json = json.loads(analysis_result)
            except json.JSONDecodeError:
                # If not valid JSON, return as text
                analysis_json = {"raw_analysis": analysis_result}
            
            return jsonify({
                "status": "success",
                "message": "CV uploaded and analyzed successfully",
                "extracted_text": cv_text[:500] + "..." if len(cv_text) > 500 else cv_text,  # First 500 chars for preview
                "analysis": analysis_json
            })
            
        except Exception as e:
            return jsonify({"error": "Failed to analyze CV", "details": str(e)}), 500

    except Exception as e:
        print(f"Error in /upload_cv endpoint: {e}")
        return jsonify({'error': "An internal server error occurred."}), 500
    finally:
        # Clean up temporary PDF file
        if temp_pdf_path and temp_pdf_path.exists():
            try:
                temp_pdf_path.unlink()
                print(f"Deleted temporary PDF file: {temp_pdf_path}")
            except OSError as e:
                print(f"Error deleting temporary file {temp_pdf_path}: {e}")

@app.route('/update_cv_info', methods=['POST'])
def update_cv_info():
    """Update CV information in the interview system."""
    global messages, cv
    
    try:
        cv_analysis = request.json.get('cv_analysis')
        if not cv_analysis:
            return jsonify({"error": "No CV analysis data provided"}), 400

        # Update the global cv variable with the analyzed data
        cv = json.dumps(cv_analysis, indent=2, ensure_ascii=False)
        
        # Update the system message to include the new CV information
        new_personality = f"""
You are a chatbot acting as a professional interviewer for a company.
**Context:**

* You are provided with the candidate's CV and may receive specific company information during the interview process.
* Your task is to analyze the CV and available company information to ask relevant interview questions, assessing the candidate's skills and experience against job requirements.
* When company information is provided, tailor your questions specifically to that company's field, culture, and position requirements.

**Interview Process:**

1.  **Round 1: Personal Introduction (warm-up)**
    * Ask an open-ended question for the candidate to introduce themselves (not directly related to professional skills).
        * Example: "Could you share a bit about your hobbies or extracurricular activities?"
    * Ask 1-2 follow-up questions to understand the candidate's personality and motivation better.
    * Record the answers and provide brief, encouraging feedback.
    * Analyze the answer, make comments, and give advice to the user to improve their answer (if needed).
2.  **Round 2: Basic Professional Knowledge**
    * Based on the job description and company information (if available), ask 2 questions about basic professional knowledge related to the position.
    * Ask 1-2 follow-up questions for each main question to test the candidate's depth of understanding.
    * Record the answers.
    * Analyze the answer, explain again if the user answer is wrong, and give advice to the user to improve their answer.
3.  **Round 3: Project Experience**
    * Ask the candidate to describe in detail the projects they have participated in (based on the CV).
    * Ask deeper questions to understand:
        * What were the candidate's roles in the projects?
        * Which teams did the candidate work with?
        * Detailed analysis of the technical expertise used in the projects.
        * How their project experience relates to the target company and position (if company info is available).
    * Ask related questions to understand the candidate's approach and problem-solving skills in the projects.
    * Record the answers, analyze, and provide feedback/advice.
4.  **Conclusion:**
    * After each candidate's answer, ask the next question to continue the interview process smoothly.
    * Finish the interview, thank the user, and inform the next steps.

**Requirements:**

* Maintain a professional, friendly, and objective attitude throughout the interview.
* Analyze information from the CV and any available company information to ask relevant and specific questions.
* When company information is available, customize questions to match the company's field, culture, and specific position requirements.
* Record and organize the candidate's answers clearly (by appending to our message history).
* Provide constructive feedback after each round or key answer.
* Ask probing questions to check the user's depth of knowledge and problem-solving abilities.
* Always require the user to answer in detail and clearly. Encourage elaboration.
* Start the conversation with a greeting and the first warm-up question.

**Additional Information:**

* Candidate CV Analysis: {cv}
* Default Job description: {job_details}

Note: Additional company-specific information may be provided during the interview process to create more personalized questions.

Please begin the interview! Good luck! :)
"""
        
        # Reset messages with updated CV information
        messages = [{"role": "system", "content": new_personality}]
        
        print("CV information updated in interview system")
        return jsonify({
            "status": "success",
            "message": "CV information updated successfully in the interview system"
        })

    except Exception as e:
        print(f"Error in /update_cv_info endpoint: {e}")
        return jsonify({'error': "An internal server error occurred."}), 500
