/**
 * Interactive Frontend Controller for JanSahayak Multilingual Welfare Scheme Guide.
 * Connects to API Gateway REST & Server-Sent Events (SSE) endpoints and coordinates:
 *   1. Multilingual Citizen Chat (12 Indian Languages incl. Punjabi, Gujarati, Malayalam, Odia, Urdu)
 *   2. Voice Input (STT) & Read-Aloud Playback (TTS) via CitizenVoiceController
 *   3. Multi-Turn Session Conversation & 1-Click Missing-Field Follow-Up Prompts
 *   4. Interactive Document Readiness Progress Tracker & Printable/Downloadable Export
 *   5. Live 6-Agent Microsoft Agent Framework Pipeline Stepper
 *   6. Shared Profile Memory Inspector, 10-Profile Precision/Recall Benchmark & Redis Telemetry
 */

const SAMPLE_PROMPTS = [
  {
    label: "Hindi · Elderly Farmer",
    lang: "hi",
    query:
      "मैं 65 साल का किसान हूं। मैं गांव में रहता हूं, मेरे पास 2 एकड़ खेती की जमीन है, सालाना आय 90000 रुपये है, BPL कार्ड है और पक्का घर नहीं है।",
  },
  {
    label: "Punjabi · Rural Farmer",
    lang: "pa",
    query:
      "ਮੈਂ 45 ਸਾਲ ਦਾ ਪੇਂਡੂ ਕਿਸਾਨ ਹਾਂ। ਮੇਰੇ ਕੋਲ 2 ਏਕੜ ਖੇਤੀ ਵਾਲੀ ਜ਼ਮੀਨ ਹੈ, ਪਰਿਵਾਰ ਦੀ ਸਾਲਾਨਾ ਆਮਦਨ 95000 ਰੁਪਏ ਹੈ, ਬੀਪੀਐਲ ਕਾਰਡ ਹੈ, ਪੱਕਾ ਘਰ ਨਹੀਂ ਹੈ ਅਤੇ ਸਰਕਾਰੀ ਕਰਮਚਾਰੀ ਨਹੀਂ ਹਾਂ।",
  },
  {
    label: "Telugu · Rural Widow",
    lang: "te",
    query:
      "నేను 48 సంవత్సరాల గ్రామీణ వితంతువు మహిళను మరియు కూలీ పని చేస్తాను. నాకు బిపిఎల్ కార్డు ఉంది, వార్షిక ఆదాయం 75000 రూపాయలు, నాకు గ్యాస్ కనెక్షన్ లేదు మరియు పక్కా ఇల్లు లేదు.",
  },
  {
    label: "English · OBC Student",
    lang: "en",
    query:
      "I am a 20-year-old male undergraduate college student from the OBC category living in an urban city. My family annual income is 180000 INR.",
  },
  {
    label: "Tamil · Pregnant Woman",
    lang: "ta",
    query:
      "நான் 26 வயது கர்ப்பிணிப் பெண், கிராமத்தில் வசிக்கிறேன், வேலையற்ற நிலை, SC பிரிவைச் சேர்ந்தவர், குடும்ப ஆண்டு வருமானம் 120000 ரூபாய், எனக்கு கேஸ் இணைப்பு இல்லை, அரசு ஊழியர் அல்ல.",
  },
  {
    label: "Bengali · Street Vendor",
    lang: "bn",
    query:
      "আমি ৩৪ বছর বয়সী শহরের একজন রাস্তার হকার। আমার বার্ষিক আয় ১৮০০০০ টাকা এবং আমি সরকারি কর্মচারী নই।",
  },
  {
    label: "Marathi · Rural Potter",
    lang: "mr",
    query:
      "मी 38 वर्षांचा ग्रामीण भागातील कुंभार कारागीर आहे. माझे वार्षिक उत्पन्न 140000 रुपये आहे, मला पक्के घर नाही आणि मी सरकारी नोकरदार नाही.",
  },
  {
    label: "Kannada · Divyang Citizen",
    lang: "kn",
    query:
      "ನಾನು 42 ವರ್ಷದ ಗ್ರಾಮೀಣ ವ್ಯಕ್ತಿ, ನನಗೆ 85% ಅಂಗವೈಕಲ್ಯವಿದೆ, ಬಿಪಿಎಲ್ ಕಾರ್ಡ್ ಇದೆ, ವಾರ್ಷಿಕ ಆದಾಯ 80000 ರೂಪಾಯಿ, ಪಕ್ಕಾ ಮನೆ ಇಲ್ಲ ಮತ್ತು ನಿರುದ್ಯೋಗಿ, ಸರ್ಕಾರಿ ನೌಕರರಲ್ಲ.",
  },
  {
    label: "Gujarati · Dairy & Land Farmer",
    lang: "gu",
    query:
      "હું 40 વર્ષનો ગ્રામીણ ખેડૂત છું, મારી પાસે 2 એકર ખેતીની જમીન છે, વાર્ષિક આવક 90000 રૂપિયા છે, બીપીએલ કાર્ડ છે, પાકું ઘર નથી અને હું સરકારી કર્મચારી નથી.",
  },
  {
    label: "Malayalam · Rural Artisan",
    lang: "ml",
    query:
      "ഞാൻ 36 വയസ്സുള്ള ഗ്രാമീണ കൈത്തൊഴിലാളിയാണ്, വാർഷിക വരുമാനം 95000 രൂപയാണ്, പക്കാ വീട് ഇല്ല, ബിപിഎൽ കാർഡ് ഉണ്ട്, സർക്കാർ ജീവനക്കാരനല്ല.",
  },
  {
    label: "Odia · Pregnant Mother",
    lang: "or",
    query:
      "ମୁଁ 27 ବର୍ଷର ଗ୍ରାମୀଣ ଗର୍ଭବତୀ ମହିଳା ଅଟେ, ମୋର ବିପିଏଲ୍ କାର୍ଡ ଅଛି, ବାର୍ଷିକ ଆୟ 85000 ଟଙ୍କା, ଗ୍ୟାସ୍ ସଂଯୋଗ ନାହିଁ ଏବଂ ସରକାରୀ କର୍ମଚାରୀ ନୁହେଁ।",
  },
  {
    label: "Urdu · Farmer & Girl Father",
    lang: "ur",
    query:
      "میں 38 سال کا دیہی کسان ہوں، میرے پاس 2 ایکڑ زرعی زمین ہے، سالانہ آمدنی 110000 روپے ہے، میری 6 سال کی بیٹی ہے اور میں سرکاری ملازم نہیں ہوں۔",
  },
];

