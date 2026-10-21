# 60–90 Second Product Demo Walkthrough & Video Script

This script outlines the exact user flow, camera shots, voiceover cues, and click sequences for recording the 60-to-90-second portfolio demo video / GIF.

---

## Video Specifications
- **Duration:** 75 Seconds (Target: 60–90s)
- **Resolution:** 1920×1080 (16:9 Desktop) or 1080×1920 (Mobile/Shorts)
- **Format:** MP4 (H.264 video codec, AAC audio) + GIF loop for GitHub README
- **Recommended Tools:** OBS Studio, Loom, or Screen Studio

---

## Shot-by-Shot Timeline

| Time | Scene | On-Screen Action | Voiceover / Text Overlay |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:10** | **Landing Page** | Cursor moves across the sleek dark theme hero section. Highlights the 3-step "How It Works" strip and clicks **"Sign In with Demo"**. | *"Welcome to AI Study Assistant — an intelligent platform that turns passive study reading into active recall in seconds."* |
| **00:10 - 00:20** | **Sign In & Dashboard** | Clicks Sign In using pre-filled demo credentials (`demo@example.com`). Instant redirect to `/dashboard`. Cursor scrolls over the 5 stat cards (4-day streak, 86.4% avg score) and dynamic Chart.js visualizations. | *"Logging into the dashboard, students immediately see their daily study streak, historical test scores, and priority weak-topic analytics."* |
| **00:20 - 00:35** | **Note Ingestion & AI Synthesis** | Clicks **"New Note"**. Pastes sample biology notes on photosynthesis. Clicks **"Save & Synthesize"**. Button displays `"Analyzing notes with AI..."`. Instant redirect to the generated note page displaying the **Executive Summary** and **Key Terminology pills**. | *"Students paste raw lecture notes or upload a PDF. Our dual-engine architecture instantly synthesizes an executive summary and extracts key terminology."* |
| **00:35 - 00:50** | **Cheat-Proof Quiz Taking** | Clicks **"Generate Quiz (5 Questions)"**. Lands on `/quiz/<id>` with active elapsed timer ticker. Cursor selects answers to 4 questions, leaving one blank. Clicks **"Submit Quiz"**. | *"With one click, the system generates interactive multiple-choice questions. Answers are never exposed in the client HTML, guaranteeing total test integrity."* |
| **00:50 - 01:05** | **Safe Scoring & Results** | Lands on `/quiz/attempt/<id>`. Displays 80% score banner. Scrolls down through question breakdown showing green checkmarks, red missed answers, correct answers, and context explanations. | *"The server evaluates answers safely, storing detailed attempt history and displaying explanations for every question."* |
| **01:05 - 01:20** | **SM-2 Spaced Repetition Review** | Navigates to `/flashcards/review`. Displays "RuBisCO" card. Presses **Space** to reveal the definition. Clicks rating button **"5: Easy"** (or presses key `5`). Card slides to the next due item; study streak updates. | *"Finally, the SuperMemo 2 algorithm schedules flashcard reviews based on your recall quality, ensuring concepts stay locked in long-term memory."* |
| **01:20 - 01:25** | **Closing CTA** | Returns to the dashboard showing the updated score progression graph and celebratory banner. | *"Built with Flask 3, Docker, and Claude AI. Clone the repository and try it today!"* |
