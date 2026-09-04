# Project TicShield (formerly VoiceFlow / VoxNav)
### Target Track: Inclusive Innovation | Hackathon: `>.hack();_'26`

---

## 1. Executive Summary & Context

- **Event**: `>.hack();_'26`
- **Track**: **Inclusive Innovation**
- **Current Status**: **Selected** (Moving from ideation/submission into build & demo phase).
- **Team**:
  - **GSK (Ganesh S)**: Backend orchestration, FastAPI, WebSockets, LLM inference pipeline, system integration.
  - **Gopika**: Acoustic ML classifier, audio feature extraction, tic signature detection.
  - **Yazeen & Adithyan**: Client interface (Android / Web interface), audio capture/streaming, UX & demo pitch presentation.
- **Repository**: `VoxNav` (repurposed for the new direction).
- **Core Pivot**: Transitioned from generic voice navigation for low-vision users to an empathetic, novel assistive technology: **a real-time symptom-aware communication buffer for individuals with Tourette Syndrome and vocal tics.**

---

## 2. The Decision Journey & Competitive Analysis

During our strategic pivot discussions, we evaluated four distinct neuro/psychological conditions against our existing technical stack (**Audio Capture + Groq Whisper + Llama 3 + ChromaDB + Acoustic Classifier**).

### Evaluated Alternatives & Why They Were Rejected:

1. **Alzheimer's Memory / Context Companion**
   - *The Concept*: An ambient assistant answering repeated questions using ChromaDB RAG.
   - *Why Rejected*: **Extremely saturated hackathon cliché.**
     - *Memory Mate*: Hackathon project running Whisper + GPT-4o-mini answering repeated senior questions.
     - *Almond*: Android companion using "therapeutic fibbing" via RAG.
     - *Lumi*: Hackathon project with fine-tuned model + persistent ChromaDB memory.
     - *NeuroNest & KindredMind*: Existing voice journaling/reminders and voice-cloning companions.
     - *Verdict*: Judges will recognize this pattern immediately; zero novelty points.

2. **Acute OCD Compulsion Interrupt & Delay Logger**
   - *The Concept*: Voice-triggered compulsive urge logging and evidence-based ERP delay nudges.
   - *Why Rejected*: **Crowded by funded startups and mature app store products.**
     - *nOCD*: Raised $1M+ seed, dominant clinical/ERP platform.
     - *ocd.app*: 150k+ active users covering OCD/CBT.
     - *OCD SensAI & ObsessLess*: Already provide AI companion ERP coaching and delay tracking.
     - *Patterns*: Open-source ERP app featuring the exact "compulsion delay" mechanism.
     - *Verdict*: High barrier to novelty; hard to stand out against commercial products.

3. **PTSD Grounding Companion**
   - *The Concept*: Stress marker detection with guided de-escalation.
   - *Why Rejected*: Truly detecting PTSD episodes requires biometric sensors (wearables, galvanic skin response, heart rate variability). Without hardware, it reduces to a generic scripted meditation chatbot.

---

### Why Tourette's Syndrome Won Decisively:

- **Total White Space / Pure Novelty**:
  - Existing tech is either **hardware-only safety monitors** (NIH research wristband monitoring sweat/movement), **clinical video diagnostic tools** (Uni Lübeck), or **passive daily habit logs** (TicTracker).
  - **Zero tools exist for real-time, in-conversation vocal tic detection and communication smoothing.**
- **High Empathy & Real Impact**: Individuals with vocal tics (coprolalia, palilalia, involuntary barking, coughing, or phrase repetition) experience profound anxiety during remote job interviews, meetings, and presentations.
- **Perfect Stack Alignment**: Reuses our low-latency voice pipeline (Whisper + Llama 3) combined with Gopika’s acoustic classifier and ChromaDB personal tic profiling without requiring any external hardware.

---

## 3. Product Specification: What We Are Building

### Product Name: **TicShield** *(working title: VoxNav / VoiceFlow)*
**"An in-flight, dignity-first communication buffer for vocal tics."**

### Core Capabilities:
1. **Dual-Stage Tic Detection**:
   - **Stage 1 (Acoustic Anomaly)**: Fast ML classifier (Gopika) checks raw audio frames for explosive vocal outbursts, repetitive clicking, throat-clearing, or abnormal pitch/energy spikes in <50ms.
   - **Stage 2 (Semantic Outlier Detection)**: Groq Whisper transcribes rapid speech chunks; Llama 3 evaluates whether an utterance fits conversational context or is an involuntary intrusion (e.g., sudden swear words, unrelated outbursts, or loop repetitions).
2. **Live Caption Smoothing**:
   - For video calls (Zoom/Meet/Discord), generates real-time sanitized and smoothed captions that reflect the speaker's true intent, suppressing involuntary vocal tics.
3. **Audio Ducking / Suppression (The "Buffer" Mode)**:
   - For virtual meetings, automatically ducks or mutes the audio track for the brief duration of the detected acoustic tic, or replaces it with ambient room tone to prevent interruption.
4. **Personalized Tic Memory Bank (ChromaDB)**:
   - Users train the system on their specific tics (their common trigger words, vocalizations, or repetition patterns), drastically cutting down false positives.

---

