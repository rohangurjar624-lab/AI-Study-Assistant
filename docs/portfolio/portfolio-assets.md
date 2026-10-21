# Portfolio Assets & Career Deliverables

This document provides ready-to-use resume bullet points, social media launch copy, and portfolio showcase metadata for **AI Study Assistant**.

---

## 1. Resume Bullets (Tailored for Software Engineer & Full-Stack Roles)

- **AI Study Assistant (Full-Stack Web App):** Architected and deployed an end-to-end active recall web application using Flask 3, PostgreSQL, Docker, and the Anthropic Claude API; achieved **90% automated test coverage** across 64 unit and integration tests in GitHub Actions CI/CD.
- **Resilient AI & NLP Architecture:** Engineered a dual study engine with seamless fallback from LLM JSON generation to a deterministic TF-IDF extractive summarizer, guaranteeing 100% uptime regardless of external API quota or latency constraints.
- **Cheat-Proof Assessment & Spaced Repetition:** Implemented safe server-side quiz scoring preventing DOM answer leakage and incorporated the SuperMemo 2 (SM-2) algorithm to dynamically schedule flashcard reviews and calculate daily study streaks.
- **Enterprise Security & Data Isolation:** Enforced multi-tenant isolation with stealth 404 access controls, cryptographic CSRF verification on all POST operations, Werkzeug scrypt hashing, and automated Alembic database migrations.

---

## 2. LinkedIn Post Draft

```markdown
🚀 Excited to unveil my latest project: AI Study Assistant — an intelligent active recall platform built with Python, Flask 3, Docker, and Claude AI!

Students often fall into the "passive learning trap" — reading pages of notes without actively testing recall. I built AI Study Assistant to turn any raw lecture note or PDF into a complete study ecosystem in seconds:

✨ Features:
• 📑 Document Ingestion: Extracts text from plain text or textbook PDFs with automatic scanned-document detection.
• 🧠 Dual AI Engine: Powered by Anthropic's Claude API with an automated silent fallback to an offline TF-IDF NLP engine.
• 🎯 Safe Server-Side Scoring: Fully cheat-proof MCQ quizzes where answers never leak to the client DOM.
• 🔄 SM-2 Spaced Repetition: Algorithmic flashcards that adjust review intervals based on recall difficulty.
• 📊 Diagnostic Dashboard: Live Chart.js analytics tracking score progress, streak counters, and weak-topic diagnostics.

🛠️ Tech Stack: Python 3.12, Flask 3, SQLAlchemy, Alembic, Docker, PostgreSQL, pytest (90% coverage), GitHub Actions CI/CD.

Check out the GitHub repo and live demo:
🔗 Repository: https://github.com/your-username/ai-study-assistant
🌐 Live Demo: https://ai-study-assistant.onrender.com (Demo: demo@example.com / DemoPass123!)

Feedback and code reviews welcome! 💬👇

#Python #Flask #ArtificialIntelligence #EdTech #SoftwareEngineering #WebDevelopment #OpenSource
```

---

## 3. Short Portfolio Website Card

- **Project Title:** AI Study Assistant
- **Tagline:** Intelligent active recall & spaced repetition platform powered by dual-engine AI.
- **2-Line Description:** An end-to-end learning web application that ingests lecture notes and PDFs to instantly generate executive summaries, cheat-proof MCQ quizzes, and SM-2 spaced repetition flashcards.
- **Tech Stack Badges:** `Python 3.12` &bull; `Flask 3` &bull; `SQLAlchemy` &bull; `Anthropic API` &bull; `Docker` &bull; `PostgreSQL` &bull; `Chart.js` &bull; `pytest (90%)`
- **Actions:**
  - View Live Demo &rarr;
  - View Source Code on GitHub &rarr;
  - Read Architecture Case Study &rarr;

---

## 4. Pre-Loaded Demo Account Credentials

- **Email:** `demo@example.com`
- **Password:** `DemoPass123!`
- **Pre-Loaded Study Sets:**
  1. *Biology:* Photosynthesis, Thylakoid light reactions, and the Calvin Cycle.
  2. *Computer Science:* Operating systems process scheduling, Round Robin, deadlocks, and virtual memory paging.
- **Pre-Loaded Records:** 2 completed quiz attempts with detailed score history, and 4 spaced repetition flashcards due for immediate recall review.
- **Security Lock:** Demo account password changes and deletions are strictly blocked at the application controller level to guarantee persistent access for interviewers and evaluators.
