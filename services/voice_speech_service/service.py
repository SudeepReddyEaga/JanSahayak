"""
Core Domain Services for Voice & Speech Microservice.
Follows SRP, OCP, and DIP by implementing IVoiceLocaleRegistry and ISpeechTextSanitizer
independently from HTTP transport (FastAPI) and frontend Web Speech API synthesis.
"""

import re

from shared.domain.enums import LanguageCode
from shared.domain.models import PreparedSpeechPayload, VoiceLocaleSpec
from shared.interfaces.voice_interface import ISpeechTextSanitizer, IVoiceLocaleRegistry


class VoiceLocaleRegistryService(IVoiceLocaleRegistry):
    """
    Open/Closed locale table mapping every LanguageCode in the platform to its
    standard BCP-47 speech locale tag, native script label, RTL flag, and spoken sample.
    """

    # Declarative registry (add new citizen languages simply by appending a spec)
    _LOCALES: dict[LanguageCode, VoiceLocaleSpec] = {
        LanguageCode.ENGLISH: VoiceLocaleSpec(
            language=LanguageCode.ENGLISH,
            display_name="English",
            native_name="English",
            bcp47_tag="en-IN",
            tts_rate_default=1.0,
            rtl=False,
            sample_spoken_prompt="I am a 45 year old rural farmer with 2 acres of land and annual income Rs 90000",
        ),
        LanguageCode.HINDI: VoiceLocaleSpec(
            language=LanguageCode.HINDI,
            display_name="Hindi",
            native_name="हिन्दी",
            bcp47_tag="hi-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="मैं 45 साल का किसान हूं, मेरे पास 2 एकड़ जमीन है और सालाना आय 90000 रुपये है",
        ),
        LanguageCode.PUNJABI: VoiceLocaleSpec(
            language=LanguageCode.PUNJABI,
            display_name="Punjabi",
            native_name="ਪੰਜਾਬੀ",
            bcp47_tag="pa-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="ਮੈਂ 42 ਸਾਲ ਦਾ ਪੇਂਡੂ ਕਿਸਾਨ ਹਾਂ, ਮੇਰੇ ਕੋਲ 2 ਏਕੜ ਜ਼ਮੀਨ ਹੈ ਅਤੇ ਸਾਲਾਨਾ ਆਮਦਨ 95000 ਰੁਪਏ ਹੈ",
        ),
        LanguageCode.TELUGU: VoiceLocaleSpec(
            language=LanguageCode.TELUGU,
            display_name="Telugu",
            native_name="తెలుగు",
            bcp47_tag="te-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="నేను 45 సంవత్సరాల రైతును, నాకు 2 ఎకరాల భూమి ఉంది మరియు వార్షిక ఆదాయం 85000 రూపాయలు",
        ),
        LanguageCode.TAMIL: VoiceLocaleSpec(
            language=LanguageCode.TAMIL,
            display_name="Tamil",
            native_name="தமிழ்",
            bcp47_tag="ta-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="நான் 38 வயது விவசாயி, 1.5 ஏக்கர் நிலம் உள்ளது, ஆண்டு வருமானம் 80000 ரூபாய்",
        ),
        LanguageCode.BENGALI: VoiceLocaleSpec(
            language=LanguageCode.BENGALI,
            display_name="Bengali",
            native_name="বাংলা",
            bcp47_tag="bn-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="আমি ৩২ বছর বয়সী গ্রামীণ মহিলা, বিপিএল কার্ড আছে এবং বার্ষিক আয় ৭০০০০ টাকা",
        ),
        LanguageCode.MARATHI: VoiceLocaleSpec(
            language=LanguageCode.MARATHI,
            display_name="Marathi",
            native_name="मराठी",
            bcp47_tag="mr-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="मी 35 वर्षांचा ग्रामीण कारागीर आहे, वार्षिक उत्पन्न 110000 रुपये आहे",
        ),
        LanguageCode.KANNADA: VoiceLocaleSpec(
            language=LanguageCode.KANNADA,
            display_name="Kannada",
            native_name="ಕನ್ನಡ",
            bcp47_tag="kn-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="ನಾನು 68 ವರ್ಷದ ಹಿರಿಯ ನಾಗರಿಕ, ಬಿಪಿಎಲ್ ಕಾರ್ಡ್ ಇದೆ ಮತ್ತು ವಾರ್ಷಿಕ ಆದಾಯ 45000 ರೂಪಾಯಿ",
        ),
        LanguageCode.GUJARATI: VoiceLocaleSpec(
            language=LanguageCode.GUJARATI,
            display_name="Gujarati",
            native_name="ગુજરાતી",
            bcp47_tag="gu-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="હું 40 વર્ષનો ગ્રામીણ ખેડૂત છું, મારી પાસે 2 એકર જમીન છે અને વાર્ષિક આવક 90000 રૂપિયા છે",
        ),
        LanguageCode.MALAYALAM: VoiceLocaleSpec(
            language=LanguageCode.MALAYALAM,
            display_name="Malayalam",
            native_name="മലയാളം",
            bcp47_tag="ml-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="ഞാൻ 36 വയസ്സുള്ള ഗ്രാമീണ കൈത്തൊഴിലാളിയാണ്, വാർഷിക വരുമാനം 95000 രൂപയാണ്",
        ),
        LanguageCode.ODIA: VoiceLocaleSpec(
            language=LanguageCode.ODIA,
            display_name="Odia",
            native_name="ଓଡ଼ିଆ",
            bcp47_tag="or-IN",
            tts_rate_default=0.96,
            rtl=False,
            sample_spoken_prompt="ମୁଁ 44 ବର୍ଷର ଗ୍ରାମୀଣ ଚାଷୀ ଅଟେ, ମୋ ପାଖରେ 2 ଏକର ଜମି ଅଛି ଏବଂ ବାର୍ଷିକ ଆୟ 80000 ଟଙ୍କା",
        ),
        LanguageCode.URDU: VoiceLocaleSpec(
            language=LanguageCode.URDU,
            display_name="Urdu",
            native_name="اردو",
            bcp47_tag="ur-IN",
            tts_rate_default=0.95,
            rtl=True,
            sample_spoken_prompt="میں 50 سال کا دیہی کسان ہوں، میرے پاس 2 ایکڑ زمین ہے اور سالانہ آمدنی 90000 روپے ہے",
        ),
    }

    def list_locales(self) -> list[VoiceLocaleSpec]:
        """Return ordered list of VoiceLocaleSpec entries for all 12 citizen languages."""
        return list(self._LOCALES.values())

    def get_locale(self, language: LanguageCode) -> VoiceLocaleSpec:
        """Resolve exact VoiceLocaleSpec for language, safely falling back to English."""
        return self._LOCALES.get(language, self._LOCALES[LanguageCode.ENGLISH])


