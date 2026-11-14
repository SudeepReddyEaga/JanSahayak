# Multilingual Government Scheme Eligibility Guide (JanSahayak AI)

> **Official Repository:** [https://github.com/SudeepReddyEaga/JanSahayak](https://github.com/SudeepReddyEaga/JanSahayak)  
> **Comprehensive Project Report:** [PROJECT_REPORT.md](file:///d:/Downloads/agenticpro/PROJECT_REPORT.md) &middot; Printable HTML: [PROJECT_REPORT.html](file:///d:/Downloads/agenticpro/PROJECT_REPORT.html)  
> **Course:** CSE476: Agentic AI / Multi-Agent Systems &middot; **Section:** K3E2327  
> **Faculty Supervisor:** Mr. Ravneet Singh (UID: 35120)  
> **Institution:** Lovely School of Computer Science and Engineering, Lovely Professional University, Phagwara  
> **Submitted By:**  
> 1. Sudeep Kumar Reddy Eaga (Reg: 12318529, Roll: 23)  
> 2. Kanithi Naresh Kumar (Reg: 12313053)  
> 3. Seepana Jyothi Swaroop (Reg: 12310991)  

---

## Key Features Implemented

- **6 Specialized Agent Modules (Microsoft Agent Framework `SequentialBuilder`)**:
  1. `ProfileIntakeAgent` (`services/agent_orchestrator_service/agents/profile_intake_agent.py`): Auto-detects language across **12 Indian languages** (`en`, `hi`, `pa`, `te`, `ta`, `bn`, `mr`, `kn`, `gu`, `ml`, `or`, `ur`), normalizes Indic/Urdu digits, extracts demographic/socioeconomic attributes, and writes to shared `UserProfileMemory`.
  2. `SchemeRetrievalAgent` (`scheme_retrieval_agent.py`): Executes **Hybrid BM25 + Dense Vector RAG** with multilingual profile query expansion over 17 seeded government welfare schemes.
  3. `EligibilityRuleAgent` (`eligibility_rule_agent.py`): Applies a **deterministic Strategy-Pattern rule engine** strictly over RAG-retrieved candidates with rule-by-rule audit reasons and boundary checks.
  4. `DocumentChecklistAgent` (`document_checklist_agent.py`): Generates a deduplicated, localized document checklist specifying issuing authorities per eligible scheme.
  5. `GuideManagerAgent` (`guide_manager_agent.py`): Enforces an explicit **`GroundingGate`** check before compiling eligible schemes, reasons, documents, and step-by-step application workflows.
  6. `LanguageReviewerAgent` (`language_reviewer_agent.py`): Audits reply language consistency across all 12 scripts (including Urdu RTL) and ensures **every official scheme name remains intact verbatim**, automatically repairing omissions or label leaks.
- **Voice Input & Speech Read-Aloud across 12 Languages**:
  - Dedicated `voice-speech-service` (`:8004`) exposes BCP-47 speech locale metadata (`en-IN`, `hi-IN`, `pa-IN`, `te-IN`, `ta-IN`, `bn-IN`, `mr-IN`, `kn-IN`, `gu-IN`, `ml-IN`, `or-IN`, `ur-IN`) and sanitizes Markdown replies into browser-safe utterance chunks.
  - `CitizenVoiceController` (`services/frontend_ui/static/voice_controller.js`) progressively integrates Web Speech API STT + TTS with non-blocking fallback so normal text operation is never disturbed.
- **Shared User-Profile Memory**: Every agent reads from and writes to `UserProfileMemory` via Microsoft Agent Framework's `SharedProfileMemoryContextProvider(ContextProvider)`, backed by PostgreSQL + Redis write-through storage.
- **Fast & Accurate Redis Semantic + Exact Cache**: Two-tier cache-aside engine preventing cross-profile collisions while delivering `<5 ms` hits on repeated or paraphrased citizen queries.
- **Microservice Architecture**:
  - `api-gateway` (`:8000`) — REST & SSE Gateway + Cache Audit Telemetry + Voice Proxy
  - `profile-memory-service` (`:8001`) — Shared Citizen Memory & Evaluation Persistence
  - `rag-retrieval-service` (`:8002`) — Scheme Knowledge Base & Hybrid RAG Engine
  - `agent-orchestrator-service` (`:8003`) — Microsoft Agent Framework Sequential Pipeline & Evaluator
  - `voice-speech-service` (`:8004`) — Multilingual Voice Locale Registry & Markdown-to-Speech Sanitizer
  - `frontend-ui` (`:3000`) — Nginx-hosted Interactive SPA (also accessible at `:8000/`)
  - `postgres` (`:5432`) & `redis` (`:6379`)
- **10-Profile Precision & Recall Benchmark**: Automated CO3/CO4 evaluator testing 10 multilingual citizen profiles (including negative controls), reporting Macro/Micro Precision, Recall, F1, Grounding Pass Rate, Language Consistency, and Scheme Name Integrity.

---

## Quick Start with Docker

### Option A: Full Multi-Container Microservice Stack (`docker compose`)
```bash
cp .env.example .env
docker compose up --build
```
- **Interactive Web UI**: http://localhost:3000 (or http://localhost:8000)
- **API Gateway Swagger Docs**: http://localhost:8000/docs
- **Microservices**: `:8001` (Profile Memory), `:8002` (RAG Retrieval), `:8003` (Agent Orchestrator), `:8004` (Voice & Speech)

### Option B: Single Portable All-in-One Docker Image
```bash
docker build -t multilingual-scheme-guide .
docker run -p 8000:8000 multilingual-scheme-guide
```
- **Interactive Web UI & API**: http://localhost:8000

### Option C: Local Python Execution (Zero Docker Setup)
```bash
pip install -r requirements.txt
set ORCHESTRATION_MODE=local_inproc   # export ORCHESTRATION_MODE=local_inproc on Linux/macOS
uvicorn services.api_gateway.main:app --host 0.0.0.0 --port 8000
```

---

## Running Tests & 10-Profile Evaluation

```bash
# Run full unit & integration test suite (including 10-profile benchmark & Redis cache tests)
pytest -v
```

You can also click **"Run 10-Profile Evaluation"** inside the Web UI (**Tab 3: 10-Profile Evaluation**) or call:
```bash
curl -X POST http://localhost:8000/api/v1/evaluate
```

---

## Enabling External LLMs (Optional)

Out of the box, `LLM_PROVIDER=deterministic` uses Microsoft Agent Framework's `FunctionInvocationLayer` + `BaseChatClient` locally with zero API keys required. To route agent reasoning through OpenAI, Gemini, or Ollama, set in `.env`:
```env
LLM_PROVIDER=openai   # or gemini / ollama
OPENAI_API_KEY=sk-...
```
See [`docs/ARCHITECTURE_AND_LLD.md`](docs/ARCHITECTURE_AND_LLD.md) for sequence diagrams, ER schema, and SOLID LLD design patterns.

