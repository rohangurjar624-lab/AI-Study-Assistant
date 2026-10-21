# Engineering Case Study: AI Study Assistant

**Role:** Full-Stack Software Engineer & AI System Architect  
**Domain:** Educational Technology, AI Synthesis & Active Recall  
**Status:** Production Ready (v1.0.0) &bull; 90% Test Coverage &bull; CI/CD Green  

---

## 1. Problem Statement
Modern students and researchers are routinely overwhelmed by vast volumes of passive reading materials: textbook PDFs, lecture transcripts, and unstructured notes. Traditional study workflows suffer from two fundamental bottlenecks:
1. **Passive Learning Trap:** Merely re-reading or highlighting notes produces the illusion of competence without building durable neural recall pathways.
2. **High Friction in Material Creation:** Manually writing balanced multiple-choice questions (MCQs), distilling concise summaries, and organizing spaced-repetition schedules takes hours of tedious manual effort, leading to student burnout.

---

## 2. The Solution
**AI Study Assistant** is a web-based educational platform that ingests unstructured raw notes and text-based PDFs and automates the creation of an end-to-end active recall ecosystem. In seconds, the application extracts:
- An **Executive Summary** capturing the foundational thesis of the text.
- Core **Keywords and Definitions** for rapid indexing.
- Interactive, **Cheat-Proof MCQ Quizzes** scored securely on the server.
- **Spaced Repetition Flashcards** governed by the proven SuperMemo 2 (SM-2) algorithm.
- Real-time **Analytics & Weak-Topic Diagnostics** to direct study focus where it is needed most.

---

## 3. Key Features
- **Document Ingestion Engine:** Seamless text extraction supporting raw copy-paste and `.txt` / `.pdf` uploads up to 5 MB, with proactive scanned-document validation.
- **Dual Study Engine with Automatic Fallback:** Powered primarily by the Anthropic Claude API (`claude-3-5-sonnet-20241022`) for high-order reasoning, with a zero-configuration deterministic offline NLP engine (TF-IDF sentence ranking and keyword extraction) if the API key is absent, times out, or errors.
- **Server-Side Safe Scoring:** Question answers and explanations are decoupled entirely from the client DOM during quiz taking to guarantee test integrity.
- **Adaptive SM-2 Spaced Repetition:** Calculates dynamic review intervals and ease factors based on 6 recall confidence tiers (0 to 5), updating daily study streaks.
- **Diagnostic Dashboard:** Visual progress analytics rendered via Chart.js, plotting score progression over time, average performance per note, and lowest-accuracy weak topic warnings.
- **Strict Data Isolation & Security:** Full multi-tenant data segregation (every route taking an entity ID verifies ownership and returns a stealth 404 on violation to prevent object enumeration).

---

## 4. Tech Stack & Architectural Decisions

| Layer / Concern | Technology | Engineering Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.12 / 3.13 | High developer velocity, rich NLP ecosystem, standard enterprise backing. |
| **Web Framework** | Flask 3.1 | Micro-framework offering minimal overhead, explicit blueprint modularity, and app factory scalability without framework bloat. |
| **ORM & Migrations**| SQLAlchemy 2.0 / Flask-Migrate (Alembic) | Robust relational modeling, strict foreign key constraints with `ON DELETE CASCADE`, and database-agnostic schema migrations. |
| **Persistence** | SQLite (Dev/Test) / PostgreSQL (Prod) | In-memory zero-latency isolation during automated unit testing; high-concurrency ACID guarantees in production. |
| **Authentication** | Flask-Login + Werkzeug | Battle-tested scrypt password hashing, session management with `HttpOnly`, `SameSite=Lax`, and secure cookies. |
| **Form & CSRF** | Flask-WTF + WTForms + email-validator | Comprehensive input validation, length bounds enforcement, and cryptographic CSRF token verification across all state-mutating requests. |
| **PDF Extraction**| pypdf 6.2 | Pure-Python PDF parser eliminating C-library binary dependency headaches during deployment. |
| **Primary LLM** | Anthropic Claude API | Exceptional instruction following, native JSON schema conformance, and nuanced educational explanations. |
| **Offline NLP** | Pure-Python TF-IDF & Sentence Scorer | Ultra-fast, zero-network fallback ensuring uninterrupted platform functionality even offline. |
| **Rate Limiting** | Flask-Limiter | Protection of compute-intensive routes (5/min registration, 10/min login, 10/hour AI generation per user). |
| **Testing & CI** | pytest + pytest-cov + GitHub Actions | 64 comprehensive unit/integration test suites achieving 90% total test coverage and 91% coverage across services. |
| **Deployment** | Docker + Gunicorn + Render | Multi-stage slim Docker image, non-root user security, gunicorn WSGI concurrency. |

