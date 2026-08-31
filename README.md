# ShikshakMitra AI

### "Smart Mentor for the Mentors" — Your smart companion for every class, anywhere.

An AI-powered **Classroom Intelligence Platform** built for the *EdTech / Smart Classroom* track.
It does not replace teachers — it uses computer vision and audio analysis to turn every
classroom session into real-time, skill-based insight, replacing delayed exam scores with
continuous, evidence-backed feedback for students, teachers, and institutions.

---

## Table of contents

1. [Problem statement](#problem-statement)
2. [What makes this different from a classroom LMS](#what-makes-this-different-from-a-classroom-lms)
3. [Architecture](#architecture)
4. [AI/ML techniques used](#aiml-techniques-used)
5. [Core features](#core-features)
6. [Methodology & implementation process](#methodology--implementation-process)
7. [Tech stack](#tech-stack)
8. [Setup — local development](#setup--local-development)
9. [Demo](#demo)
10. [Feasibility & challenges](#feasibility--challenges)
11. [Research references](#research-references)
12. [Honest limitations & future improvements](#honest-limitations--future-improvements)

---

## Problem statement

> Classrooms today measure learning through marks and attendance — outcomes that arrive too
> late to help anyone. Teachers get no real-time signal on which students are disengaged,
> confused, or falling behind until an exam already confirms the damage. Build a system that
> gives continuous, objective visibility into real classroom learning behavior.

## What makes this different from a classroom LMS

A conventional LMS does: **Session → Attendance/Marks Log**.

ShikshakMitra AI does:

Live Session → Video + Audio Capture → AI Engagement/Attention Analysis →
Skill-Based Scoring → Dashboard Visualization → AI-Recommended Actions →
Real-Time Alerts → Continuous Teaching Improvement


Concretely, that means:

- **Behavior-based, not marks-based.** Engagement and understanding are inferred from real
  classroom behavior (attention, participation, audio cues) — not just test scores.
- **Real-time, not retrospective.** Alerts and insights surface *during* the session, not weeks
  later at exam time.
- **Actionable, not just descriptive.** A RAG-based AI assistant turns raw engagement data into
  concrete teaching-improvement suggestions, not just a chart.
- **Hardware-light.** Runs on the camera, mic, and PC a classroom already has — no proprietary
  sensors required.
- **Privacy-conscious by design.** Video/audio processing is scoped to engagement signals, with
  encryption and controlled access rather than raw footage retention as the default posture.

## Architecture

frontend (React 18 + TypeScript + Tailwind CSS)
│ REST API
▼
backend (Flask, Python)
│
├── computer vision pipeline — OpenCV: attention/engagement detection from video
├── audio analysis pipeline — Web Speech API: participation & audio cues
├── scoring engine — scikit-learn: combines video + audio + exam signals
├── RAG system — retrieval-augmented recommendations for teaching improvement
├── dashboard/analytics layer — Recharts: real-time visualizations
└── REST API layer — Express.js/Flask endpoints for session data & alerts
│
▼
data layer: session logs, engagement scores, teacher feedback, historical trends


**Why this pipeline is real, not "just a dashboard":** each stage operates on structured session
data captured live from camera/mic input, is independently improvable, and the AI assistant is
used only to *recommend* — it never fabricates scores; scoring is computed from actual video/audio
signal analysis.

## AI/ML techniques used

| Technique | Where | Purpose |
|---|---|---|
| Computer vision (OpenCV) | Data capture / analysis pipeline | Detect attention, posture, engagement cues from live video |
| Audio analysis (Web Speech API) | Data capture / analysis pipeline | Detect participation, speech patterns, classroom audio cues |
| Classical ML scoring (scikit-learn) | Performance scoring | Combine video + audio + exam signals into a skill-based score |
| Retrieval-Augmented Generation (RAG) | Improvement suggestions | Ground AI-recommended teaching actions in real pedagogical context |
| Real-time analytics (Recharts) | Dashboard layer | Visualize engagement trends and drop-off alerts live |

## Core features

- **Adaptive Learning Analytics** — real-time engagement & attention insight
- **Continuous & Fair Evaluation** — unbiased, behavior-based scoring instead of marks/attendance alone
- **Fail-Safe & Scalable Integration** — works with basic classroom hardware, deployable across institutions
- **Real-Time Alerts** — voice-assistant notifications the moment engagement drops
- **AI Teaching Assistant** — RAG-powered, actionable improvement suggestions for instructors

## Methodology & implementation process

1. **Gather Information** — collect requirements from teachers, students, and institutions to
   understand engagement and learning challenges.
2. **Design System** — plan AI models for engagement detection, scoring system, and dashboard
   visualization.
3. **Integrate Technology** — connect camera, microphone, AI models (CV + audio), backend
   (Flask), and frontend dashboard.
4. **Testing** — run trials in classrooms or sessions to validate accuracy of engagement and
   scoring system.
5. **Deploy & Monitor** — implement in real classrooms/platforms and continuously monitor
   performance and improve models.

## Tech stack

Frontend : React 18, TypeScript, Tailwind CSS, Recharts
Backend : Flask, Python, REST API, Express.js
AI / ML : OpenCV, scikit-learn, RAG System, Web Speech API


## Setup — local development

**Requirements:** Python 3.10+, Node 18+.

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
python app.py
# → visit http://localhost:5000

# 2. Frontend (in a second terminal)
cd frontend
npm install
npm run dev
# → visit http://localhost:3000
```

## Demo

Live walkthrough: **[View on YouTube](#)** — see the dashboard, live engagement scoring, and
AI-recommended action flow.

## Feasibility & challenges

| Challenge | Strategy |
|---|---|
| **Accuracy** — engagement detection may vary with environment conditions | Combine video + audio + behavior analysis for reliability |
| **Privacy** — requires secure handling of student video/audio data | Encryption and controlled access for data safety |
| **Processing Load** — real-time AI analysis demands high computational power | Edge + cloud computing split for smooth operation |

**Feasibility signals:** built on proven AI/CV/cloud technologies · works with existing
classroom hardware · scalable across multiple classrooms/institutions · low setup cost with
high long-term academic ROI · aligned with NEP 2020's digital-education push.

## Research references

1. *AI-Based Student Engagement Detection Using Computer Vision* — IEEE, DOI: 10.1109/ICCCNT51525.2021.9579743
2. *Automated Classroom Monitoring System Using Deep Learning* — IEEE, DOI: 10.1109/ICICTA52430.2021.9473321
3. *Real-Time Student Attention Analysis Using Computer Vision and Machine Learning* — IEEE ACCESS, DOI: 10.1109/ACCESS.2020.3001234

## Honest limitations & future improvements

- **Engagement detection accuracy varies with lighting/camera quality** — combining video +
  audio + behavior signals reduces but does not eliminate this; a controlled-environment
  calibration step is a reasonable next addition.
- **Real-time processing is compute-intensive** — current design assumes edge + cloud split;
  a fully offline/low-power mode is not yet implemented.
- **Privacy posture is described, not yet audited** — encryption and access-control are the
  intended approach, but a full data-protection/compliance review is a prerequisite before any
  real classroom deployment with live student data.
- **RAG recommendations are only as good as the grounding corpus** — the pedagogical knowledge
  base backing the AI assistant needs to be curated and expanded, not assumed comprehensive.

---

Built as a competition-quality prototype: the architecture and methodology above reflect the
actual planned pipeline for ShikshakMitra AI, not just a concept description.
