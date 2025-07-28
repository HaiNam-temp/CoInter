# CoInter

CoInter is a web-based platform designed for conducting remote interviews. It provides a real-time communication interface with video and audio capabilities, allowing for a seamless interview experience.

## Key Features

*   **User Authentication:** Secure registration and login system for users.
*   **Real-time Video/Audio:** High-quality, real-time video and audio communication for interviews.
*   **Interview Dashboard:** A centralized dashboard to manage and schedule interviews.
*   **Screen Sharing:** Share your screen for presentations or technical demonstrations.
*   **Interview Ratings:** (Potential Feature) A system for rating and providing feedback on interviews.

## Tech Stack

*   **Frontend:**
    *   React
    *   TypeScript
    *   Vite
    *   Tailwind CSS
*   **Backend:**
    *   Python
    *   Flask (or a similar Python web framework)
    *   WebRTC for real-time communication

## Getting Started

### Prerequisites

*   Node.js and npm
*   Python 3

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/e4glevlr/CoInter
    git checkout fe
    cd CoInter
    ```

2.  **Frontend Setup:**
    ```bash
    npm install
    ```

3.  **Backend Setup:**

    *   **Create a Conda environment:**
        ```bash
        conda create -n nerfstream python=3.10
        conda activate nerfstream
        ```

    *   **Install PyTorch:**
        *(Note: The following command is for CUDA 11.3. If you have a different CUDA version, please refer to the [PyTorch website](https://pytorch.org/get-started/previous-versions/) for the correct command.)*
        ```bash
        conda install pytorch==1.12.1 torchvision==0.13.1 cudatoolkit=11.3 -c pytorch
        ```

    *   **Install other dependencies:**
        ```bash
        pip install -r livetalking/requirements.txt
        ```

    *   **Download Models:**
        Download the necessary models from one of the following links:
        *   [Quark Cloud Disk](https://pan.quark.cn/s/83a750323ef0)
        *   [Google Drive](https://drive.google.com/drive/folders/1FOC_MD6wdogyyX_7V1d4NDIO7P9NlSAJ?usp=sharing)

        Then:
        1.  Copy `wav2lip256.pth` to the `livetalking/models/` directory and rename it to `wav2lip.pth`.
        2.  Extract `wav2lip256_avatar1.tar.gz` and copy the entire extracted folder to the `livetalking/data/avatars/` directory.

### Running the Project

To run the project, you can use the provided scripts. These scripts will start the frontend and backend servers.

**For Windows:**

```bash
start.bat
```

**For Linux/macOS:**

```bash
./start.sh
```

This will start:
- The frontend development server.
- The main backend server.
- The livetalking backend server.

## Project Structure

```
.
├── src/                      # Frontend source code
│   ├── components/           # React components
│   ├── pages/                # Page components
│   ├── store/                # State management
│   └── main.tsx              # Main application entry point
├── livetalking/              # Backend source code for real-time communication
│   ├── app.py                # Main backend application file
│   └── webrtc.py             # WebRTC handling
├── public/                   # Public assets
├── package.json              # Frontend dependencies and scripts
├── app.py                    # Main backend application file
└── README.md                 # This file
```