// Suggested natural follow-up phrases mapped to missing profile field keys
const MISSING_FIELD_QUICK_REPLIES = {
  age: ["My age is 35 years", "My age is 65 years"],
  annual_income_inr: ["My annual family income is Rs. 90,000", "My annual family income is Rs. 2,00,000"],
  residence_type: ["I live in a rural village", "I live in an urban city"],
  occupation: ["I am a farmer", "I am an artisan", "I am a student"],
  has_bpl_card: ["I have a BPL card", "I do not have a BPL card"],
  owns_pucca_house: ["I do not own a pucca house", "I own a pucca house"],
  is_pregnant_or_lactating: ["Yes, expecting mother / pregnant", "Not pregnant or lactating"],
  has_girl_child_under_10: ["I have a 6-year-old girl child", "No girl child under 10"],
};

let activeSessionId = null;
let conversationHistory = [];
let latestGuideResponse = null;
let cachedSchemesCatalog = [];
let activeKbCategory = "all";
let voiceController = null;

// ============================================================================
// Initialization, Voice Binding & Tab Switching
// ============================================================================

document.addEventListener("DOMContentLoaded", async () => {
  initVoiceController();
  renderSampleChips();
  bindTabEvents();
  bindActionButtons();
  updateLanguageDirectionAndLocale();
  refreshHealthStatus();
  loadSchemesCatalog();
  loadCacheStats();
  loadEvaluationHistory();
});

function initVoiceController() {
  voiceController = new window.CitizenVoiceController({
    onTranscript: (text, isFinal) => {
      const box = document.getElementById("citizenQuery");
      box.value = text;
      // Optionally auto-run the multi-agent pipeline once voice dictation finalizes
      if (isFinal && document.getElementById("voiceAutoSendChk").checked && text.trim()) {
        runQueryFlow(text);
      }
    },
    onStatusChange: (state) => {
      const micBtn = document.getElementById("voiceMicBtn");
      const micLabel = document.getElementById("voiceMicBtnLabel");
      const statusText = document.getElementById("voiceStatusText");
      const ttsStatusLine = document.getElementById("ttsStatusLine");
      const playBtn = document.getElementById("ttsPlayBtn");
      const pauseBtn = document.getElementById("ttsPauseBtn");
      const stopBtn = document.getElementById("ttsStopBtn");

      if (!state.canListen) {
        micBtn.disabled = true;
        micLabel.textContent = "Mic Unsupported Here";
      } else {
        micBtn.disabled = false;
        micBtn.classList.toggle("listening", state.isListening);
        micLabel.textContent = state.isListening ? "Stop Listening" : "Speak in Selected Language";
      }

      if (state.message && (state.code.startsWith("stt") || state.code === "listening" || state.code === "idle")) {
        statusText.textContent = state.message;
      }

      if (!state.canSpeak && playBtn) {
        playBtn.disabled = true;
        playBtn.title = "SpeechSynthesis not supported by this browser";
      } else if (playBtn) {
        playBtn.disabled = !latestGuideResponse;
        pauseBtn.disabled = !state.isSpeaking;
        pauseBtn.textContent = state.isPaused ? "Resume" : "Pause";
        stopBtn.disabled = !state.isSpeaking;
        if (state.code === "speaking" || state.code === "paused" || state.code === "tts_done" || state.code === "unsupported_tts") {
          ttsStatusLine.textContent = state.message;
        }
      }
    },
  });

  voiceController.loadLocales().then(() => updateLanguageDirectionAndLocale());
}

function updateLanguageDirectionAndLocale() {
  const selectedLang = document.getElementById("languageSelect").value || "en";
  const spec = voiceController ? voiceController.getLocaleSpec(selectedLang) : { bcp47_tag: `${selectedLang}-IN`, rtl: selectedLang === "ur" };
  document.getElementById("voiceLocalePill").textContent = spec.bcp47_tag;

  const queryEl = document.getElementById("citizenQuery");
  queryEl.dir = spec.rtl ? "rtl" : "ltr";
}

function bindTabEvents() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      const targetId = `tab-${btn.dataset.tab}`;
      document.getElementById(targetId).classList.add("active");

      if (btn.dataset.tab === "memory") loadSessions();
      if (btn.dataset.tab === "kb-cache") {
        loadCacheStats();
        loadSchemesCatalog();
      }
      if (btn.dataset.tab === "evaluation") loadEvaluationHistory();
    });
  });
}

