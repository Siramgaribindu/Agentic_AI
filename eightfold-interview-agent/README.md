# 💼 AI Interview Practice Partner

An interactive, multi-stage AI Mock Interview Simulator built with **Streamlit** and **FastAPI**. This application guides candidates through a structured, professional interview experience spanning introduction, technical deep-dives, and behavioral evaluations, culminating in a comprehensive performance scorecard.

---

## 🚀 Features

*   **Multi-Stage Pipeline:** Guides users dynamically through structured interview phases: `INTRO` ➔ `TECHNICAL_1` ➔ `TECHNICAL_2` ➔ `BEHAVIORAL` ➔ `FEEDBACK`.
*   **Customizable Sessions:** Tailor your experience by choosing your target job role and experience level (Internship, Junior, or Mid-Senior).
*   **Voice Synthesis (TTS):** The AI panel "speaks" questions out loud using native browser Text-to-Speech integration.
*   **Polished UI:** Immersive, scannable dark-mode workspace utilizing custom CSS styling for distinct visual separation between the panel and candidate.
*   **Automated Evaluation:** Generates a complete performance breakdown, scoring matrix, and growth-oriented feedback at the end of the session.

---

## 🛠️ Project Architecture

The application is split into two independent services:
1.  **Frontend (`app.py`):** A Streamlit-based graphical user interface handling chat history, text-to-speech rendering, and configuration states.
2.  **Backend (`main.py`):** A lightweight FastAPI server responding to user conversation logs and evaluating responses.

---

## 📦 Installation & Local Setup

### 1. Clone the Project
Unzip your project files or clone your repository into a local workspace directory.

### 2. Install Dependencies
Ensure you have Python installed. Run the following command to install the required libraries:
```bash
pip install streamlit fastapi uvicorn requests