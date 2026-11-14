/**
 * CitizenVoiceController (Single Responsibility + Adapter Pattern)
 * Encapsulates Multilingual Voice Input (SpeechRecognition STT) and Audio Output
 * (SpeechSynthesis TTS + Voice Microservice Speech Sanitizer) for all 12 citizen languages.
 *
 * Designed with defensive progressive enhancement: if a browser lacks Web Speech API
 * support, regional OS voice packs, or microphone permissions, normal text/form
 * operation continues undisturbed.
 */

class CitizenVoiceController {
  /**
   * @param {Object} options
   * @param {(text: string, isFinal: boolean) => void} options.onTranscript - Called as user speaks
   * @param {(state: Object) => void} options.onStatusChange - UI telemetry callback
   */
  constructor({ onTranscript, onStatusChange } = {}) {
    this.onTranscript = onTranscript || (() => {});
    this.onStatusChange = onStatusChange || (() => {});

    // Feature detection guards
    this.SpeechRecognitionCtor =
      window.SpeechRecognition || window.webkitSpeechRecognition || null;
    this.synth = window.speechSynthesis || null;

    this.localesByCode = {};
    this.orderedLocales = [];
    this.recognition = null;
    this.isListening = false;
    this.isSpeaking = false;
    this.isPaused = false;
    this.speechRate = 1.0;
    this._activePlaybackToken = 0;

    // Static fallback map in case /api/v1/voice/locales hasn't loaded yet
    this._fallbackBcp47 = {
      en: { language: "en", display_name: "English", native_name: "English", bcp47_tag: "en-IN", rtl: false, recommended_rate: 1.0 },
      hi: { language: "hi", display_name: "Hindi", native_name: "हिन्दी", bcp47_tag: "hi-IN", rtl: false, recommended_rate: 0.96 },
      pa: { language: "pa", display_name: "Punjabi", native_name: "ਪੰਜਾਬੀ", bcp47_tag: "pa-IN", rtl: false, recommended_rate: 0.96 },
      te: { language: "te", display_name: "Telugu", native_name: "తెలుగు", bcp47_tag: "te-IN", rtl: false, recommended_rate: 0.96 },
      ta: { language: "ta", display_name: "Tamil", native_name: "தமிழ்", bcp47_tag: "ta-IN", rtl: false, recommended_rate: 0.96 },
      bn: { language: "bn", display_name: "Bengali", native_name: "বাংলা", bcp47_tag: "bn-IN", rtl: false, recommended_rate: 0.96 },
      mr: { language: "mr", display_name: "Marathi", native_name: "मराठी", bcp47_tag: "mr-IN", rtl: false, recommended_rate: 0.96 },
      kn: { language: "kn", display_name: "Kannada", native_name: "ಕನ್ನಡ", bcp47_tag: "kn-IN", rtl: false, recommended_rate: 0.96 },
      gu: { language: "gu", display_name: "Gujarati", native_name: "ગુજરાતી", bcp47_tag: "gu-IN", rtl: false, recommended_rate: 0.96 },
      ml: { language: "ml", display_name: "Malayalam", native_name: "മലയാളം", bcp47_tag: "ml-IN", rtl: false, recommended_rate: 0.96 },
      or: { language: "or", display_name: "Odia", native_name: "ଓଡ଼ିଆ", bcp47_tag: "or-IN", rtl: false, recommended_rate: 0.96 },
      ur: { language: "ur", display_name: "Urdu", native_name: "اردو", bcp47_tag: "ur-IN", rtl: true, recommended_rate: 0.95 },
    };

    // Pre-warm asynchronous browser voice list when available
    if (this.synth && typeof this.synth.onvoiceschanged !== "undefined") {
      this.synth.onvoiceschanged = () => {
        this._emitStatus("ready");
      };
    }
  }

  /** Whether Speech-to-Text microphone input is available in this browser. */
  get canListen() {
    return Boolean(this.SpeechRecognitionCtor);
  }