function renderSampleChips() {
  const container = document.getElementById("sampleChips");
  container.innerHTML = "";
  SAMPLE_PROMPTS.forEach((sample) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "sample-chip";
    btn.textContent = sample.label;
    btn.addEventListener("click", () => {
      document.getElementById("citizenQuery").value = sample.query;
      document.getElementById("languageSelect").value = sample.lang;
      activeSessionId = null;
      conversationHistory = [];
      renderChatThread();
      updateSessionBadge();
      updateLanguageDirectionAndLocale();
    });
    container.appendChild(btn);
  });
}

function bindActionButtons() {
  document.getElementById("submitQueryBtn").addEventListener("click", () => runQueryFlow());
  document.getElementById("citizenQuery").addEventListener("keydown", (ev) => {
    if ((ev.ctrlKey || ev.metaKey) && ev.key === "Enter") {
      ev.preventDefault();
      runQueryFlow();
    }
  });

  document.getElementById("languageSelect").addEventListener("change", updateLanguageDirectionAndLocale);
  document.getElementById("clearInputBtn").addEventListener("click", () => {
    document.getElementById("citizenQuery").value = "";
  });

  document.getElementById("voiceMicBtn").addEventListener("click", () => {
    const selectedLang = document.getElementById("languageSelect").value || "en";
    voiceController.toggleListening(selectedLang);
  });

  document.getElementById("ttsPlayBtn").addEventListener("click", () => {
    if (!latestGuideResponse) return;
    voiceController.speakGuide(latestGuideResponse.final_reply, latestGuideResponse.detected_language);
  });
  document.getElementById("ttsPauseBtn").addEventListener("click", () => voiceController.togglePauseResume());
  document.getElementById("ttsStopBtn").addEventListener("click", () => voiceController.stopSpeaking());
  document.getElementById("ttsRateSelect").addEventListener("change", (ev) => {
    voiceController.setRate(ev.target.value);
  });

  document.getElementById("copyGuideBtn").addEventListener("click", copyGuideToClipboard);
  document.getElementById("downloadGuideBtn").addEventListener("click", downloadGuideAsText);

  document.getElementById("newSessionBtn").addEventListener("click", () => {
    voiceController.stopSpeaking();
    activeSessionId = null;
    conversationHistory = [];
    latestGuideResponse = null;
    renderChatThread();
    updateSessionBadge();
    document.getElementById("citizenQuery").value = "";
    document.getElementById("resultsContainer").classList.add("hidden");
    document.getElementById("quickFollowupsBox").classList.add("hidden");
    resetPipelineSteps();
  });

  document.getElementById("testParaphraseBtn").addEventListener("click", demoParaphraseCache);
  document.getElementById("refreshSessionsBtn").addEventListener("click", loadSessions);
  document.getElementById("runEvalBtn").addEventListener("click", runEvaluationBenchmark);
  document.getElementById("refreshCacheBtn").addEventListener("click", loadCacheStats);
  document.getElementById("flushCacheBtn").addEventListener("click", flushRedisCache);
  document.getElementById("kbSearchInput").addEventListener("input", renderFilteredSchemes);
}

function updateSessionBadge() {
  const badge = document.getElementById("sessionBadge");
  badge.textContent = activeSessionId ? `Session: ${activeSessionId}` : "New Session";
}

// ============================================================================
// Health & Microservices Strip
// ============================================================================

async function refreshHealthStatus() {
  const strip = document.getElementById("healthStrip");
  try {
    const res = await fetch("/health");
    const data = await res.json();
    const pills = [];
    for (const [svc, st] of Object.entries(data.services || {})) {
      const ok = st.includes("healthy");
      pills.push(
        `<span class="pill ${ok ? "pill-success" : "pill-danger"}">${svc}: ${st}</span>`
      );
    }
    pills.push(`<span class="pill pill-info">Cache: ${data.cache_backend || "redis"}</span>`);
    strip.innerHTML = pills.join("");
  } catch (err) {
    strip.innerHTML = `<span class="pill pill-danger">Gateway Unreachable</span>`;
  }
}

// ============================================================================
// Pipeline Stepper & SSE Citizen Eligibility Query Execution
// ============================================================================

function resetPipelineSteps() {
  document.querySelectorAll("#pipelineSteps .step-card").forEach((el) => {
    el.classList.remove("running", "completed");
    el.querySelector(".step-status").textContent = "Waiting";
  });
  const pill = document.getElementById("cacheStatusPill");
  pill.className = "pill pill-neutral";
  pill.textContent = "Idle";
}

function collectProfileOverrides() {
  const overrides = {};
  const age = document.getElementById("ovrAge").value;
  const income = document.getElementById("ovrIncome").value;
  const gender = document.getElementById("ovrGender").value;
  const occ = document.getElementById("ovrOccupation").value;
  const res = document.getElementById("ovrResidence").value;
  const cat = document.getElementById("ovrCategory").value;
  const bpl = document.getElementById("ovrBpl").value;
  const pucca = document.getElementById("ovrPucca").value;

  if (age) overrides.age = parseInt(age, 10);
  if (income) overrides.annual_income_inr = parseInt(income, 10);
  if (gender) overrides.gender = gender;
  if (occ) overrides.occupation = occ;
  if (res) overrides.residence_type = res;
  if (cat) overrides.social_category = cat;
  if (bpl !== "") overrides.has_bpl_card = bpl === "true";
  if (pucca !== "") overrides.owns_pucca_house = pucca === "true";

  return Object.keys(overrides).length ? overrides : null;
}

