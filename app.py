# app.py
import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError # Thêm các loại lỗi cụ thể
from flask import Flask, render_template, request, jsonify, send_file, abort
from flask_cors import CORS
from pydub import AudioSegment  # Thêm thư viện này để chuyển đổi định dạng âm thanh
from pydub.utils import which

AudioSegment.converter = which("ffmpeg")  # Đảm bảo `pydub` sử dụng đúng `ffmpeg`

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": {"https://localhost:5173", "https://192.168.1.15:5173", "https://192.168.1.15:5000"}}}, supports_credentials=True)  # Cho phép tất cả các nguồn gốc (origins) truy cập vào API
# --- Load Biến Môi Trường ---
load_dotenv()
api_key = os.getenv("OPEN_AI_KEY")
# --- Khởi Tạo Flask App ---
# Sử dụng thư mục templates và static mặc định


# --- Khởi Tạo OpenAI Client ---
client = OpenAI(api_key=api_key)

# --- Dữ Liệu CV và Job Details ---
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
personality = f"""
  You are a chatbot acting as a professional interviewer for a company (the name isn't explicitly mentioned, let's assume Step Up based on job_details).
  **Context:**

  * You are provided with the candidate's CV and the job description of the position being recruited.
  * Your task is to analyze the CV and job description to ask relevant interview questions, assessing the candidate's skills and experience against the job requirements.

  **Interview Process:**

  1.  **Round 1: Personal Introduction (warm-up)**
      * Ask an open-ended question for the candidate to introduce themselves (not directly related to professional skills).
          * Example: "Could you share a bit about your hobbies or extracurricular activities?"
      * Ask 1-2 follow-up questions to understand the candidate's personality and motivation better.
      * Record the answers and provide brief, encouraging feedback.
      * Analyze the answer, make comments, and give advice to the user to improve their answer (if needed).
  2.  **Round 2: Basic Professional Knowledge**
      * Based on the job description, ask 2 questions about basic professional knowledge related to the position (e.g., AI/ML concepts, LLMs, MLOps).
      * Ask 1-2 follow-up questions for each main question to test the candidate's depth of understanding.
      * Record the answers.
      * Analyze the answer, explain again if the user answer is wrong, and give advice to the user to improve their answer.
  3.  **Round 3: Project Experience**
      * Ask the candidate to describe in detail the projects they have participated in (based on the CV).
      * Ask deeper questions to understand:
          * What were the candidate's roles in the projects?
          * Which teams did the candidate work with?
          * Detailed analysis of the technical expertise used in the projects (e.g., specific models like Faster R-CNN, DeepQLearning, fine-tuning LLMs if mentioned).
      * Ask related questions to understand the candidate's approach and problem-solving skills in the projects.
      * Record the answers, analyze, and provide feedback/advice.
  4.  **Conclusion:**
      * After each candidate's answer, ask the next question to continue the interview process smoothly.
      * Finish the interview, thank the user, and inform the next steps (e.g., "Thank you for your time. We will review your application and get back to you soon.").

  **Requirements:**

  * Maintain a professional, friendly, and objective attitude throughout the interview.
  * Analyze information from the CV and job description to ask relevant and specific questions.
  * Record and organize the candidate's answers clearly (by appending to our message history).
  * Provide constructive feedback after each round or key answer.
  * Ask probing questions to check the user's depth of knowledge and problem-solving abilities.
    * Always require the user to answer in detail and clearly. Encourage elaboration.
    * Start the conversation with a greeting and the first warm-up question.

**Language Requirement:**
* All outputs, questions, analysis, and feedback **must be written in English** regardless of the user's language.


  **Additional Information:**

  * Candidate CV: {cv}
  * Job description: {job_details}

  Please begin the interview! Good luck! :)
"""

# --- Lịch Sử Hội Thoại ---
# !!! Cảnh báo: Biến global, không phù hợp cho nhiều người dùng đồng thời.
messages = [{"role": "system", "content": personality}]

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