---

## 5. Architectural Overview

```
                      [ User Browser / Mobile Client ]
                                     |
                                     v
                       [ Security & Reverse Proxy ]
                   (Rate Limiting, CSRF, Security Headers)
                                     |
                                     v
                  +-------------------------------------+
                  |       Flask 3 Application Factory   |
                  +-------------------------------------+
                                     |
        +-------------+-------------+-------------+-------------+
        |             |             |             |             |
        v             v             v             v             v
   [ Auth BP ]   [ Notes BP ]  [ Quiz BP ]   [ Cards BP ]  [ Dash BP ]
        |             |             |             |             |
        +-------------+------+------+-------------+-------------+
                             |
                             v
               +----------------------------+
               |       Services Layer       |
               +----------------------------+
               |  • extract.py (PDF/TXT)    |
               |  • llm.py (Claude API)     |
               |  • nlp.py (TF-IDF Fallback)|
               |  • srs.py (SM-2 Algorithm) |
               +----------------------------+
                             |
                             v
               +----------------------------+
               |  Relational Database Layer |
               | (SQLite Dev / Postgres Prod|
               +----------------------------+
```

---

## 6. Key Engineering Challenges & Solutions

### Challenge 1: Preventing Client-Side Quiz Cheating
- **Problem:** Many student-focused apps bundle correct answers in hidden HTML fields, data attributes, or JSON scripts, enabling students to inspect element or view DOM source to identify answers.
- **Solution:** Designed a strict two-stage quiz lifecycle. During the `GET /quiz/<id>` request, a sanitized view model is projected omitting `correct_index` and `explanation`. When the student submits (`POST /quiz/<id>`), option indices are checked purely on the server against the database. Results are persisted to `Attempt` and `AttemptAnswer` records, and the user is redirected via Post/Redirect/Get to `/quiz/attempt/<id>`.

### Challenge 2: Graceful LLM Degradation & Schema Conformance
- **Problem:** External AI APIs can suffer network timeouts, invalid JSON generation, or rate quotas.
- **Solution:** Architected a unified study engine interface (`summarize`, `extract_keywords`, `generate_quiz`, `generate_flashcards`). Implemented a 20-second timeout, strict response schema parsing, and a single automated retry loop. If Anthropic is unavailable or unconfigured, the system silently and instantaneously falls back to `nlp.py` without user-facing disruption, tagging `engine_used='offline'` on the quiz.

### Challenge 3: Multi-Tenant Data Leakage & Existence Probing
- **Problem:** Malicious users could probe sequential integer IDs (e.g., `/notes/42`) to determine if notes exist or access other students' records.
- **Solution:** Enforced an application-wide ownership policy. Every route querying an entity by `<id>` filters by both entity ID and `current_user.id`. If a record is not owned by the active session, the app returns HTTP 404 (Not Found) rather than 403 (Forbidden), completely eliminating existence enumeration.

### Challenge 4: Corrupt & Scanned PDF Handling
- **Problem:** PDFs uploaded by students often contain scanned image pages without OCR text layers, causing silent failures or empty note syntheses.
- **Solution:** Developed an extraction pipeline in `services/extract.py`. After PDF page processing, text length is strictly validated. If zero extractable text is detected, a custom `ScannedPDFError` is caught and surfaces an actionable notice: *"This PDF looks scanned; please upload a text-based PDF or paste the text."*

---

## 7. Results & Metrics
- **Test Coverage:** **90% overall coverage** and **91% on `app/services/`**, verified by pytest-cov.
- **Test Suite:** **64 automated tests** passing in under 25 seconds covering auth, validation, isolation, scoring, algorithms, and error responses.
- **Security:** CSRF on all mutation forms, `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, CSP restricting inline executions to trusted CDNs, and zero leaked credentials.
- **Performance:** Sub-100ms response time on local requests; containerized production build under 180 MB.

---

## 8. What I Would Improve Next
1. **Asynchronous Task Queue (Celery / Redis):** Offload long document ingestion and LLM calls to background worker pools with WebSocket push notifications.
2. **Client-Side OCR (Tesseract / PDF2Image):** Add optical character recognition to handle photographed textbook pages and handwritten notes.
3. **Export Formats:** Enable one-click export of generated quizzes and summaries into Anki deck packages (`.apkg`) and formatted Markdown.