async function runQueryFlow(customQuery = null) {
  const queryText = (customQuery || document.getElementById("citizenQuery").value).trim();
  if (!queryText) {
    alert("Please enter or speak a citizen profile query, or click a sample prompt.");
    return;
  }

  voiceController.stopSpeaking();
  const preferredLang = document.getElementById("languageSelect").value || null;
  const bypassCache = document.getElementById("bypassCacheChk").checked;
  const overrides = collectProfileOverrides();

  conversationHistory.push({
    role: "citizen",
    lang: preferredLang || "auto",
    text: queryText,
    time: new Date().toLocaleTimeString(),
  });
  renderChatThread();

  resetPipelineSteps();
  const cachePill = document.getElementById("cacheStatusPill");
  cachePill.className = "pill pill-info";
  cachePill.textContent = "Executing...";

  const submitBtn = document.getElementById("submitQueryBtn");
  submitBtn.disabled = true;

  try {
    const payload = {
      query: queryText,
      session_id: activeSessionId,
      preferred_language: preferredLang,
      profile_overrides: overrides,
      bypass_cache: bypassCache,
    };

    const response = await fetch("/api/v1/guide/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split("\n\n");
      buffer = blocks.pop() || "";

      for (const block of blocks) {
        const lines = block.split("\n");
        let eventType = "message";
        let dataStr = "";
        for (const ln of lines) {
          if (ln.startsWith("event:")) eventType = ln.slice(6).trim();
          if (ln.startsWith("data:")) dataStr += ln.slice(5).trim();
        }
        if (!dataStr) continue;
        const parsed = JSON.parse(dataStr);

        if (eventType === "agent_step") {
          markPipelineStepCompleted(parsed);
        } else if (eventType === "cache_hit") {
          cachePill.className = "pill pill-success";
          cachePill.textContent = `REDIS ${parsed.cache_status.toUpperCase()} (${parsed.similarity})`;
        } else if (eventType === "complete") {
          renderCompleteGuide(parsed);
        }
      }
    }
  } catch (err) {
    alert(`Pipeline error: ${err.message}`);
    cachePill.className = "pill pill-danger";
    cachePill.textContent = "Error";
  } finally {
    submitBtn.disabled = false;
    loadCacheStats();
  }
}

function markPipelineStepCompleted(trace) {
  const card = document.querySelector(`#pipelineSteps .step-card[data-stage="${trace.stage}"]`);
  if (!card) return;
  card.classList.remove("running");
  card.classList.add("completed");
  card.querySelector(".step-status").textContent = `${trace.duration_ms.toFixed(1)} ms ✓`;
}

function renderChatThread() {
  const box = document.getElementById("chatThreadBox");
  const badge = document.getElementById("turnCountBadge");
  const turns = conversationHistory.filter((m) => m.role === "citizen").length;
  badge.textContent = `${turns} ${turns === 1 ? "Turn" : "Turns"}`;

  if (!conversationHistory.length) {
    box.innerHTML = `<p class="muted">Start by speaking or typing your profile. Follow-up turns reuse your active session memory automatically.</p>`;
    return;
  }

  box.innerHTML = conversationHistory
    .map(
      (msg) => `
    <div class="chat-bubble ${msg.role}">
      <div class="chat-meta">${msg.role === "citizen" ? "Citizen" : "JanSahayak Guide"} · ${msg.lang.toUpperCase()} · ${msg.time}</div>
      <div>${escapeHtml(msg.text)}</div>
    </div>`
    )
    .join("");
  box.scrollTop = box.scrollHeight;
}