def generate_audio(text, filename="speech_output.mp3"):
    """Chuyển văn bản thành audio, xử lý lỗi cơ bản."""
    # !!! Lưu ý: Giới hạn độ dài văn bản của API TTS vẫn áp dụng.
    # Cách xử lý chunking phức tạp hơn (ghép file) không được triển khai ở đây.
    speech_file_path = Path(__file__).parent / filename
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova", # Bạn có thể thử các giọng khác: alloy, echo, fable, onyx, shimmer
            input=text
        )
        response.stream_to_file(speech_file_path)
        print(f"Audio successfully generated: {speech_file_path}")
        return speech_file_path
    except APIError as e:
        print(f"OpenAI API Error during TTS generation: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during TTS generation: {e}")
        return None

def generate_text():
    """Tạo phản hồi text từ OpenAI, cập nhật lịch sử messages."""
    global messages # Sử dụng biến global (cần cẩn thận)
    try:
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
    """Trang chủ."""
    return render_template('index.html')

@app.route('/chat/text')
def text_chat():
    """Route cho giao diện chat text (trỏ về index.html)."""
    return render_template('index.html')

@app.route('/chat/speech')
def speech_chat():
    """Route cho giao diện chat speech (trỏ về index.html)."""
    return render_template('index.html')

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


@app.route('/process_audio', methods=['POST'])
def process_audio():
    """Nhận file audio, chuyển thành text, gửi đến OpenAI, tạo audio phản hồi."""
    global messages
    audio_file = None
    temp_audio_path = None
    converted_audio_path = None  # Đường dẫn file sau khi chuyển đổi
    response_audio_path = None

    try:
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

        # Chuyển đổi audio sang text (Speech-to-Text)
        try:
            with open(converted_audio_path, "rb") as audio_data:
                transcript_response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_data
                )
            transcript = transcript_response.text
            print(f"Transcription successful: {transcript}")
        except APIError as e:
            print(f"OpenAI API Error during transcription: {e}")
            return jsonify({"error": "Failed to transcribe audio."}), 500
        except Exception as e:
            print(f"An unexpected error occurred during transcription: {e}")
            return jsonify({"error": "Audio processing failed."}), 500

        # Thêm transcript (user message) vào history
        messages.append({"role": "user", "content": transcript})
        print("Transcript added to history as user message.")

        # Gọi OpenAI để lấy phản hồi text (hàm này đã tự thêm bot reply vào messages)
        bot_response_text = generate_text()

        # Tạo audio từ phản hồi text (Text-to-Speech)
        response_audio_path = generate_audio(bot_response_text)
        if not response_audio_path:
            # Nếu tạo audio lỗi, vẫn trả về text
            print("Failed to generate response audio, returning text reply.")
            save_history_to_json(messages)  # Lưu history trước khi trả về
            return jsonify({'reply_text': bot_response_text, 'error': 'Could not generate audio response.'}), 500

        # Lưu lịch sử (tùy chọn)
        save_history_to_json(messages)

        # Gửi file audio phản hồi về client
        return send_file(response_audio_path, as_attachment=True, download_name='response.mp3', mimetype='audio/mpeg')

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

@app.route('/process_text', methods=['POST'])
def process_text():
    global messages

    user_message = request.json['user_message']
    user_session = request.json['sessionid']
    print("user_message:", user_message)
    print("user_session:", user_session)

    messages.append({"role": "user", "content": user_message})
    print("Transcript added to history as user message.")

    # Sinh phản hồi từ bot
    bot_response_text = generate_text()
    print("bot_response_text:", bot_response_text)

    # Gửi POST request đến server digital human
    try:
        response = requests.post(
            "https://192.168.1.15:8010/human",
            json={
                "text": bot_response_text,
                "type": "echo",
                "interrupt": True,
                "sessionid": user_session
            },
            verify=False  # ⚠️ Tắt SSL verification nếu là local self-signed cert
        )
        print("Sent to digital human:", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print("Error sending to digital human:", e)
        return jsonify({"success": False, "error": str(e)}), 500

    return jsonify({
        "success": True,
        "bot_response": bot_response_text
    })


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
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=('ssl/cert.pem', 'ssl/key.pem')) # Chạy trên tất cả interface, port 5000