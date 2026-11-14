# Low-Level Design (LLD) & System Architecture

## 1. Architectural Overview (Microservices + Microsoft Agent Framework)

The **Multilingual Government Scheme Eligibility Guide** (`JanSahayak AI`) is engineered as a decoupled microservice architecture running on **Microsoft Agent Framework (`agent-framework` + `agent-framework-orchestrations`)**, **FastAPI**, **PostgreSQL**, **Redis**, and a **Voice & Speech Service** spanning **12 Indian languages**.

```mermaid
flowchart LR
    UI["Frontend UI Microservice<br/>(Nginx :3000 + CitizenVoiceController)"] --> GW["API Gateway Microservice<br/>(FastAPI :8000)"]
    GW -->|"Exact + Semantic Cache Check"| REDIS[("Redis 7<br/>:6379")]
    GW -->|"REST / SSE Stream"| ORCH["Agent Orchestrator Service<br/>(MAF SequentialBuilder :8003)"]
    GW -->|"Voice Locales & Speech Chunks"| VOICE["Voice & Speech Service<br/>(FastAPI :8004)"]
    ORCH -->|"Read/Write UserProfileMemory"| MEM["Profile Memory Service<br/>(FastAPI :8001)"]
    ORCH -->|"Hybrid BM25+Vector RAG"| RAG["RAG Retrieval Service<br/>(FastAPI :8002)"]
    MEM --> REDIS
    MEM --> PG[("PostgreSQL 16<br/>:5432")]
    RAG --> REDIS
    RAG --> PG
```

---

## 2. Sequential Multi-Agent Pipeline with Grounding Gate

Every citizen query travels sequentially through 6 specialized agent modules wired via `agent_framework.orchestrations.SequentialBuilder`, sharing state through `SharedProfileMemoryContextProvider(ContextProvider)`:

```mermaid
sequenceDiagram
    participant C as Citizen UI
    participant G as API Gateway + Redis Cache
    participant A1 as 1. ProfileIntakeAgent
    participant A2 as 2. SchemeRetrievalAgent (RAG)
    participant A3 as 3. EligibilityRuleAgent
    participant A4 as 4. DocumentChecklistAgent
    participant A5 as 5. GuideManagerAgent (+ GroundingGate)
    participant A6 as 6. LanguageReviewerAgent (Add-On)
    participant M as UserProfileMemory (PG + Redis)

    C->>G: Voice or Text Query (12 supported languages)
    G->>G: Exact Key + Profile-Guarded Semantic Lookup
    alt Cache Hit
        G-->>C: Cached Verified Response (<5ms)
    else Cache Miss
        G->>A1: Workflow.run(query)
        A1->>M: Read & Write CitizenProfile + Language
        A1->>A2: Forward conversation
        A2->>M: Read Profile, Write RAG Chunks & Candidate IDs
        A2->>A3: Forward conversation
        A3->>M: Read Profile + RAG Candidates, Write Rule Decisions
        A3->>A4: Forward conversation
        A4->>M: Read Eligible IDs, Write Deduplicated Docs
        A4->>A5: Forward conversation
        A5->>A5: Execute GroundingGate.verify(memory)
        A5->>M: Write GroundingReport + Localized Draft
        A5->>A6: Forward conversation
        A6->>A6: Audit Target Language + Verbatim Scheme Names
        A6->>M: Write LanguageReviewReport + Final Reply
        A6-->>G: Verified ApplicationGuideResponse
        G-->>C: Streamed Steps + Final Guide
    end
```

---

## 3. Low-Level Design (LLD) & SOLID Principles