function renderCompleteGuide(data) {
  latestGuideResponse = data;
  activeSessionId = data.session_id;
  updateSessionBadge();

  // Record summarized assistant turn inside interactive conversation thread
  const eligibleTitles = (data.eligible_schemes || []).map((s) => s.short_code).join(", ") || "None";
  conversationHistory.push({
    role: "assistant",
    lang: data.detected_language,
    text: `Matched ${(data.eligible_schemes || []).length} eligible scheme(s): ${eligibleTitles} | ${(data.document_checklist || []).length} document(s) required.`,
    time: new Date().toLocaleTimeString(),
  });
  renderChatThread();
  renderQuickFollowups(data.missing_fields_prompted || []);

  // Ensure all traces show on pipeline cards (even on Redis cache hit)
  (data.pipeline_traces || []).forEach(markPipelineStepCompleted);

  // Cache badge
  const pill = document.getElementById("cacheStatusPill");
  if (data.cache_status === "exact_hit" || data.cache_status === "semantic_hit") {
    pill.className = "pill pill-success";
    const sim = data.cache_similarity != null ? ` (sim=${data.cache_similarity})` : "";
    pill.textContent = `REDIS ${data.cache_status.toUpperCase()}${sim} · ${data.total_latency_ms} ms`;
  } else {
    pill.className = "pill pill-info";
    pill.textContent = `LIVE PIPELINE (${data.cache_status.toUpperCase()}) · ${data.total_latency_ms} ms`;
  }

  document.getElementById("resultsContainer").classList.remove("hidden");

  // Verification Banner
  const g = data.grounding_report;
  const r = data.language_review_report;
  document.getElementById("verificationBanner").innerHTML = `
    <span class="pill ${g.passed ? "pill-success" : "pill-danger"}">
      GroundingGate: ${g.passed ? "VERIFIED" : "FAILED"} (${Math.round(g.citation_coverage * 100)}% cited)
    </span>
    <span class="pill ${r.language_consistent ? "pill-success" : "pill-warn"}">
      Language Review (${r.target_language}): ${r.language_consistent ? "CONSISTENT" : "REPAIRED"}
    </span>
    <span class="pill ${r.scheme_names_intact ? "pill-success" : "pill-danger"}">
      Scheme Names Intact: ${r.scheme_names_intact ? "100% PRESERVED" : "ALTERED"} (${r.intact_scheme_names.length})
    </span>
    <span class="pill pill-info">${data.framework}</span>
  `;

  // Final Localized Reply with RTL direction support for Urdu
  const replyBox = document.getElementById("finalReplyBox");
  const spec = voiceController ? voiceController.getLocaleSpec(data.detected_language) : { rtl: data.detected_language === "ur" };
  replyBox.dir = spec.rtl ? "rtl" : "ltr";
  replyBox.textContent = data.final_reply;
  document.getElementById("replyLangBadge").textContent = data.detected_language.toUpperCase();
  document.getElementById("ttsPlayBtn").disabled = !voiceController.canSpeak;
  document.getElementById("ttsStatusLine").textContent = voiceController.canSpeak
    ? `Ready to read aloud in ${spec.display_name || data.detected_language} (${spec.bcp47_tag || data.detected_language}).`
    : "Text-to-Speech unavailable in this browser; written guide ready.";

  // Extracted Profile Chips
  const chipBox = document.getElementById("extractedProfileChips");
  chipBox.innerHTML = "";
  Object.entries(data.citizen_profile || {}).forEach(([k, v]) => {
    if (v === null || k === "raw_query") return;
    const chip = document.createElement("span");
    chip.className = "profile-chip";
    chip.textContent = `${k}: ${v}`;
    chipBox.appendChild(chip);
  });

  // Document Checklist + Interactive Readiness Progress Tracker
  const docs = data.document_checklist || [];
  document.getElementById("docCountBadge").textContent = `${docs.length} Documents`;
  const docBox = document.getElementById("documentChecklistBox");
  docBox.innerHTML = docs.length
    ? docs
        .map(
          (d, idx) => `
      <label class="doc-item">
        <input type="checkbox" class="doc-ready-chk" data-idx="${idx}" />
        <div>
          <strong>${escapeHtml(d.localized_names?.[data.detected_language] || d.name)}</strong>
          <div class="muted">For: ${d.required_for_schemes.join(", ")} · Obtain at: ${escapeHtml(d.where_to_obtain)}</div>
        </div>
      </label>`
        )
        .join("")
    : `<p class="muted">No documents required (no schemes qualified).</p>`;

  docBox.querySelectorAll(".doc-ready-chk").forEach((chk) => {
    chk.addEventListener("change", updateDocumentReadiness);
  });
  updateDocumentReadiness();

  // Eligible Schemes Cards with Per-Scheme "Read Aloud" Button
  const eligible = data.eligible_schemes || [];
  document.getElementById("eligibleCountBadge").textContent = `${eligible.length} Eligible`;
  const grid = document.getElementById("eligibleSchemesGrid");
  grid.innerHTML = eligible.length
    ? eligible
        .map(
          (s, idx) => `
      <div class="scheme-card">
        <div class="scheme-header-row">
          <h3>${escapeHtml(s.official_name)}</h3>
          <div style="display:flex; gap:6px; align-items:center;">
            <button type="button" class="btn btn-secondary btn-sm speak-scheme-btn" data-scheme-idx="${idx}" title="Read this scheme aloud">Speak</button>
            ${s.official_portal ? `<a href="${s.official_portal}" target="_blank" rel="noopener" class="btn btn-primary btn-sm" style="text-decoration:none;" title="Go directly to official portal">🌐 Official Site &rarr;</a>` : ""}
          </div>
        </div>
        <div class="scheme-meta">${escapeHtml(s.ministry)} · RAG Score: ${s.rag_score.toFixed(2)}</div>
        <p><strong>Benefit:</strong> ${escapeHtml(s.localized_benefit_summary || s.benefit_summary)}</p>
        <p><strong>Why Qualified:</strong> ${escapeHtml(s.localized_reason || s.reason)}</p>
        <details>
          <summary>Rule Checks (${s.passed_rules.length} Passed) &amp; Application Steps</summary>
          <ul class="rule-list">
            ${s.passed_rules.map((pr) => `<li>✓ <b>${escapeHtml(pr.field)}</b>=${escapeHtml(String(pr.actual_value))} — ${escapeHtml(pr.description)}</li>`).join("")}
          </ul>
          <ol class="rule-list">
            ${s.application_steps.map((st) => `<li>${escapeHtml(st)}</li>`).join("")}
          </ol>
          <div class="muted" style="margin-top:8px;">
            Official Portal: <a href="${s.official_portal}" target="_blank" rel="noopener" style="font-weight:600; color:var(--primary);">${s.official_portal}</a> · Helpline: ${escapeHtml(s.helpline)}
          </div>
        </details>
      </div>`
        )
        .join("")
    : `<p class="muted">No schemes matched all statutory eligibility rules for this citizen profile.</p>`;

  grid.querySelectorAll(".speak-scheme-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const s = eligible[parseInt(btn.dataset.schemeIdx, 10)];
      if (!s) return;
      const snippet = `${s.official_name}. ${s.localized_benefit_summary || s.benefit_summary}. ${s.localized_reason || s.reason}.`;
      voiceController.speakGuide(snippet, data.detected_language);
    });
  });

  // Potential & Ineligible Cards with Direct Official Portal Links
  const potential = data.potential_schemes || [];
  document.getElementById("potentialCountBadge").textContent = potential.length;
  document.getElementById("potentialSchemesBox").innerHTML = potential.length
    ? potential
        .map(
          (p) =>
            `<div class="session-item" style="display:flex; flex-direction:column; gap:6px;">
               <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                 <strong>${escapeHtml(p.official_name)}</strong>
                 ${p.official_portal ? `<a href="${p.official_portal}" target="_blank" rel="noopener" class="btn btn-secondary btn-sm" style="text-decoration:none; white-space:nowrap;">🌐 Official Portal</a>` : ""}
               </div>
               <div class="muted">${escapeHtml(p.localized_reason || p.reason)}</div>
               ${p.missing_fields && p.missing_fields.length ? `<div style="font-size:11.5px; color:#c2410c;">Pending confirmation: ${escapeHtml(p.missing_fields.join(", "))}</div>` : ""}
               ${p.official_portal ? `<div style="font-size:11px;"><a href="${p.official_portal}" target="_blank" rel="noopener" style="color:var(--primary); text-decoration:underline;">Learn more &amp; verify requirements on official portal &rarr;</a></div>` : ""}
             </div>`
        )
        .join("")
    : `<p class="muted">No ambiguous/pending schemes.</p>`;

  const ineligible = data.ineligible_schemes || [];
  document.getElementById("ineligibleCountBadge").textContent = ineligible.length;
  document.getElementById("ineligibleSchemesBox").innerHTML = ineligible.length
    ? ineligible
        .map(
          (x) =>
            `<div class="session-item" style="display:flex; flex-direction:column; gap:6px;">
               <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                 <strong>${escapeHtml(x.official_name || x.scheme_id)}</strong>
                 ${x.official_portal ? `<a href="${x.official_portal}" target="_blank" rel="noopener" class="btn btn-secondary btn-sm" style="text-decoration:none; white-space:nowrap;">🌐 Official Portal &rarr;</a>` : ""}
               </div>
               <div class="muted" style="font-size:12px;"><strong>Reason not matched:</strong> ${escapeHtml(x.localized_reason || x.reason)}</div>
               ${x.official_portal ? `<div style="font-size:11px;"><a href="${x.official_portal}" target="_blank" rel="noopener" style="color:var(--primary); text-decoration:underline;">Explore official policy criteria &amp; future guidelines at ${escapeHtml(x.official_portal)}</a></div>` : ""}
             </div>`
        )
        .join("")
    : `<p class="muted">None.</p>`;

  // Optional auto-read after pipeline response finishes
  if (document.getElementById("voiceAutoReadChk").checked && voiceController.canSpeak) {
    voiceController.speakGuide(data.final_reply, data.detected_language);
  }
}

