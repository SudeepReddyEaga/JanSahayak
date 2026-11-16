---
marp: true
theme: default
paginate: true
header: 'JanSahayak: Multilingual Government Scheme Eligibility Guide | LPU CSE476'
footer: 'Discipline of CSE/IT · Lovely Professional University'
style: |
  section {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: #f8fafc;
    color: #0f172a;
    padding: 35px 50px;
  }
  h1 { color: #0f172a; font-size: 1.8rem; margin-bottom: 0.4rem; }
  h2 { color: #ea580c; font-size: 1.4rem; }
  strong { color: #0f172a; }
  table { font-size: 0.72rem; }
  th { background-color: #0f172a; color: white; }
---

<!-- Slide 1 -->
# JANSAHAYAK
## Multilingual Government Scheme Eligibility Guide
### A Framework-Based Multi-Agent System with Grounded Hybrid RAG & Deterministic Rules

**Academic Course:** CSE476: Agentic AI / Multi-Agent Systems  
**Institution:** Lovely School of Computer Science & Engineering, Lovely Professional University  
**Supervisor:** Mr. Ravneet Singh (ID: 35120) | **Section:** K3E2327  

**Submitted by (Team Members):**
1. **Sudeep Kumar Reddy Eaga** — Reg: `12318529` | Roll No: `23`
2. **Kanithi Naresh Kumar** — Reg: `12313053`
3. **Seepana Jyothi Swaroop** — Reg: `12310991`

---

<!-- Slide 2 -->
# Problem Statement & Real-World Motivation
## The Citizen Welfare Access Dilemma in India

- **Linguistic Divide:** Over 22 official languages, yet official government welfare portals and gazettes are predominantly published in English or complex bureaucratic Hindi, excluding millions of rural citizens.
- **Fragmented Bureaucratic Silos:** Welfare schemes are distributed across unlinked ministries (Agriculture, Rural Dev, Health, MSME, Women & Child), forcing citizens to navigate dozens of portals.
- **Complex Multi-Conditional Eligibility:** Determining qualification requires evaluating income limits, land acreage, housing status, BPL certification, caste categories, age thresholds, and gender rules.
- **Document Ambiguity:** Citizens lack clear guidance on required papers and certifying authorities (Tehsildar, CSC, Panchayat, Banks), causing repeated rejections.

---

<!-- Slide 3 -->
# System Architecture & Microservices Topology
## Decoupled Microservice Topology (6 Services + 2 Backing Stores)

| Service Name | Port | Core Role & Technology |
|---|:---:|---|
| **`frontend-ui`** | `3000` | Nginx Alpine Single Page Application with Web Speech API STT/TTS |
| **`api-gateway`** | `8000` | Unified REST/SSE edge proxy, two-tier Redis cache & connection pooling |
| **`profile-memory-service`** | `8001` | Session working memory, profile state & read/write audit logging |
| **`rag-retrieval-service`** | `8002` | Hybrid Okapi BM25 + Dense Character Trigram vector RAG search |
| **`agent-orchestrator-service`** | `8003` | Microsoft Agent Framework `SequentialBuilder` multi-agent pipeline |
| **`voice-speech-service`** | `8004` | 12 BCP-47 speech locales & Markdown-to-speech sanitizer |
| **`postgres`** | `5432` | PostgreSQL 16 3NF schema with JSONB dynamic columns |
| **`redis`** | `6379` | Redis 7 in-memory store for exact and semantic query caches |

---

<!-- Slide 4 -->
# Multi-Agent Sequential Pipeline Architecture
## Microsoft Agent Framework (`SequentialBuilder`) Coordination

- **Why Sequential Pipeline?** Administrative welfare decisions follow a deterministic linear workflow:
  $$\text{Language/Profile} \longrightarrow \text{Candidate Schemes} \longrightarrow \text{Rules} \longrightarrow \text{Documents} \longrightarrow \text{Grounding} \longrightarrow \text{Language Audit}$$
- **Template Method Pattern:** `SpecializedPipelineAgent(BaseAgent)` orchestrates MAF lifecycle hooks, execution timing, and read/write audit entries.
- **Shared Memory Provider:** `SharedProfileMemoryContextProvider(ContextProvider)` dynamically syncs session memory with PostgreSQL and Redis.
- **Zero Hallucination Guarantee:** GroundingGate sits between rule evaluation and citizen output, cryptographically auditing citations.

---

<!-- Slide 5 -->
# Agent 1: Profile Intake Agent
## Language Detection & Demographic Slot Extraction

- **12-Language Script Detection Algorithm:**
  - Evaluates Unicode codepoints across 12 scripts (Devanagari, Gurmukhi, Telugu, Tamil, Bengali, Kannada, Gujarati, Malayalam, Odia, Urdu, Latin).
  - Disambiguates shared scripts (Hindi vs Marathi) using grammatical markers (`आहे`/`नाही` vs `है`/`नहीं`).
- **Indic & Urdu Numeral Normalizer:**
  - Maps native numerals to ASCII digits: `[०-९, ੦-੯, ౦-౯, ০-৯, ۰-۹] -> [0-9]`.
- **Regex Demographic Slot Extraction (14 Attributes):**
  - Extracts Age, Income (INR/Lakhs), Land Acres, Pucca House, BPL Card, Gender, Marital Status, Caste, Disability %, LPG, Student, Govt Employee, Girl Child Age.
- **Missing Field Detection:** Flags missing baseline parameters (`missing_profile_fields`) to guide the citizen interactively.

---

<!-- Slide 6 -->
# Agent 2: Scheme Retrieval Agent
## Grounded Hybrid Lexical (BM25) + Dense Vector RAG

- **Why Hybrid RAG?**
  - Pure sparse search misses colloquial dialect terms.
  - Pure dense vector search hallucinates or confuses official scheme acronyms (PM-KISAN vs PMFBY).
- **Hybrid Fusion Formula:**
  $$\text{Score} = 0.5 \times \text{BM25Score}(d, q) + 0.5 \times \text{CosineSimilarity}(\vec{E}_d, \vec{E}_q)$$
- **Profile-Guided Query Expansion:** Ingests raw query and enriches it with demographic context (e.g. "elderly rural farmer 2 acres bpl agriculture crop insurance").
- **Citation Lineage:** Retrieves top $K=10$ candidate chunks, retaining explicit chunk IDs (`scheme_id::chunk_0`) for GroundingGate verification.

---

<!-- Slide 7 -->
# Agent 3: Eligibility Rule Agent
## Deterministic Strategy Pattern & Tri-State Classification

- **Strategy Pattern (`_OPERATOR_STRATEGIES`):**
  - Pure comparator functions for `LTE`, `GTE`, `EQ`, `NEQ`, `IN`, `RANGE`, `BOOL_IS`.
- **Strictly Bounded to RAG Candidates:** Evaluates only schemes retrieved by RAG, completely preventing phantom scheme hallucination.
- **Composite Rule Grammar:**
  - `all_of`: Mandatory conjunction (every criterion must pass).
  - `any_of_groups`: Alternative disjunction (passes if $\ge 1$ branch passes).
- **Tri-State Classification Logic:**
  - **ELIGIBLE:** Zero failed rules, zero missing required fields, passed rules $\ge 1$.
  - **POTENTIAL:** Zero failed rules, 1–2 unconfirmed fields requiring citizen clarification.
  - **INELIGIBLE:** Violated $\ge 1$ statutory rule (e.g. income exceeded, govt employee exclusion).

---

<!-- Slide 8 -->
# Agent 4: Document Checklist Agent
## Intelligent Cross-Scheme Merging & Deduplication

- **Cross-Scheme Document Problem:** Qualifying for multiple schemes (e.g. PM-KISAN, PMFBY, PMAY-G, AB-PMJAY) naively yields duplicate bullet points for common papers like Aadhaar and Bank Passbooks.
- **Deduplication Algorithm:** Keyed dictionary `merged_docs: dict[str, DocumentRequirement]`. Consolidates identical documents into one bullet point while tracking all qualifying schemes in `required_for_schemes`.
- **Statutory Authority Attribution:**
  - **Aadhaar Card:** UIDAI / Aadhaar Seva Kendra
  - **BPL / Ration Card:** Food & Civil Supplies Department
  - **Income / Caste Certificate:** Tehsildar / Revenue Department / CSC
  - **Land Records:** Revenue Patwari / State Bhulekh Portal
  - **Disability Certificate:** CMO / District Medical Board

---

<!-- Slide 9 -->
# Agent 5: Guide Manager Agent & GroundingGate
## Formal Verification & Structured Synthesis

- **The Three Mandatory GroundingGate Invariants (`GroundingGate.verify`):**
  1. **Invariant 1 (RAG Lineage):** Scheme must exist in `retrieved_scheme_ids` with non-empty chunk evidence IDs.
  2. **Invariant 2 (Deterministic Passage):** Scheme must have 0 failed rules and $\ge 1$ passed rule.
  3. **Invariant 3 (Document Traceability):** Every checklist paper must link to at least one verified eligible scheme.
- **Direct Official Portals for Both Matched & Non-Matched Policies:**
  - **Eligible Schemes (Matched):** Official scheme titles kept verbatim intact with benefit summaries, qualification reasons, step-by-step workflow, and direct official portal links (`.gov.in` / `.nic.in`).
  - **Potential Schemes (Pending Facts):** Lists missing confirmation fields + direct official portal link to verify prerequisites.
  - **Non-Matched Schemes (Other Evaluated Policies):** Lists every evaluated policy with its explicit non-matching reason AND a direct official government portal link so the citizen can learn more directly from the ministry site.
  - **Consolidated document checklist** with issuing authorities and toll-free helpline numbers.

---

<!-- Slide 10 -->
# Agent 6: Language-Consistency Reviewer Agent
## Group-of-3 Quality Assurance & Auto-Repair Engine

- **Invariant 1: Native Script Consistency Audit:**
  - Computes script match ratio: $R_{\text{script}} = \frac{\text{Target\_Chars}}{\text{Total\_Alpha\_Chars}}$.
  - Indic scripts: Enforces $R_{\text{script}} \ge 0.35$ and verifies native greetings.
  - English: Enforces $R_{\text{script}} \ge 0.60$.
- **Invariant 2: Verbatim Scheme Name Preservation:**
  - Government scheme names are statutory legal entities (e.g. *"Pradhan Mantri Kisan Samman Nidhi"*). Translating them into generic dictionary words prevents citizens from locating the scheme at physical CSCs.
  - Verifies all official names remain verbatim intact.
- **Deterministic Auto-Repair:** Restores missing scheme titles and prepends localized greetings automatically if dropped during LLM synthesis.

---

<!-- Slide 11 -->
# Multilingual NLP, Voice & Data Visualizer
## 12 Languages, Dedicated Voice (:8004) & Scheme Analytics

- **12 Indian Languages:** English (`en`), Hindi (`hi`), Punjabi (`pa`), Telugu (`te`), Tamil (`ta`), Bengali (`bn`), Marathi (`mr`), Kannada (`kn`), Gujarati (`gu`), Malayalam (`ml`), Odia (`or`), Urdu (`ur`, RTL).
- **Dynamic Full-Page Localization:** Selecting a language instantly updates all navbar titles, tabs, form inputs, placeholders, voice hints, and scheme metrics without reloading.
- **Audio Waveform Equalizer:** 6-bar dynamic pulsating equalizer in the voice dock responding in real time to microphone dictation (STT) and read-aloud playback (TTS).
- **Scheme Analytics & KPI Matrix:** Each scheme card features an SVG radial match gauge (100%/75%/35%), financial benefit KPI pill, and 4 comparative analytics bars (Match, Financial Index, Process Ease, Document Simplicity).
- **Interactive Sector Filters:** Instant category filtering (`🌾 Agriculture`, `🏥 Healthcare`, `🏠 Housing`, `💼 Loans/MSME`, `👵 Pensions`, `👩 Women/Child`, `🛡️ Insurance`).
- **Markdown Speech Sanitizer:** `POST /api/v1/voice/sanitize-speech` cleans Markdown tables, URLs, and asterisks into fluent spoken utterances.

---

<!-- Slide 12 -->
# Database Design & Redis Caching
## PostgreSQL 16 Schema & Profile-Guarded Two-Tier Cache

- **PostgreSQL 16 Relational + JSONB Schema:**
  - 3NF tables: `SCHEMES`, `SCHEME_CHUNKS`, `CITIZEN_SESSIONS`, `AGENT_AUDIT_LOGS`, `EVALUATION_RUNS`.
  - JSONB columns for flexible rule definitions, required papers, and 12-language localized summaries.
- **Two-Tier Profile-Guarded Redis Cache:**
  - **Demographic Fingerprint:** Generates SHA-256 `profile_hash` over normalized demographic facts.
  - **Tier 1 (Exact Hit):** $\mathcal{O}(1)$ lookup on `<profile_hash>:<query_hash>`. Latency $< 5\text{ms}$.
  - **Tier 2 (Semantic Paraphrase):** Cosine similarity $\ge 0.90$ within the exact same demographic bucket.
  - **Zero Cross-Profile Hallucination Guarantee:** Completely partitions cache by demographic signature.

---

<!-- Slide 13 -->
# Software Engineering & Low-Level Design (LLD)
## SOLID Principles & Design Patterns

- **SOLID Principles:**
  - **SRP:** Single responsibility per agent, client, and repository.
  - **OCP:** Open for new rule operators (`_OPERATOR_STRATEGIES`) and language packs (`language_packs.py`) without modifying evaluators.
  - **LSP:** `RedisCacheStore` and `InMemoryCacheStore` identically fulfill `ICacheStore`.
  - **ISP & DIP:** Fine-grained interfaces in `shared/interfaces/`, injected via FastAPI.
- **GoF Design Patterns:**
  - **Template Method:** `SpecializedPipelineAgent` lifecycle and audit logging.
  - **Strategy Pattern:** Rule operators and LLM provider selection.
  - **Repository & Unit of Work:** `SqlProfileMemoryRepository` and `SqlSchemeRepository`.
  - **Cache-Aside:** `SemanticQueryCacheService`.

---

<!-- Slide 14 -->
# Quantitative Evaluation Benchmark (CO3 & CO4)
## 10 Multilingual Citizen Profiles Evaluated

| Metric | Score | Invariant Checked |
|---|:---:|---|
| **Macro Precision** | **100.0% (1.0000)** | Zero irrelevant schemes recommended |
| **Macro Recall** | **100.0% (1.0000)** | Zero eligible schemes missed |
| **Micro Precision / Recall** | **100.0% (1.0000)** | Perfect across all 35 scheme assignments |
| **GroundingGate Pass Rate** | **100.0%** | Zero ungrounded or hallucinated claims |
| **Scheme Name Preservation** | **100.0%** | All official names preserved verbatim |

- **Negative Control Profile (P10):** High-income urban government employee correctly evaluated to 0 eligible schemes.

---

<!-- Slide 15 -->
# Deployment & Execution
## Three Flexible Deployment Options & Automated Testing

- **Option A: Full Docker Compose (8 Containers):**
  - UI (:3000), Gateway (:8000), Memory (:8001), RAG (:8002), Orchestrator (:8003), Voice (:8004), Postgres (:5432), Redis (:6379).
  - Command: `docker compose up --build`
- **Option B: Portable Single Docker Container:**
  - Single self-contained image with SQLite and in-memory cache on port 8000.
  - Commands: `docker build -t jansahayak .` && `docker run -p 8000:8000 jansahayak`
- **Option C: Local Python Execution:**
  - Command: `set ORCHESTRATION_MODE=local_inproc && uvicorn services.api_gateway.main:app --port 8000`
- **Automated Test Suite:** Full 19-test suite passing in ~54s (`pytest -v`).

---

<!-- Slide 16 -->
# Summary & Academic Compliance
## Attainment of CO3 & CO4 · Bloom's L4, L5, L6

- **CO3 Attainment:** Designed and constructed a multi-agent system using Microsoft Agent Framework `SequentialBuilder`, shared context provider, and hybrid RAG.
- **CO4 Attainment:** Evaluated system across 10 multilingual profiles, achieving 100% precision, recall, grounding, and name preservation.
- **Bloom's Taxonomy:** L4 (Analyze), L5 (Evaluate), L6 (Create) achieved.
- **Future Roadmap:** DigiLocker API integration, offline edge speech models (IndicWav2Vec), state gazette crawlers.
- **Official GitHub Repository:** [https://github.com/SudeepReddyEaga/JanSahayak](https://github.com/SudeepReddyEaga/JanSahayak)

**Thank You! Questions & Live Demonstration on http://localhost:3000**