class SpeechTextSanitizerService(ISpeechTextSanitizer):
    """
    Prepares rich Markdown welfare scheme replies for clean browser Text-to-Speech (TTS).
    Chunking segments to <= 220 characters prevents Chrome/Edge Web Speech API's
    long-utterance silence bug while preserving official scheme names intact.
    """

    # Hard ceiling per spoken chunk so browser SpeechSynthesis plays reliably without stalls
    _MAX_SEGMENT_CHARS = 220

    def __init__(self, locale_registry: IVoiceLocaleRegistry) -> None:
        self.locale_registry = locale_registry

    @classmethod
    def sanitize_markdown_for_speech(cls, text: str) -> str:
        """Strip Markdown formatting, bullet symbols, and verbose URL schemes."""
        # Convert Markdown links [label](url) to label only so URLs are not spelled out
        cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        # Strip bare URL protocol prefixes while keeping readable domain names
        cleaned = re.sub(r"https?://(?:www\.)?", "", cleaned)
        # Strip Markdown headings, bold/italic markers, code ticks, and horizontal rules
        cleaned = re.sub(r"[#*_`~>|]", " ", cleaned)
        cleaned = re.sub(r"^[\s\-•▪●]+", "", cleaned, flags=re.MULTILINE)
        # Convert currency symbol to spoken word friendly form while keeping digits clear
        cleaned = cleaned.replace("₹", "Rs ")
        # Normalize extra spaces while preserving sentence boundaries across scripts
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{2,}", ". ", cleaned)
        cleaned = cleaned.replace("\n", ". ")
        # Collapse duplicate punctuation introduced by newline replacement
        cleaned = re.sub(r"[.\s]{2,}", ". ", cleaned)
        return cleaned.strip()

    @classmethod
    def split_into_spoken_segments(cls, spoken_text: str) -> list[str]:
        """
        Split sanitized speech text into ordered utterances <= _MAX_SEGMENT_CHARS.
        Handles Latin periods (.), Devanagari/Punjabi/Odia danda (।), and Urdu dash (۔).
        """
        if not spoken_text:
            return []

        raw_sentences = re.split(r"(?<=[.!?।॥۔])\s+", spoken_text)
        segments: list[str] = []
        current = ""

        for sentence in raw_sentences:
            piece = sentence.strip()
            if not piece:
                continue
            # If single sentence exceeds max length, subdivide on commas/semicolons
            if len(piece) > cls._MAX_SEGMENT_CHARS:
                if current:
                    segments.append(current)
                    current = ""
                subparts = re.split(r"(?<=[,;:])\s+", piece)
                for sub in subparts:
                    sub_clean = sub.strip()
                    if not sub_clean:
                        continue
                    if len(current) + len(sub_clean) + 1 <= cls._MAX_SEGMENT_CHARS:
                        current = f"{current} {sub_clean}".strip()
                    else:
                        if current:
                            segments.append(current)
                        current = sub_clean[: cls._MAX_SEGMENT_CHARS]
            elif len(current) + len(piece) + 1 <= cls._MAX_SEGMENT_CHARS:
                current = f"{current} {piece}".strip()
            else:
                if current:
                    segments.append(current)
                current = piece

        if current:
            segments.append(current)
        return segments

    def prepare_speech(self, *, text: str, language: LanguageCode) -> PreparedSpeechPayload:
        """Compile sanitized text and speech-chunk array for the target citizen language."""
        spec = self.locale_registry.get_locale(language)
        spoken = self.sanitize_markdown_for_speech(text)
        segments = self.split_into_spoken_segments(spoken)
        return PreparedSpeechPayload(
            language=spec.language,
            bcp47_tag=spec.bcp47_tag,
            display_name=spec.display_name,
            rtl=spec.rtl,
            spoken_text=spoken,
            segments=segments,
            recommended_rate=spec.tts_rate_default,
        )