## 4. System Architecture & Tech Stack

```
[ User Microphone (Android / Web App) ]
                   │
                   ▼ (Low-Latency 16kHz PCM Stream / WebSockets)
       [ FastAPI Streaming Gateway ]
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
 [ Layer 1: Acoustic ]    [ Layer 2: Fast ASR ]
 [ Classifier (Gopika) ]  [ Groq Whisper-large-v3 ]
 (MFCC/Pitch/Spikes)      (~150ms Latency)
       │                       │
       └───────────┬───────────┘
                   ▼
       [ Layer 3: Semantic Reconstruction ]
       [ Llama 3 70B/8B on Groq ]
       - Context-aware intent extraction
       - Tic suppression & smoothing
                   ▲
                   │ RAG Personalization
       [ Layer 4: ChromaDB Tic Profile Store ]
       (User-specific tic patterns & history)
                   │
                   ▼
  [ Real-Time Output Streaming Engine ]
   ├── Low-Latency Smoothed Captions (WebSockets)
   └── Audio Buffer State (Duck / Mute / Pass-through)
```

### Detailed Tech Stack:
- **Mobile/Client Layer**: Android App (Kotlin/Jetpack Compose) or Next.js/React Web Audio Dashboard with WebSockets.
- **Backend API**: FastAPI (Python 3.11+), Uvicorn, Asyncio, WebSockets.
- **Acoustic Layer**: Librosa, PyTorch/ONNX, Scikit-learn (Feature extraction: MFCCs, Zero Crossing Rate, Spectral Centroid, Energy RMS).
- **Fast ASR**: Groq API with `whisper-large-v3` (sub-200ms turnaround).
- **Semantic Understanding**: Groq API with `llama-3.1-70b-versatile` / `llama-3.1-8b-instant`.
- **Personalized Memory**: ChromaDB (stores vector embeddings of user-specific confirmed tics vs baseline speech).

---

## 5. Team Roles & Work Breakdown

| Member | Primary Responsibility | Hackathon Deliverables |
|---|---|---|
| **GSK (Lead)** | Backend & AI Orchestration | FastAPI streaming server, Groq Whisper + Llama 3 pipeline, ChromaDB RAG integration, WebSocket sync. |
| **Gopika** | Acoustic ML Classifier | Audio preprocessing script, acoustic feature extraction (MFCC/pitch), tic classification model, synthetic tic audio test set. |
| **Yazeen** | Client App / Audio Streamer | Android/Web audio recorder, low-latency PCM streaming to WebSocket, clean UI with live dual-transcript (Raw vs Smoothed). |
| **Adithyan** | UX, Integration & Pitch | Live demo scenario design, UI/UX polish (privacy controls, user dignity toggle), pitch deck, competitive novelty presentation. |

---

## 6. 36-Hour Hackathon Execution Roadmap

### Phase 1: Hours 0 – 12 (Core Pipelines & Feasibility)
- [ ] **Backend**: Set up FastAPI WebSocket endpoint receiving audio chunks.
- [ ] **Groq Integration**: Connect Groq Whisper-v3 for real-time chunk transcription.
- [ ] **Acoustic Model**: Gopika builds baseline classifier for abrupt acoustic tics (volume spikes, rapid clicks, isolated phonations).
- [ ] **Frontend**: Yazeen sets up audio capture streaming 16kHz audio via WebSocket.

### Phase 2: Hours 12 – 24 (Fusion & Smoothing Engine)
- [ ] **Semantic Filter**: Implement Llama 3 prompt pipeline to detect contextual incongruity and reconstruct intended sentences.
- [ ] **ChromaDB**: Integrate ChromaDB to load user-specific tic profiles and calibrate thresholds.
- [ ] **Fusion Layer**: Combine acoustic probability score with semantic perplexity score to trigger tic flags.
- [ ] **Client UI**: Live split-view demo interface:
  - Left: *Raw Audio Stream & Transcribed Words (showing raw tics)*.
  - Right: *TicShield Dignity Feed (cleaned, intent-preserved live stream)*.

### Phase 3: Hours 24 – 36 (Polish, Edge Cases & Judge Demo)
- [ ] **Latency Optimization**: Ensure end-to-end latency stays under 400ms for captions.
- [ ] **Edge Cases**: Prevent over-censoring normal speech; add user sensitivity slider.
- [ ] **Live Demo Rehearsal**: Script a realistic presentation with simulated/recorded vocal tics to demonstrate seamless real-time correction.
- [ ] **Pitch Deck**: Highlight the Inclusive Innovation track angle: Dignity, Empathy, Novelty over saturated Alzheimer's/OCD apps.

---

## 7. Judge Pitch: The Winning Narrative

1. **The Hook**: "Imagine having an important job interview or university presentation, but your vocal tics interrupt your sentences. Today, you are forced to apologize, endure awkward silence, or stay muted."
2. **The Innovation**: "Current medical tech monitors tics after the fact. We built the world's first **real-time, in-conversation communication buffer** that preserves the speaker's dignity without altering their true intent."
3. **The Tech Depth**: "Not just another generic LLM wrapper. We combine sub-50ms acoustic classification with sub-200ms semantic inference on Groq, backed by personal vector profiling with ChromaDB."
