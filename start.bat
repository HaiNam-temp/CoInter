@echo off

echo Starting frontend...
start "Frontend" cmd /c "npm run dev"

echo Starting main backend...
start "Main Backend" cmd /c "python app.py"

echo Starting livetalking backend...
start "Livetalking Backend" cmd /c "cd livetalking && python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1"