| Principle / Pattern | Concrete Implementation in Codebase |
|---|---|
| **Single Responsibility (SRP)** | Each agent resides in its own module under `services/agent_orchestrator_service/agents/`; repositories, embedders, cache stores, and rule operators each isolate one task. |
| **Open/Closed (OCP)** | `_OPERATOR_STRATEGIES` in `eligibility_rule_agent.py` and `LANGUAGE_TEMPLATES` in `shared/data/language_packs.py` allow adding new rule operators or languages without altering core evaluators. |
| **Liskov Substitution (LSP)** | `RedisCacheStore` and `InMemoryCacheStore` identically fulfill `ICacheStore`; `HttpProfileMemoryClient` and `LocalProfileMemoryClient` fulfill `IProfileMemoryClient`. |
| **Interface Segregation (ISP)** | Focused abstract contracts in `shared/interfaces/`: `ICacheStore`, `ISemanticQueryCache`, `IProfileMemoryRepository`, `ISchemeRepository`, `IVectorRetriever`, `ISpecializedAgent`, `IGroundingVerifier`, `ILanguageConsistencyReviewer`, `IVoiceLocaleRegistry`, `ISpeechTextSanitizer`. |
| **Dependency Inversion (DIP)** | High-level `SequentialSchemePipeline` depends purely on abstract interfaces (`IProfileMemoryClient`, `IRAGRetrievalClient`, `ISemanticQueryCache`, `IGroundingVerifier`), never hardcoded database or Redis drivers. |
| **Template Method Pattern** | `SpecializedPipelineAgent(BaseAgent, ISpecializedAgent)` manages MAF lifecycle hooks, timing, read/write audit logging, and streaming while subclasses implement `execute_step()`. |
| **Strategy Pattern** | `RuleOperator` comparators (`_OPERATOR_STRATEGIES`), `HybridTextEmbedder(IEmbeddingProvider)`, and `ChatClientFactory` LLM selection (`deterministic`, `openai`, `gemini`, `ollama`). |
| **Repository & Unit-of-Work** | `SqlProfileMemoryRepository`, `SqlSchemeRepository`, `SqlEvaluationRepository` + `DatabaseManager.session_scope()`. |
| **Cache-Aside & Decorator** | `SemanticQueryCacheService` wraps pipeline execution with exact canonical lookups + profile-guarded semantic vector lookups. |

---

## 4. Relational + JSONB Database Design (PostgreSQL)

```mermaid
erDiagram
    SCHEMES ||--o{ SCHEME_CHUNKS : contains
    CITIZEN_SESSIONS ||--o{ AGENT_AUDIT_LOGS : tracks

    SCHEMES {
        string scheme_id PK
        string official_name
        string short_code
        string ministry
        text benefit_summary
        json localized_summaries
        json rules_json
        json documents_json
        json application_steps_json
        string official_portal
        string helpline
    }

    SCHEME_CHUNKS {
        string chunk_id PK
        string scheme_id FK
        int chunk_index
        text chunk_text
        json embedding_json
    }

    CITIZEN_SESSIONS {
        string session_id PK
        string citizen_id
        string detected_language
        json profile_json
        json memory_snapshot_json
        datetime updated_at
    }

    AGENT_AUDIT_LOGS {
        int id PK
        string session_id FK
        string agent_name
        string action
        json fields_accessed_json
        text summary
        string timestamp
    }

    EVALUATION_RUNS {
        string run_id PK
        string timestamp
        int total_profiles
        float macro_precision
        float macro_recall
        float micro_precision
        float micro_recall
        float grounding_pass_rate
        json summary_json
    }

    QUERY_CACHE_AUDIT {
        int id PK
        string query_hash
        string language
        string cache_status
        float similarity_score
        float latency_ms
    }
```

---

## 5. Redis Two-Tier Accurate Query Cache Architecture

To ensure Redis caching is **both fast and 100% accurate** (never serving another demographic's schemes):
1. **Canonical Profile Signature**: Before checking semantic similarity, `ProfileIntakeAgent.extract_quick_profile()` extracts normalized demographic facts into a SHA-256 `profile_hash`.
2. **Tier 1 (Exact Hit)**: Looks up `scheme_guide:v1:exact:<profile_hash>:<query_hash>` in $O(1)$.
3. **Tier 2 (Semantic Paraphrase Hit)**: Queries `scheme_guide:v1:sem_bucket:<profile_hash>` containing character 3-gram + token vectors of previous queries *sharing the identical language and citizen profile*. If cosine similarity $\ge \text{SEMANTIC\_CACHE\_THRESHOLD}$, returns the cached verified guide with `cache_status = "semantic_hit"`.
4. **Tier 3 (RAG & Working Memory)**: `rag-retrieval-service` caches chunk retrievals under `scheme_guide:v1:rag:*`, and `profile-memory-service` maintains write-through session memory under `scheme_guide:v1:profile_mem:*`.