function renderQuickFollowups(missingFields) {
  const wrapper = document.getElementById("quickFollowupsBox");
  const chipsContainer = document.getElementById("quickFollowupChips");
  chipsContainer.innerHTML = "";

  const suggestions = [];
  missingFields.forEach((field) => {
    (MISSING_FIELD_QUICK_REPLIES[field] || []).forEach((phrase) => suggestions.push(phrase));
  });

  if (!suggestions.length) {
    wrapper.classList.add("hidden");
    return;
  }

  suggestions.slice(0, 6).forEach((phrase) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "sample-chip";
    btn.textContent = `+ ${phrase}`;
    btn.addEventListener("click", () => {
      document.getElementById("citizenQuery").value = phrase;
      runQueryFlow(phrase);
    });
    chipsContainer.appendChild(btn);
  });
  wrapper.classList.remove("hidden");
}

function updateDocumentReadiness() {
  const checkboxes = document.querySelectorAll("#documentChecklistBox .doc-ready-chk");
  const total = checkboxes.length;
  const checked = Array.from(checkboxes).filter((c) => c.checked).length;
  document.getElementById("docReadinessText").textContent = `${checked} / ${total} Ready`;
  const pct = total ? Math.round((checked / total) * 100) : 0;
  document.getElementById("docProgressBar").style.width = `${pct}%`;
}

async function copyGuideToClipboard() {
  if (!latestGuideResponse) return;
  try {
    await navigator.clipboard.writeText(latestGuideResponse.final_reply);
    const btn = document.getElementById("copyGuideBtn");
    btn.textContent = "Copied ✓";
    setTimeout(() => {
      btn.textContent = "Copy";
    }, 1500);
  } catch (_) {}
}