  /** Whether Text-to-Speech synthesis is available in this browser. */
  get canSpeak() {
    return Boolean(this.synth && typeof window.SpeechSynthesisUtterance !== "undefined");
  }

  /** Load authoritative BCP-47 voice specs from the Voice & Speech Microservice. */
  async loadLocales() {
    try {
      const res = await fetch("/api/v1/voice/locales");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const list = await res.json();
      this.orderedLocales = list;
      this.localesByCode = {};
      list.forEach((loc) => {
        this.localesByCode[loc.language] = loc;
      });
    } catch (_) {
      // Non-fatal fallback so voice UI remains operational offline
      this.orderedLocales = Object.values(this._fallbackBcp47);
      this.localesByCode = { ...this._fallbackBcp47 };
    }
    this._emitStatus("ready");
    return this.orderedLocales;
  }

  /** Resolve voice locale metadata for a citizen LanguageCode (empty string defaults to en-IN). */
  getLocaleSpec(langCode) {
    const key = langCode || "en";
    return this.localesByCode[key] || this._fallbackBcp47[key] || this._fallbackBcp47.en;
  }

  /** Find best matching OS/Browser SpeechSynthesisVoice for a BCP-47 tag (e.g., pa-IN -> pa). */
  _pickVoice(bcp47Tag) {
    if (!this.synth) return null;
    const voices = this.synth.getVoices() || [];
    if (!voices.length) return null;
    const normTag = bcp47Tag.toLowerCase();
    const baseLang = normTag.split("-")[0];

    return (
      voices.find((v) => v.lang && v.lang.toLowerCase() === normTag) ||
      voices.find((v) => v.lang && v.lang.toLowerCase().startsWith(`${baseLang}-`)) ||
      voices.find((v) => v.lang && v.lang.toLowerCase() === baseLang) ||
      voices.find((v) => v.lang && v.lang.toLowerCase().includes("in")) ||
      voices[0]
    );
  }

