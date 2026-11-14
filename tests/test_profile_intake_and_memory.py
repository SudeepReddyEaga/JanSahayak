"""Tests for ProfileIntakeAgent multilingual extraction and shared UserProfileMemory auditing."""

import asyncio

from shared.data.language_packs import LanguagePackRegistry
from shared.domain.enums import LanguageCode
from shared.domain.models import ApplicationGuideRequest


def test_multilingual_script_detection_and_extraction():
    """Verify automatic language detection and field extraction across Indic scripts and English."""
    # Hindi rural farmer with Devanagari digits
    p_hi = LanguagePackRegistry.extract_profile_from_text(
        "मैं ६५ साल का किसान हूं, गांव में रहता हूं, २ एकड़ जमीन है, आय 90000 रुपये है, BPL कार्ड है और पक्का घर नहीं है।"
    )
    assert p_hi.language == LanguageCode.HINDI
    assert p_hi.age == 65
    assert p_hi.occupation == "farmer"
    assert p_hi.residence_type == "rural"
    assert p_hi.owns_cultivable_land is True
    assert p_hi.land_acres == 2.0
    assert p_hi.annual_income_inr == 90000
    assert p_hi.has_bpl_card is True
    assert p_hi.owns_pucca_house is False

    # Marathi potter (disambiguated from Hindi despite shared Devanagari script)
    p_mr = LanguagePackRegistry.extract_profile_from_text(
        "मी 38 वर्षांचा ग्रामीण भागातील कुंभार कारागीर आहे. माझे वार्षिक उत्पन्न 140000 रुपये आहे, मला पक्के घर नाही आणि मी सरकारी नोकरदार नाही."
    )
    assert p_mr.language == LanguageCode.MARATHI
    assert p_mr.age == 38
    assert p_mr.occupation == "artisan"
    assert p_mr.owns_pucca_house is False
    assert p_mr.is_govt_employee is False

    # Bengali street vendor with Bengali digits
    p_bn = LanguagePackRegistry.extract_profile_from_text(
        "আমি ৩৪ বছর বয়সী শহরের একজন রাস্তার হকার। আমার বার্ষিক আয় ১৮০০০০ টাকা এবং আমি সরকারি কর্মচারী নই।"
    )
    assert p_bn.language == LanguageCode.BENGALI
    assert p_bn.age == 34
    assert p_bn.occupation == "street_vendor"
    assert p_bn.annual_income_inr == 180000
    assert p_bn.is_govt_employee is False


def test_all_six_agents_read_and_write_shared_memory(pipeline_bundle):
    """Verify every agent in the sequential pipeline both reads and writes UserProfileMemory."""
    pipeline = pipeline_bundle["pipeline"]
    req = ApplicationGuideRequest(
        query="I am a 20-year-old male undergraduate student in OBC category in an urban city with family income 180000 INR.",
        session_id="mem-audit-session",
        bypass_cache=True,
    )
    resp = asyncio.run(pipeline.run(req))

    # Confirm every agent stage executed and produced audit reads & writes
    read_agents = {e.agent for e in resp.memory_audit_log if e.action == "read"}
    write_agents = {e.agent for e in resp.memory_audit_log if e.action == "write"}

    expected_agents = {
        "ProfileIntakeAgent",
        "SchemeRetrievalAgent",
        "EligibilityRuleAgent",
        "DocumentChecklistAgent",
        "GuideManagerAgent",
        "LanguageReviewerAgent",
    }
    assert expected_agents.issubset(read_agents)
    assert expected_agents.issubset(write_agents)
