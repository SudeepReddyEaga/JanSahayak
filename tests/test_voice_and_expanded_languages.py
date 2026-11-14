"""
Tests for Voice & Speech Microservice (Port 8004), Expanded 12 Citizen Languages
(Punjabi, Gujarati, Malayalam, Odia, Urdu + existing 7), and UI Q14 Removal.
"""

import asyncio
from pathlib import Path

import pytest

from services.voice_speech_service.service import (
    SpeechTextSanitizerService,
    VoiceLocaleRegistryService,
)
from shared.data.language_packs import LANGUAGE_TEMPLATES, LanguagePackRegistry
from shared.data.schemes_catalog import SCHEMES_CATALOG
from shared.domain.enums import LanguageCode
from shared.domain.models import ApplicationGuideRequest


def test_all_12_languages_registered_across_templates_catalog_and_voice():
    """Verify 100% parity across LanguageCode enum, UI templates, catalog, and Voice service."""
    registry = VoiceLocaleRegistryService()
    locales = registry.list_locales()
    locale_map = {loc.language: loc for loc in locales}

    assert len(LanguageCode) == 12
    assert len(locales) == 12

    for lang in LanguageCode:
        assert lang.value in LANGUAGE_TEMPLATES, f"Missing template pack for {lang.value}"
        assert lang in locale_map, f"Missing voice locale spec for {lang.value}"
        assert locale_map[lang].bcp47_tag.endswith("-IN")
        for scheme in SCHEMES_CATALOG:
            assert lang.value in scheme.localized_summaries, (
                f"Scheme {scheme.scheme_id} missing summary localization for {lang.value}"
            )

    assert locale_map[LanguageCode.PUNJABI].bcp47_tag == "pa-IN"
    assert locale_map[LanguageCode.URDU].rtl is True
    assert locale_map[LanguageCode.HINDI].rtl is False


def test_speech_sanitizer_strips_markdown_preserves_scheme_names_and_chunks():
    """Verify Markdown-to-Speech sanitization creates short browser-safe chunks without altering scheme titles."""
    registry = VoiceLocaleRegistryService()
    sanitizer = SpeechTextSanitizerService(registry)

    sample_markdown = (
        "## **Eligible Government Welfare Schemes**\n"
        "- **Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)**: ₹6,000/year. "
        "Official Portal: https://pmkisan.gov.in\n"
        "- Follow steps at Gram Panchayat or Common Service Centre. "
        "Verify Aadhaar card, land records, and DBT bank account passbook at the branch office carefully before applying online."
    )
    payload = sanitizer.prepare_speech(text=sample_markdown, language=LanguageCode.PUNJABI)

    assert payload.bcp47_tag == "pa-IN"
    assert payload.rtl is False
    assert "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)" in payload.spoken_text
    assert "https://" not in payload.spoken_text
    assert "**" not in payload.spoken_text
    assert "##" not in payload.spoken_text
    assert len(payload.segments) >= 1
    assert all(len(seg) <= 220 for seg in payload.segments)