  /** Start or toggle microphone dictation for the chosen citizen language. */
  toggleListening(langCode) {
    if (this.isListening) {
      this.stopListening();
      return false;
    }
    if (!this.canListen) {
      this._emitStatus("unsupported_stt", "Browser Speech Recognition unavailable; type your query freely.");
      return false;
    }

    // Halt active TTS playback so the microphone does not hear our own speech
    this.stopSpeaking();

    const spec = this.getLocaleSpec(langCode);
    const recognition = new this.SpeechRecognitionCtor();
    recognition.lang = spec.bcp47_tag;
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;

    let finalBuffer = "";
    recognition.onstart = () => {
      this.isListening = true;
      this._emitStatus("listening", `Listening in ${spec.display_name} (${spec.bcp47_tag})...`);
    };

    recognition.onresult = (event) => {
      let interimText = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const piece = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalBuffer += `${piece} `;
        } else {
          interimText += piece;
        }
      }
      const combined = (finalBuffer || interimText).trim();
      this.onTranscript(combined, Boolean(finalBuffer.trim()));
      if (interimText && !finalBuffer) {
        this._emitStatus("listening", `Heard: "${interimText.trim()}"`);
      }
    };

    recognition.onerror = (event) => {
      this.isListening = false;
      this.recognition = null;
      const reason =
        event.error === "not-allowed"
          ? "Microphone permission denied. Typing works normally."
          : event.error === "no-speech"
          ? "No speech detected. Try speaking again or typing."
          : `Voice input (${spec.bcp47_tag}): ${event.error}`;
      this._emitStatus("stt_error", reason);
    };

    recognition.onend = () => {
      const hadFinal = Boolean(finalBuffer.trim());
      this.isListening = false;
      this.recognition = null;
      this._emitStatus("idle", hadFinal ? `Voice transcript captured (${spec.bcp47_tag}).` : "Voice input stopped.");
    };

    this.recognition = recognition;
    try {
      recognition.start();
      return true;
    } catch (err) {
      this.isListening = false;
      this.recognition = null;
      this._emitStatus("stt_error", `Unable to start microphone: ${err.message}`);
      return false;
    }
  }

  stopListening() {
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (_) {}
      this.recognition = null;
    }
    this.isListening = false;
    this._emitStatus("idle");
  }

  setRate(rateVal) {
    const parsed = parseFloat(rateVal);
    if (!Number.isNaN(parsed) && parsed >= 0.6 && parsed <= 1.6) {
      this.speechRate = parsed;
    }
  }

  /**
   * Call backend Voice & Speech Microservice (/api/v1/voice/prepare-speech) to clean Markdown
   * and slice text into safe utterance chunks, then play sequentially in the citizen's language.
   */
  async speakGuide(rawText, langCode) {
    if (!this.canSpeak) {
      this._emitStatus("unsupported_tts", "Text-to-Speech unavailable in this browser.");
      return;
    }
    this.stopSpeaking();

    const spec = this.getLocaleSpec(langCode);
    let segments = [];
    let bcp47 = spec.bcp47_tag;
    let rate = this.speechRate || spec.recommended_rate || 1.0;

    try {
      const res = await fetch("/api/v1/voice/prepare-speech", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: rawText, language: spec.language }),
      });
      if (res.ok) {
        const prepared = await res.json();
        segments = prepared.segments || [prepared.spoken_text || rawText];
        bcp47 = prepared.bcp47_tag || bcp47;
      }
    } catch (_) {
      // Safe client-side strip fallback if Gateway unreachable
      segments = rawText
        .replace(/https?:\/\/\S+/g, "")
        .replace(/[#*_`>|]/g, " ")
        .split(/(?<=[.!?।॥۔])\s+/)
        .filter((s) => s.trim().length > 0);
    }

    if (!segments.length) return;
    this._playSegments(segments, bcp47, rate, spec.display_name);
  }

  _playSegments(segments, bcp47Tag, rate, displayName) {
    if (!this.synth) return;
    const token = ++this._activePlaybackToken;
    this.isSpeaking = true;
    this.isPaused = false;

    const chosenVoice = this._pickVoice(bcp47Tag);
    let index = 0;

    const speakNext = () => {
      if (token !== this._activePlaybackToken) return;
      if (index >= segments.length) {
        this.isSpeaking = false;
        this.isPaused = false;
        this._emitStatus("tts_done", `Finished reading in ${displayName} (${bcp47Tag}).`);
        return;
      }

      const chunk = segments[index];
      this._emitStatus("speaking", `Reading aloud (${displayName} · segment ${index + 1}/${segments.length})`);

      const utter = new SpeechSynthesisUtterance(chunk);
      utter.lang = bcp47Tag;
      utter.rate = this.speechRate || rate;
      if (chosenVoice) {
        utter.voice = chosenVoice;
      }

      utter.onend = () => {
        index += 1;
        speakNext();
      };
      utter.onerror = () => {
        index += 1;
        speakNext();
      };
      this.synth.speak(utter);
    };

    speakNext();
  }

  togglePauseResume() {
    if (!this.synth || !this.isSpeaking) return;
    if (this.isPaused) {
      this.synth.resume();
      this.isPaused = false;
      this._emitStatus("speaking", "Audio resumed.");
    } else {
      this.synth.pause();
      this.isPaused = true;
      this._emitStatus("paused", "Audio paused.");
    }
  }

  stopSpeaking() {
    this._activePlaybackToken += 1;
    if (this.synth) {
      try {
        this.synth.cancel();
      } catch (_) {}
    }
    const wasSpeaking = this.isSpeaking;
    this.isSpeaking = false;
    this.isPaused = false;
    if (wasSpeaking) {
      this._emitStatus("idle", "Audio stopped.");
    }
  }

  _emitStatus(code, message = "") {
    this.onStatusChange({
      code,
      message,
      isListening: this.isListening,
      isSpeaking: this.isSpeaking,
      isPaused: this.isPaused,
      canListen: this.canListen,
      canSpeak: this.canSpeak,
    });
  }
}

window.CitizenVoiceController = CitizenVoiceController;

