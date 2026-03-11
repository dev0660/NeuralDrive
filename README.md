# AI Sales Training Platform

A Django-based conversational AI training platform that simulates dealership sales calls, evaluates rep performance using LLM-based scoring, and stores structured call analytics for coaching and improvement.

## Why I Built This

Sales teams need realistic practice, not static scripts. I built this platform to let dealership reps train against AI-powered customer personas, receive structured feedback on their performance, and review transcript-based coaching insights after each call.

## Current Features

- User authentication and account-based call history
- AI-powered outbound sales practice calls using voice assistants
- Multiple customer personas with separate assistant flows
- Transcript retrieval from Vapi call artifacts
- Automatic transcript parsing and call duration extraction
- LLM-based sales evaluation using a 5-part scoring rubric
- Structured feedback including reasoning and coaching suggestions
- Rep-specific score tracking by assistant/persona
- Admin dashboard for viewing user call activity
- Dealership leaderboard with aggregated performance metrics

## How It Works

1. A salesperson logs into the platform and selects an AI customer persona.
2. The rep places a practice sales call through a Vapi-powered voice assistant.
3. After the call, the platform retrieves the latest matching call and transcript.
4. The transcript is evaluated using an OpenAI model against a custom automotive sales rubric.
5. The system stores:
   - total score
   - rubric category scores
   - reasons for each score
   - coaching suggestions
   - transcript
   - call metadata
6. The rep can review the full transcript, score breakdown, and feedback inside the application.

## System Architecture

1. Sales Rep
2. Django Web App
3. Vapi Voice Assistant
4. Call Transcript + Metadata
5. OpenAI Evaluation Pipeline
6. CallAnalysis Model / Database
7. Score Review, Call History, Leaderboards

## Tech Stack

- **Backend:** Django, Python
- **Database:** Django ORM / relational database
- **AI / LLM:** OpenAI API
- **Voice AI:** Vapi
- **Analytics:** Score aggregation, leaderboard metrics, transcript evaluation
- **Frontend:** Django templates, HTML, CSS

## Technical Highlights

- Integrated third-party voice AI workflows into a Django application
- Built transcript ingestion and parsing logic for post-call analysis
- Designed an LLM-driven scoring workflow with structured JSON outputs
- Persisted rubric-based call evaluations for rep coaching and historical review
- Implemented role-based access patterns for reps and admin views
- Aggregated user and dealership performance metrics for leaderboard analysis

## Current Limitations

- Evaluation currently runs synchronously during refresh flow
- Business logic is still being refactored out of view functions into service modules
- Persona configuration is partially hardcoded
- Analytics outputs are stored primarily as rubric scores rather than richer structured conversation features

## Roadmap

- Move transcript retrieval and evaluation into async background jobs
- Add richer conversation analytics:
  - objection types
  - sentiment shifts
  - closing attempts
  - trust violations
- Introduce configurable persona profiles instead of hardcoded assistants
- Build rep improvement dashboards over time
- Add structured JSON analytics payloads for downstream reporting
- Refactor evaluation logic into service-layer architecture

<img width="1710" height="1020" alt="Screenshot 2026-03-11 at 12 45 29 PM" src="https://github.com/user-attachments/assets/71b0ff25-459b-49ae-aaf0-c4ecaeec4b83" />
<img width="1707" height="1022" alt="Screenshot 2026-03-11 at 12 45 45 PM" src="https://github.com/user-attachments/assets/5cb7e9a3-a571-4efa-8c77-af7dd772d27d" />
<img width="1710" height="1023" alt="Screenshot 2026-03-11 at 12 45 57 PM" src="https://github.com/user-attachments/assets/fe8e6cc3-9c48-4813-9521-f875cd2fbcdf" />
<img width="1710" height="1025" alt="Screenshot 2026-03-11 at 12 46 06 PM" src="https://github.com/user-attachments/assets/a95bf342-5060-4264-a1c0-24cbc145686b" />
<img width="1710" height="1022" alt="Screenshot 2026-03-11 at 12 46 31 PM" src="https://github.com/user-attachments/assets/c811ce37-fa83-48bd-9bb4-e5649efff694" />
<img width="1229" height="968" alt="Screenshot 2026-03-11 at 1 30 16 PM" src="https://github.com/user-attachments/assets/b39a0959-0c75-43e2-ad3c-7c1696e7a93a" />
<img width="1236" height="1008" alt="Screenshot 2026-03-11 at 1 30 27 PM" src="https://github.com/user-attachments/assets/de888adf-9733-419e-b55e-4ab1878ff170" />