@pytest.mark.parametrize(
    "lang,query,expected_subset",
    [
        (
            LanguageCode.PUNJABI,
            "ਮੈਂ 45 ਸਾਲ ਦਾ ਪੇਂਡੂ ਕਿਸਾਨ ਹਾਂ। ਮੇਰੇ ਕੋਲ 2 ਏਕੜ ਖੇਤੀ ਵਾਲੀ ਜ਼ਮੀਨ ਹੈ, ਸਾਲਾਨਾ ਆਮਦਨ 95000 ਰੁਪਏ ਹੈ, ਬੀਪੀਐਲ ਕਾਰਡ ਹੈ, ਪੱਕਾ ਘਰ ਨਹੀਂ ਹੈ ਅਤੇ ਸਰਕਾਰੀ ਕਰਮਚਾਰੀ ਨਹੀਂ ਹਾਂ।",
            {"PM-KISAN", "PMFBY", "PMAY-G", "AB-PMJAY", "MGNREGA"},
        ),
        (
            LanguageCode.GUJARATI,
            "હું 40 વર્ષનો ગ્રામીણ ખેડૂત છું, મારી પાસે 2 એકર ખેતીની જમીન છે, વાર્ષિક આવક 90000 રૂપિયા છે, બીપીએલ કાર્ડ છે, પાકું ઘર નથી અને હું સરકારી કર્મચારી નથી.",
            {"PM-KISAN", "PMFBY", "PMAY-G", "AB-PMJAY", "MGNREGA"},
        ),
        (
            LanguageCode.MALAYALAM,
            "ഞാൻ 36 വയസ്സുള്ള ഗ്രാമീണ കൈത്തൊഴിലാളിയാണ്, വാർഷിക വരുമാനം 95000 രൂപയാണ്, പക്കാ വീട് ഇല്ല, ബിപിഎൽ കാർഡ് ഉണ്ട്, സർക്കാർ ജീവനക്കാരനല്ല.",
            {"PM-VISHWAKARMA", "PMAY-G", "AB-PMJAY", "MGNREGA"},
        ),
        (
            LanguageCode.ODIA,
            "ମୁଁ 27 ବର୍ଷର ଗ୍ରାମୀଣ ଗର୍ଭବତୀ ମହିଳା ଅଟେ, ମୋର ବିପିଏଲ୍ କାର୍ଡ ଅଛି, ବାର୍ଷିକ ଆୟ 85000 ଟଙ୍କା, ଗ୍ୟାସ୍ ସଂଯୋଗ ନାହିଁ ଏବଂ ସରକାରୀ କର୍ମଚାରୀ ନୁହେଁ।",
            {"PMMVY", "PMUY", "AB-PMJAY"},
        ),
        (
            LanguageCode.URDU,
            "میں 38 سال کا دیہی کسان ہوں، میرے پاس 2 ایکڑ زرعی زمین ہے، سالانہ آمدنی 110000 روپے ہے، میری 6 سال کی بیٹی ہے اور میں سرکاری ملازم نہیں ہوں۔",
            {"PM-KISAN", "PMFBY", "SSY", "MGNREGA"},
        ),
    ],
)
def test_expanded_languages_end_to_end_pipeline(pipeline_bundle, lang, query, expected_subset):
    """Verify Punjabi, Gujarati, Malayalam, Odia, and Urdu queries succeed through all 6 agents."""
    # Auto-detect script without explicit preferred_language override first
    detected = LanguagePackRegistry.detect_language(query)
    assert detected == lang

    resp = asyncio.run(
        pipeline_bundle["pipeline"].run(
            ApplicationGuideRequest(query=query, bypass_cache=True)
        )
    )
    assert resp.detected_language == lang
    predicted_ids = {s.scheme_id for s in resp.eligible_schemes}
    assert expected_subset.issubset(predicted_ids), (
        f"Expected {expected_subset} in {predicted_ids} for lang={lang.value}"
    )
    assert resp.grounding_report.passed is True
    assert resp.language_review_report.language_consistent is True
    assert resp.language_review_report.scheme_names_intact is True


def test_api_gateway_voice_endpoints_and_ui_clean(api_client):
    """Verify Gateway voice endpoints work cleanly and Q14 branding is absent from UI & OpenAPI."""
    root = Path(__file__).resolve().parent.parent
    index_html = (root / "services" / "frontend_ui" / "static" / "index.html").read_text(encoding="utf-8")
    app_js = (root / "services" / "frontend_ui" / "static" / "app.js").read_text(encoding="utf-8")
    assert "q14" not in index_html.lower()
    assert "q14" not in app_js.lower()

    # Check HTML response & voice controller static bundle
    html_res = api_client.get("/")
    assert html_res.status_code == 200
    assert "q14" not in html_res.text.lower()
    assert 'value="pa"' in html_res.text
    assert 'value="ur"' in html_res.text

    voice_js_res = api_client.get("/static/voice_controller.js")
    assert voice_js_res.status_code == 200
    assert "CitizenVoiceController" in voice_js_res.text

    # Check voice REST endpoints via Gateway
    loc_res = api_client.get("/api/v1/voice/locales")
    assert loc_res.status_code == 200
    locs = loc_res.json()
    assert len(locs) == 12
    assert any(loc["language"] == "pa" and loc["bcp47_tag"] == "pa-IN" for loc in locs)
    assert any(loc["language"] == "ur" and loc["rtl"] is True for loc in locs)

    prep_res = api_client.post(
        "/api/v1/voice/prepare-speech",
        json={
            "text": "## Sukanya Samriddhi Yojana (SSY)\nGet 8.2% p.a. at https://nsiindia.gov.in",
            "language": "ur",
        },
    )
    assert prep_res.status_code == 200
    prep_json = prep_res.json()
    assert prep_json["bcp47_tag"] == "ur-IN"
    assert prep_json["rtl"] is True
    assert "Sukanya Samriddhi Yojana (SSY)" in prep_json["spoken_text"]