function downloadGuideAsText() {
  if (!latestGuideResponse) return;
  const blob = new Blob([latestGuideResponse.final_reply], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `scheme-guide-${latestGuideResponse.session_id}-${latestGuideResponse.detected_language}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

// Demonstrate Redis Semantic Cache Hit using a paraphrased version of a citizen query
async function demoParaphraseCache() {
  const baseQuery =
    "I am a 35-year-old urban small business owner with an annual income of 550000 INR and I have a 6-year-old girl child.";
  const paraphraseQuery =
    "Which government welfare benefits fit a 35yo city small business owner earning 550000 INR with a 6-year-old girl child?";

  document.getElementById("languageSelect").value = "en";
  updateLanguageDirectionAndLocale();
  document.getElementById("bypassCacheChk").checked = false;
  document.getElementById("citizenQuery").value = baseQuery;
  await runQueryFlow(baseQuery);

  document.getElementById("citizenQuery").value = paraphraseQuery;
  await runQueryFlow(paraphraseQuery);
}

// ============================================================================
// TAB 2: Shared User-Profile Memory & Agent Audit Inspector
// ============================================================================

async function loadSessions() {
  const listBox = document.getElementById("sessionsListBox");
  listBox.innerHTML = `<p class="muted">Loading sessions...</p>`;
  try {
    const res = await fetch("/api/v1/sessions?limit=15");
    const sessions = await res.json();
    if (!sessions.length) {
      listBox.innerHTML = `<p class="muted">No citizen sessions stored yet.</p>`;
      return;
    }
    listBox.innerHTML = "";
    sessions.forEach((sess) => {
      const div = document.createElement("div");
      div.className = "session-item";
      div.innerHTML = `
        <strong>${escapeHtml(sess.session_id)}</strong> · <span class="badge badge-info">${escapeHtml(sess.profile.language)}</span>
        <div class="muted">Eligible: ${(sess.eligible_scheme_ids || []).join(", ") || "None"} | Audit Events: ${(sess.audit_log || []).length}</div>
      `;
      div.addEventListener("click", () => renderMemorySnapshot(sess));
      listBox.appendChild(div);
    });
    renderMemorySnapshot(sessions[0]);
  } catch (err) {
    listBox.innerHTML = `<p class="muted">Failed to load sessions: ${escapeHtml(err.message)}</p>`;
  }
}

function renderMemorySnapshot(sess) {
  const box = document.getElementById("memoryInspectorBox");
  const auditHtml = (sess.audit_log || [])
    .map(
      (a) =>
        `<tr><td><b>${escapeHtml(a.agent)}</b></td><td><span class="badge ${a.action === "write" ? "badge-success" : "badge-info"}">${a.action.toUpperCase()}</span></td><td>${escapeHtml((a.fields_accessed || []).join(", "))}</td><td>${escapeHtml(a.summary)}</td></tr>`
    )
    .join("");

  box.innerHTML = `
    <div class="table-wrap">
      <table>
        <thead><tr><th>Agent</th><th>Op</th><th>Fields Accessed</th><th>Audit Summary</th></tr></thead>
        <tbody>${auditHtml}</tbody>
      </table>
    </div>
    <h4 class="sub-heading">Persisted Shared UserProfileMemory JSON</h4>
    <pre>${escapeHtml(JSON.stringify({ session_id: sess.session_id, profile: sess.profile, eligible_scheme_ids: sess.eligible_scheme_ids, grounding_report: sess.grounding_report, language_review_report: sess.language_review_report }, null, 2))}</pre>
  `;
}

// ============================================================================
// TAB 3: 10-Profile Precision & Recall Benchmark Evaluation
// ============================================================================

async function runEvaluationBenchmark() {
  const btn = document.getElementById("runEvalBtn");
  btn.disabled = true;
  btn.textContent = "Running 10 Profiles...";
  try {
    const res = await fetch("/api/v1/evaluate", { method: "POST" });
    const summary = await res.json();
    renderEvaluationSummary(summary);
  } catch (err) {
    alert(`Evaluation failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "Run 10-Profile Evaluation";
  }
}

async function loadEvaluationHistory() {
  try {
    const res = await fetch("/api/v1/evaluation-history?limit=1");
    const list = await res.json();
    if (list && list.length) {
      renderEvaluationSummary(list[0]);
    }
  } catch (_) {}
}

