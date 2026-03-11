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

Sales Rep
   ↓
Django Web App
   ↓
Vapi Voice Assistant
   ↓
Call Transcript + Metadata
   ↓
OpenAI Evaluation Pipeline
   ↓
CallAnalysis Model / Database
   ↓
Score Review, Call History, Leaderboards

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
