# ✍️ AirScript – Real-Time Gesture-Based Virtual Writing System

AirScript is a real-time computer vision project that allows users to write in the air using hand gestures. The system tracks hand movements via a webcam and converts them into digital writing on the screen.

---

## 🚀 Features

- ✋ Real-time hand tracking using webcam
- 🖊️ Air writing with finger gestures
- 🧠 Gesture-based drawing/interaction system
- 📌 Smooth and responsive tracking
- 🖥️ Works without any special hardware (only webcam required)

---

## 🛠️ Tech Stack

- Python 🐍
- OpenCV 👁️
- MediaPipe ✋
- NumPy 🔢

---

## 📁 Project Structure


Airscript/
│
├── main.py # Main application file
├── hand_tracker.py # Hand detection & tracking module
├── utils.py # Helper functions
├── requirements.txt # Dependencies
└── README.md


---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Airscript.git
cd Airscript
2. Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate   # Windows
3. Install dependencies
pip install -r requirements.txt
▶️ Run the Project
python main.py
📌 How It Works
Webcam captures live video feed
MediaPipe detects hand landmarks
Index finger movement is tracked
Movements are drawn on a virtual canvas
Output is displayed in real time
💡 Future Improvements
Add text recognition (OCR)
Mobile version support
Adding color wheel
Multiple color pen support
Eraser gesture
Cloud saving of drawings