function renderEvaluationSummary(summary) {
  const kpiBox = document.getElementById("evalSummaryCards");
  kpiBox.innerHTML = `
    <div class="kpi-box"><div class="kpi-val">${(summary.macro_precision * 100).toFixed(1)}%</div><div class="kpi-lbl">Macro Precision</div></div>
    <div class="kpi-box"><div class="kpi-val">${(summary.macro_recall * 100).toFixed(1)}%</div><div class="kpi-lbl">Macro Recall</div></div>
    <div class="kpi-box"><div class="kpi-val">${(summary.macro_f1 * 100).toFixed(1)}%</div><div class="kpi-lbl">Macro F1 Score</div></div>
    <div class="kpi-box"><div class="kpi-val">${(summary.micro_precision * 100).toFixed(1)}%</div><div class="kpi-lbl">Micro Precision</div></div>
    <div class="kpi-box"><div class="kpi-val">${(summary.micro_recall * 100).toFixed(1)}%</div><div class="kpi-lbl">Micro Recall</div></div>
    <div class="kpi-box"><div class="kpi-val">${(summary.grounding_pass_rate * 100).toFixed(0)}%</div><div class="kpi-lbl">Grounding Pass Rate</div></div>
    <div class="kpi-box"><div class="kpi-val">${(summary.language_consistency_rate * 100).toFixed(0)}%</div><div class="kpi-lbl">Language Consistent</div></div>
    <div class="kpi-box"><div class="kpi-val">${(summary.scheme_name_preservation_rate * 100).toFixed(0)}%</div><div class="kpi-lbl">Scheme Names Intact</div></div>
  `;

  const rows = (summary.profile_results || [])
    .map(
      (r) => `
    <tr>
      <td><b>${escapeHtml(r.profile_id)}</b><br/><span class="badge badge-info">${escapeHtml(r.language)}</span></td>
      <td>${escapeHtml(r.label)}</td>
      <td>${r.expected_scheme_ids.join(", ") || "<i>None (Negative Control)</i>"}</td>
      <td>${r.predicted_scheme_ids.join(", ") || "<i>None</i>"}</td>
      <td><b>${r.precision.toFixed(2)}</b></td>
      <td><b>${r.recall.toFixed(2)}</b></td>
      <td>${r.grounding_passed ? "✓" : "✗"} / ${r.language_consistent ? "✓" : "✗"} / ${r.scheme_names_intact ? "✓" : "✗"}</td>
      <td>${r.latency_ms.toFixed(1)} ms</td>
    </tr>`
    )
    .join("");

  document.getElementById("evalTableContainer").innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID / Lang</th>
          <th>Citizen Profile</th>
          <th>Expected Schemes</th>
          <th>Predicted Schemes</th>
          <th>Precision</th>
          <th>Recall</th>
          <th>Ground / Lang / Name</th>
          <th>Latency</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

// ============================================================================
// TAB 4: Scheme Knowledge Base (Search/Filter) & Redis Cache Inspector
// ============================================================================

async function loadCacheStats() {
  const box = document.getElementById("redisStatsBox");
  try {
    const res = await fetch("/api/v1/cache/stats");
    const stats = await res.json();
    const audits = (stats.recent_query_audits || [])
      .map(
        (a) =>
          `<tr><td><code>${escapeHtml(a.query_hash.slice(0, 10))}...</code></td><td>${escapeHtml(a.language)}</td><td><span class="badge ${a.cache_status.includes("hit") ? "badge-success" : "badge-info"}">${escapeHtml(a.cache_status)}</span></td><td>${a.similarity_score ?? "-"}</td><td>${a.latency_ms} ms</td></tr>`
      )
      .join("");

    box.innerHTML = `
      <div class="kpi-grid">
        <div class="kpi-box"><div class="kpi-val">${escapeHtml(stats.backend)}</div><div class="kpi-lbl">Cache Backend</div></div>
        <div class="kpi-box"><div class="kpi-val">${stats.total_keys}</div><div class="kpi-lbl">Active Keys</div></div>
        <div class="kpi-box"><div class="kpi-val">${stats.hits}</div><div class="kpi-lbl">Cache Hits</div></div>
        <div class="kpi-box"><div class="kpi-val">${(stats.hit_rate * 100).toFixed(1)}%</div><div class="kpi-lbl">Hit Rate</div></div>
      </div>
      <h3 class="sub-heading">Recent Query Cache Telemetry (PostgreSQL Audit)</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Query Hash</th><th>Lang</th><th>Status</th><th>Similarity</th><th>Latency</th></tr></thead>
          <tbody>${audits || '<tr><td colspan="5" class="muted">No queries recorded yet.</td></tr>'}</tbody>
        </table>
      </div>
    `;
  } catch (err) {
    box.innerHTML = `<p class="muted">Cache stats unavailable: ${escapeHtml(err.message)}</p>`;
  }
}

async function flushRedisCache() {
  await fetch("/api/v1/cache/flush", { method: "POST" });
  await loadCacheStats();
}

async function loadSchemesCatalog() {
  try {
    const res = await fetch("/api/v1/schemes");
    cachedSchemesCatalog = await res.json();
    renderKbCategoryButtons();
    renderFilteredSchemes();
  } catch (err) {
    document.getElementById("schemesCatalogBox").innerHTML = `<p class="muted">Could not load schemes catalog: ${escapeHtml(err.message)}</p>`;
  }
}

function renderKbCategoryButtons() {
  const categories = [
    { key: "all", label: "All" },
    { key: "farmer", label: "Farmer" },
    { key: "women", label: "Women & Child" },
    { key: "student", label: "Student" },
    { key: "senior", label: "Senior / Widow / Disability" },
    { key: "housing", label: "Health & Housing" },
    { key: "artisan", label: "Artisan & Business" },
  ];
  const bar = document.getElementById("kbCategoryFilters");
  bar.innerHTML = "";
  categories.forEach((cat) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `sample-chip ${activeKbCategory === cat.key ? "active-filter" : ""}`;
    btn.textContent = cat.label;
    btn.addEventListener("click", () => {
      activeKbCategory = cat.key;
      renderKbCategoryButtons();
      renderFilteredSchemes();
    });
    bar.appendChild(btn);
  });
}

function renderFilteredSchemes() {
  const box = document.getElementById("schemesCatalogBox");
  const term = (document.getElementById("kbSearchInput")?.value || "").trim().toLowerCase();

  const matchesCategory = (s) => {
    if (activeKbCategory === "all") return true;
    const blob = `${s.official_name} ${(s.target_tags || []).join(" ")} ${s.benefit_summary}`.toLowerCase();
    if (activeKbCategory === "women") return /women|pregnant|widow|girl|lpg|maternity/.test(blob);
    if (activeKbCategory === "senior") return /elderly|old age|widow|disability|pension|divyang/.test(blob);
    if (activeKbCategory === "housing") return /house|health|hospital|lpg/.test(blob);
    if (activeKbCategory === "artisan") return /artisan|vendor|business|mudra|vishwakarma/.test(blob);
    return blob.includes(activeKbCategory);
  };

  const filtered = cachedSchemesCatalog.filter((s) => {
    if (!matchesCategory(s)) return false;
    if (!term) return true;
    const haystack = `${s.scheme_id} ${s.official_name} ${s.ministry} ${s.benefit_summary} ${(s.target_tags || []).join(" ")}`.toLowerCase();
    return haystack.includes(term);
  });

  document.getElementById("kbCountBadge").textContent = `${filtered.length} / ${cachedSchemesCatalog.length} Schemes`;
  box.innerHTML = filtered.length
    ? filtered
        .map(
          (s) => `
      <div class="kb-item">
        <strong>${escapeHtml(s.official_name)}</strong> <span class="badge badge-info">${escapeHtml(s.scheme_id)}</span>
        <div class="muted">${escapeHtml(s.benefit_summary)}</div>
        <div class="muted">Portal: <a href="${s.official_portal}" target="_blank" rel="noopener">${s.official_portal}</a> · Helpline: ${escapeHtml(s.helpline)}</div>
      </div>`
        )
        .join("")
    : `<p class="muted">No schemes match the active search or category filter.</p>`;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
