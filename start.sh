#!/bin/bash

# Start the frontend
(npm run dev) &

# Start the main backend
(python app.py) &

# Start the livetalking backend
(cd livetalking && python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1)
