"""
Generates the comprehensive 16-slide PowerPoint presentation for JanSahayak AI.
Course: CSE476: Agentic AI / Multi-Agent Systems
Institution: Lovely Professional University
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Palette
    NAVY = RGBColor(15, 23, 42)       # #0f172a
    NAVY_LIGHT = RGBColor(30, 41, 59) # #1e293b
    SAFFRON = RGBColor(234, 88, 12)   # #ea580c (LPU Accent)
    ORANGE_BG = RGBColor(255, 237, 213) # #ffedd5
    TEXT_DARK = RGBColor(15, 23, 42)
    TEXT_MUTED = RGBColor(71, 85, 105) # #475569
    WHITE = RGBColor(255, 255, 255)
    CARD_BG = RGBColor(248, 250, 252)  # #f8fafc
    CARD_BORDER = RGBColor(226, 232, 240) # #e2e8f0
    GREEN = RGBColor(22, 163, 74)     # #16a34a
    BLUE = RGBColor(37, 99, 235)      # #2563eb

    def add_header(slide, title_text, category_text="CSE476: AGENTIC AI · GROUP 14", slide_num=None):
        # Top banner background
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = NAVY
        top_bar.line.fill.background()

        # Accent line under header
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
        line.fill.solid()
        line.fill.fore_color.rgb = SAFFRON
        line.line.fill.background()

        # Category Tracker / Tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(10), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = SAFFRON
        p_cat.font.name = "Arial"

        # Slide Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.38), Inches(11), Inches(0.65))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = "Arial"

        # Footer
        footer_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.02))
        footer_line.fill.solid()
        footer_line.fill.fore_color.rgb = CARD_BORDER
        footer_line.line.fill.background()

        foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(8), Inches(0.35))
        tf_f = foot_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "JanSahayak: Multilingual Government Scheme Eligibility Guide | LPU CSE476"
        p_f.font.size = Pt(9.5)
        p_f.font.color.rgb = TEXT_MUTED
        p_f.font.name = "Arial"

        if slide_num:
            num_box = slide.shapes.add_textbox(Inches(11.5), Inches(7.05), Inches(1.0), Inches(0.35))
            tf_n = num_box.text_frame
            p_n = tf_n.paragraphs[0]
            p_n.alignment = PP_ALIGN.RIGHT
            p_n.text = f"{slide_num} / 17"
            p_n.font.size = Pt(9.5)
            p_n.font.bold = True
            p_n.font.color.rgb = TEXT_MUTED
            p_n.font.name = "Arial"

    def create_card(slide, left, top, width, height, title, bg_color=CARD_BG, border_color=CARD_BORDER, header_color=NAVY):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        if title:
            # Title header ribbon inside card
            t_box = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.12), width - Inches(0.3), Inches(0.45))
            tf = t_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(13.5)
            p.font.bold = True
            p.font.color.rgb = header_color
            p.font.name = "Arial"

        # Content frame
        c_box = slide.shapes.add_textbox(left + Inches(0.18), top + Inches(0.55), width - Inches(0.36), height - Inches(0.65))
        tf_content = c_box.text_frame
        tf_content.word_wrap = True
        return tf_content

    # -------------------------------------------------------------
    # SLIDE 1: Title & Academic Cover Slide
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    # Top Accent Ribbon
    ribbon = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    ribbon.fill.solid()
    ribbon.fill.fore_color.rgb = SAFFRON
    ribbon.line.fill.background()

    # LPU Header & Semester
    tb_univ = slide1.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.733), Inches(0.9))
    tf_u = tb_univ.text_frame
    p_u1 = tf_u.paragraphs[0]
    p_u1.alignment = PP_ALIGN.CENTER
    p_u1.text = "CSE476: AGENTIC AI / MULTI-AGENT SYSTEMS"
    p_u1.font.size = Pt(16)
    p_u1.font.bold = True
    p_u1.font.color.rgb = SAFFRON
    p_u1.font.name = "Arial"

    p_u2 = tf_u.add_paragraph()
    p_u2.alignment = PP_ALIGN.CENTER
    p_u2.text = "Lovely School of Computer Science & Engineering · Lovely Professional University, Punjab"
    p_u2.font.size = Pt(12)
    p_u2.font.color.rgb = RGBColor(203, 213, 225)
    p_u2.font.name = "Arial"

    # Main Project Title
    tb_title = slide1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(1.8))
    tf_t = tb_title.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.alignment = PP_ALIGN.CENTER
    p_t.text = "JANSAHAYAK"
    p_t.font.size = Pt(44)
    p_t.font.bold = True
    p_t.font.color.rgb = WHITE
    p_t.font.name = "Arial"

    p_sub = tf_t.add_paragraph()
    p_sub.alignment = PP_ALIGN.CENTER
    p_sub.text = "Multilingual Government Scheme Eligibility Guide"
    p_sub.font.size = Pt(24)
    p_sub.font.bold = True
    p_sub.font.color.rgb = SAFFRON
    p_sub.font.name = "Arial"

    p_sub2 = tf_t.add_paragraph()
    p_sub2.alignment = PP_ALIGN.CENTER
    p_sub2.text = "A Framework-Based Multi-Agent System with Grounded Hybrid RAG & Deterministic Rule Execution"
    p_sub2.font.size = Pt(14)
    p_sub2.font.color.rgb = RGBColor(226, 232, 240)
    p_sub2.font.name = "Arial"

    # Team Members Card
    team_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(3.9), Inches(6.0), Inches(2.7))
    team_card.fill.solid()
    team_card.fill.fore_color.rgb = NAVY_LIGHT
    team_card.line.color.rgb = RGBColor(51, 65, 85)

    tf_tm = team_card.text_frame
    tf_tm.word_wrap = True
    p_head = tf_tm.paragraphs[0]
    p_head.text = "SUBMITTED BY (TEAM MEMBERS):"
    p_head.font.size = Pt(11)
    p_head.font.bold = True
    p_head.font.color.rgb = SAFFRON

    members = [
        ("1. Sudeep Kumar Reddy Eaga", "Reg: 12318529  |  Roll No: 23"),
        ("2. Kanithi Naresh Kumar", "Reg: 12313053"),
        ("3. Seepana Jyothi Swaroop", "Reg: 12310991"),
    ]
    for name, reg in members:
        p_m = tf_tm.add_paragraph()
        p_m.text = f"{name}"
        p_m.font.size = Pt(13)
        p_m.font.bold = True
        p_m.font.color.rgb = WHITE
        p_r = tf_tm.add_paragraph()
        p_r.text = f"    {reg}"
        p_r.font.size = Pt(11)
        p_r.font.color.rgb = RGBColor(148, 163, 184)

    # Faculty & Course Info Card
    fac_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.8), Inches(3.9), Inches(4.0), Inches(2.7))
    fac_card.fill.solid()
    fac_card.fill.fore_color.rgb = NAVY_LIGHT
    fac_card.line.color.rgb = RGBColor(51, 65, 85)

    tf_fc = fac_card.text_frame
    tf_fc.word_wrap = True
    p_fh = tf_fc.paragraphs[0]
    p_fh.text = "COURSE & SUPERVISOR:"
    p_fh.font.size = Pt(11)
    p_fh.font.bold = True
    p_fh.font.color.rgb = SAFFRON

    fac_details = [
        ("Under the Guidance of:", "Mr. Ravneet Singh (ID: 35120)"),
        ("Course Code:", "CSE476 (Agentic AI)"),
        ("Section:", "K3E2327"),
        ("Academic Period:", "August 2026 - January 2027"),
        ("Target COs:", "CO3 & CO4 (Bloom's L4, L5, L6)"),
    ]
    for lbl, val in fac_details:
        p_l = tf_fc.add_paragraph()
        p_l.text = f"{lbl} "
        p_l.font.size = Pt(11)
        p_l.font.bold = True
        p_l.font.color.rgb = WHITE
        # append value inline
        run = p_l.add_run()
        run.text = val
        run.font.bold = False
        run.font.color.rgb = RGBColor(226, 232, 240)

    # -------------------------------------------------------------
    # SLIDE 2: Multi-Agent DFD, Query Caching Lifecycle & Interactive Guidance
    # -------------------------------------------------------------
    s_dfd = prs.slides.add_slide(blank_layout)
    add_header(s_dfd, "Multi-Agent DFD, Query Caching Lifecycle & Interactive Guidance", "SYSTEM ARCHITECTURE & DFD", 2)

    c_dfd1 = create_card(s_dfd, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "Detailed Multi-Agent DFD Workflow")
    c_dfd1.paragraphs[0].text = "1. Citizen Input (Voice STT / Text):"
    c_dfd1.paragraphs[0].font.bold = True
    c_dfd1.paragraphs[0].font.size = Pt(11.5)
    p = c_dfd1.add_paragraph()
    p.text = "   12 Indian Languages (en, hi, pa, te, ta, bn, mr, kn, gu, ml, or, ur RTL)."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c_dfd1.add_paragraph()
    p.text = "2. Redis Two-Tier Cache Lookup:"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p = c_dfd1.add_paragraph()
    p.text = "   Exact O(1) & Cosine Semantic >= 0.90 -> Hit returns in <5ms with 0 tokens."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c_dfd1.add_paragraph()
    p.text = "3. Profile Intake Agent:"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p = c_dfd1.add_paragraph()
    p.text = "   Script detection, Indic/Urdu numerals -> 14 demographic slots -> Shared Memory."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c_dfd1.add_paragraph()
    p.text = "4. Scheme Retrieval (Hybrid RAG) & Eligibility Rule Agent:"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p = c_dfd1.add_paragraph()
    p.text = "   BM25 + Trigram Vector search -> Top 10 -> Deterministic rule AST execution."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c_dfd1.add_paragraph()
    p.text = "5. Checklist, Guide Manager & Language Reviewer:"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p = c_dfd1.add_paragraph()
    p.text = "   Deduplicates papers -> GroundingGate verifies 3 invariants -> Scheme names verbatim."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c_dfd1.add_paragraph()
    p.text = "6. Verified Output & Write-Through Storage:"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p = c_dfd1.add_paragraph()
    p.text = "   Persisted in PostgreSQL CITIZEN_SESSIONS and cached in Redis."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    c_dfd2 = create_card(s_dfd, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Intelligent Caching, Startup Pre-Warming & Guidance")
    c_dfd2.paragraphs[0].text = "• Query Caching & Database Storage Lifecycle:"
    c_dfd2.paragraphs[0].font.bold = True
    c_dfd2.paragraphs[0].font.size = Pt(11.5)
    p = c_dfd2.add_paragraph()
    p.text = "  New queries run the 6-agent chain, persist to PostgreSQL (CITIZEN_SESSIONS, query_cache_audit), and write through to Redis. Repeated queries fetch directly from Redis/DB, saving 99% computation power (0 tokens, 0 agent invocations, <5ms latency)."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c_dfd2.add_paragraph()
    p.text = "• Startup Cache Pre-Warming:"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p = c_dfd2.add_paragraph()
    p.text = "  At server startup, all 17 welfare schemes, policy chunks, 256-dim vector embeddings, and known cached queries from PostgreSQL are pre-loaded into Redis RAM for instant zero-latency retrieval."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c_dfd2.add_paragraph()
    p.text = "• Missing Info & Dynamic Clarifications (Zero Doubts):"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p = c_dfd2.add_paragraph()
    p.text = "  If a scheme needs more info to verify eligibility, the system actively prompts the citizen with 1-click clarification chips, eliminating all doubts."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c_dfd2.add_paragraph()
    p.text = "• Transparent Rejection Reasons & Official Links:"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p = c_dfd2.add_paragraph()
    p.text = "  Ineligible schemes explicitly list the exact statutory criteria failed (e.g. income cap, pucca house) with official .gov.in portal links."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c_dfd2.add_paragraph()
    p.text = "• Localized Step-by-Step Portal Application Guide:"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p = c_dfd2.add_paragraph()
    p.text = "  Clicking any scheme on the UI opens an interactive modal detailing step-by-step portal instructions and required documents in the citizen's chosen language."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 3: Problem Statement & Real-World Motivation
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Real-World Problem & System Objectives", "PROBLEM STATEMENT & MOTIVATION", 3)

    c2_1 = create_card(s2, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "The Citizen Welfare Dilemma in India")
    c2_1.paragraphs[0].text = "• Extreme Linguistic Fragmentation:"
    c2_1.paragraphs[0].font.bold = True
    c2_1.paragraphs[0].font.size = Pt(12.5)
    p = c2_1.add_paragraph()
    p.text = "  Over 22 official languages, yet official government portals and gazettes are predominantly published in English or complex bureaucratic Hindi, alienating rural citizens."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c2_1.add_paragraph()
    p.text = "• Bureaucratic Information Silos:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c2_1.add_paragraph()
    p.text = "  Welfare programs are scattered across dozens of unlinked ministries (Agriculture, Rural Dev, Health, MSME, Women & Child), forcing citizens to navigate multiple portals."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c2_1.add_paragraph()
    p.text = "• Multi-Conditional Eligibility Thresholds:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c2_1.add_paragraph()
    p.text = "  Determining eligibility requires checking income limits, land acreage, pucca housing status, BPL certification, caste categories, age boundaries, and gender rules."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c2_1.add_paragraph()
    p.text = "• Document Ambiguity & Application Friction:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c2_1.add_paragraph()
    p.text = "  Citizens lack a clear, deduplicated checklist of mandatory papers and where to obtain them (Tehsildar, CSC, Panchayat, Banks)."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c2_2 = create_card(s2, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "The JanSahayak Multi-Agent Solution")
    c2_2.paragraphs[0].text = "• 6 Specialized Agents in Sequential Pipeline:"
    c2_2.paragraphs[0].font.bold = True
    c2_2.paragraphs[0].font.size = Pt(12.5)
    p = c2_2.add_paragraph()
    p.text = "  Orchestrated via Microsoft Agent Framework SequentialBuilder, ensuring deterministic, grounded transitions from citizen profile intake to final verified guide."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c2_2.add_paragraph()
    p.text = "• 12 Indian Languages & Voice Accessibility:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c2_2.add_paragraph()
    p.text = "  Native text and speech-to-text / text-to-speech support for Hindi, Punjabi, Telugu, Tamil, Bengali, Marathi, Kannada, Gujarati, Malayalam, Odia, Urdu (RTL), and English."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c2_2.add_paragraph()
    p.text = "• Zero-Hallucination GroundingGate:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c2_2.add_paragraph()
    p.text = "  Cryptographic citation enforcement verifying that every recommended scheme originates from RAG document chunks and passes mathematical eligibility rules."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c2_2.add_paragraph()
    p.text = "• Two-Tier Fast & Accurate Redis Cache:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c2_2.add_paragraph()
    p.text = "  O(1) exact and profile-guarded semantic vector cache (<5ms latency) with zero cross-demographic contamination guarantee."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 4: Microservices Architecture & System Topology
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Decoupled Microservice Topology & Network Infrastructure", "SYSTEM ARCHITECTURE", 4)

    c3_1 = create_card(s3, Inches(0.8), Inches(1.4), Inches(3.7), Inches(5.3), "Client & Edge Gateway")
    c3_1.paragraphs[0].text = "1. frontend-ui (:3000)"
    c3_1.paragraphs[0].font.bold = True
    c3_1.paragraphs[0].font.size = Pt(12.5)
    c3_1.paragraphs[0].font.color.rgb = BLUE
    p = c3_1.add_paragraph()
    p.text = "• High-performance Nginx Alpine SPA\n• Native Web Speech API STT/TTS\n• Visual 6-stage pipeline progress\n• Urdu Right-to-Left (RTL) mode\n• Live evaluation benchmark dashboard"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c3_1.add_paragraph()
    p.text = "2. api-gateway (:8000)"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p.font.color.rgb = BLUE
    p = c3_1.add_paragraph()
    p.text = "• Unified REST & SSE edge proxy\n• Two-Tier Redis cache lookup\n• Streaming token distribution\n• Health checks & telemetry\n• LoopAwareAsyncHttpPool connection pooling"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    c3_2 = create_card(s3, Inches(4.8), Inches(1.4), Inches(3.7), Inches(5.3), "Core Agent & Voice Services")
    c3_2.paragraphs[0].text = "3. agent-orchestrator (:8003)"
    c3_2.paragraphs[0].font.bold = True
    c3_2.paragraphs[0].font.size = Pt(12.5)
    c3_2.paragraphs[0].font.color.rgb = SAFFRON
    p = c3_2.add_paragraph()
    p.text = "• Microsoft Agent Framework runtime\n• SequentialBuilder 6-agent chain\n• GroundingGate invariant verifier\n• Language consistency review\n• 10-Profile benchmark evaluator"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c3_2.add_paragraph()
    p.text = "4. voice-speech-service (:8004)"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p.font.color.rgb = SAFFRON
    p = c3_2.add_paragraph()
    p.text = "• 12 BCP-47 speech locales\n• Markdown-to-Speech sanitizer\n• Strips markdown syntax, tables & URLs\n• Generates natural utterance chunks for browser TTS playback"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    c3_3 = create_card(s3, Inches(8.8), Inches(1.4), Inches(3.7), Inches(5.3), "Data, RAG & Persistence")
    c3_3.paragraphs[0].text = "5. profile-memory (:8001)"
    c3_3.paragraphs[0].font.bold = True
    c3_3.paragraphs[0].font.size = Pt(12.5)
    c3_3.paragraphs[0].font.color.rgb = GREEN
    p = c3_3.add_paragraph()
    p.text = "• Session state & memory snapshots\n• Read/write audit trail logger\n• Historical evaluation records\n• Backed by PostgreSQL 16 + Redis"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c3_3.add_paragraph()
    p.text = "6. rag-retrieval (:8002)"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p.font.color.rgb = GREEN
    p = c3_3.add_paragraph()
    p.text = "• Hybrid BM25 lexical retriever\n• Dense character 3-gram vector model\n• 17 central & state schemes catalog\n• 34 semantically dense chunks"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c3_3.add_paragraph()
    p.text = "7. PostgreSQL 16 & Redis 7"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p.font.color.rgb = GREEN

    # -------------------------------------------------------------
    # SLIDE 5: Microsoft Agent Framework Sequential Pipeline
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Microsoft Agent Framework Sequential Orchestration", "MULTI-AGENT COORDINATION", 5)

    c4_1 = create_card(s4, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "Why Sequential Pipeline Architecture?")
    c4_1.paragraphs[0].text = "• Linear Administrative Workflow:"
    c4_1.paragraphs[0].font.bold = True
    c4_1.paragraphs[0].font.size = Pt(12.5)
    p = c4_1.add_paragraph()
    p.text = "  Welfare eligibility follows a deterministic order: Citizen Profile -> Grounded Candidate Retrieval -> Policy Rules -> Document Compilation -> Grounding Check -> Language QA."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c4_1.add_paragraph()
    p.text = "• Elimination of Race Conditions:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c4_1.add_paragraph()
    p.text = "  Blackboard/Broadcast models introduce non-deterministic execution and concurrent state race conditions. Sequential chaining guarantees predictable, auditable evaluation."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c4_1.add_paragraph()
    p.text = "• Low Latency & Token Efficiency:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c4_1.add_paragraph()
    p.text = "  Supervisory manager architectures burn excessive LLM tokens re-routing between agents. Sequential execution eliminates coordinator overhead."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c4_1.add_paragraph()
    p.text = "• Strict Quality Gates:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c4_1.add_paragraph()
    p.text = "  GroundingGate sits explicitly between Rule Evaluation and Final Delivery, blocking hallucinations before the citizen sees them."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c4_2 = create_card(s4, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Framework Primitives & Shared Memory")
    c4_2.paragraphs[0].text = "• Microsoft Agent Framework Orchestration:"
    c4_2.paragraphs[0].font.bold = True
    c4_2.paragraphs[0].font.size = Pt(12.5)
    p = c4_2.add_paragraph()
    p.text = "  Assembled using `agent_framework.orchestrations.SequentialBuilder` with 6 participating agents adhering to `SupportsAgentRun`."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c4_2.add_paragraph()
    p.text = "• Template Method Pattern (Base Specialized Agent):"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c4_2.add_paragraph()
    p.text = "  `SpecializedPipelineAgent(BaseAgent, ISpecializedAgent)` automatically manages MAF lifecycle hooks, execution timers, and audit logging."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c4_2.add_paragraph()
    p.text = "• SharedProfileMemoryContextProvider:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c4_2.add_paragraph()
    p.text = "  Implements MAF `ContextProvider` protocol (`before_run` / `after_run`), dynamically loading and persisting shared `UserProfileMemory` across PostgreSQL and Redis."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c4_2.add_paragraph()
    p.text = "• Full Traceability & Audit Ledger:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c4_2.add_paragraph()
    p.text = "  Every agent logs memory read fields, write fields, execution duration in milliseconds, and human-readable operational summaries."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 6: Agent 1 - Profile Intake Agent
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Agent 1: Profile Intake Agent (Language & Demographics)", "SPECIALIZED AGENT BREAKDOWN", 6)

    c5_1 = create_card(s5, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "Detection & Extraction Engine")
    c5_1.paragraphs[0].text = "• 12-Language Script Detection Algorithm:"
    c5_1.paragraphs[0].font.bold = True
    c5_1.paragraphs[0].font.size = Pt(12.5)
    p = c5_1.add_paragraph()
    p.text = "  Analyzes Unicode codepoint frequencies across 12 scripts (Devanagari, Gurmukhi, Telugu, Tamil, Bengali, Kannada, Gujarati, Malayalam, Odia, Urdu, Latin).\n  Disambiguates shared scripts (Hindi vs Marathi) using grammatical markers."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c5_1.add_paragraph()
    p.text = "• Indic & Urdu Numeral Normalizer:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c5_1.add_paragraph()
    p.text = "  Maps native digits into ASCII Arabic numerals before extraction:\n  Devanagari [०-९] -> [0-9] | Gurmukhi [੦-੯] -> [0-9]\n  Telugu [౦-౯] -> [0-9] | Urdu [۰-۹] -> [0-9]"
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c5_1.add_paragraph()
    p.text = "• Multilingual Regex Slot Extraction:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c5_1.add_paragraph()
    p.text = "  Extracts 14 core demographic attributes:\n  Age, Annual Income, Land Acres, Pucca House, BPL Card, Gender, Marital Status, Caste, Disability, LPG, Student, Govt Employee, Girl Child Age."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c5_2 = create_card(s5, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Memory Contract & Interactive Features")
    c5_2.paragraphs[0].text = "• Missing Requisite Detection:"
    c5_2.paragraphs[0].font.bold = True
    c5_2.paragraphs[0].font.size = Pt(12.5)
    p = c5_2.add_paragraph()
    p.text = "  Checks for baseline parameters (age, occupation, residence, income). Unstated parameters are flagged in `missing_profile_fields` to guide the citizen interactively."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c5_2.add_paragraph()
    p.text = "• Form Override Integration:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c5_2.add_paragraph()
    p.text = "  Seamlessly merges direct dropdown inputs from the Web UI with free-form conversational text, giving the citizen full control."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c5_2.add_paragraph()
    p.text = "• Canonical Demographic Profile Signature:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c5_2.add_paragraph()
    p.text = "  Exposes `extract_quick_profile()` to compute a deterministic demographic hash for the Redis Semantic Cache before full pipeline execution."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c5_2.add_paragraph()
    p.text = "• State Reset on Turn:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c5_2.add_paragraph()
    p.text = "  Safely clears stale downstream scheme candidates, rule results, and document checklists when an updated query is submitted."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 7: Agent 2 - Scheme Retrieval Agent
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Agent 2: Scheme Retrieval Agent (Hybrid BM25 + Vector RAG)", "SPECIALIZED AGENT BREAKDOWN", 7)

    c6_1 = create_card(s6, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "Hybrid Retrieval Architecture")
    c6_1.paragraphs[0].text = "• Why Pure Keyword or Vector Fails Alone:"
    c6_1.paragraphs[0].font.bold = True
    c6_1.paragraphs[0].font.size = Pt(12.5)
    p = c6_1.add_paragraph()
    p.text = "  - Pure sparse search misses semantic concepts when citizens use dialectal terms.\n  - Pure dense embeddings hallucinate or confuse statutory acronyms (PM-KISAN vs PMFBY)."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c6_1.add_paragraph()
    p.text = "• Dual-Tier Hybrid Scoring Formula:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c6_1.add_paragraph()
    p.text = "  Score = 0.5 * BM25Score(d, q) + 0.5 * CosineSim(E_d, E_q)\n\n  - Okapi BM25 captures precise scheme acronyms, portals, and ministries.\n  - Dense Character 3-Gram Vector Model captures morphological root meanings and Indic transliterations."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c6_1.add_paragraph()
    p.text = "• Grounded Scheme Knowledge Base:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c6_1.add_paragraph()
    p.text = "  17 Indian government welfare schemes split into 34 semantically dense chunks (Chunk 0: Identity & Eligibility; Chunk 1: Application Steps & Portals)."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c6_2 = create_card(s6, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Execution & Grounding Evidence")
    c6_2.paragraphs[0].text = "• Profile-Guided Query Expansion:"
    c6_2.paragraphs[0].font.bold = True
    c6_2.paragraphs[0].font.size = Pt(12.5)
    p = c6_2.add_paragraph()
    p.text = "  Synthesizes the citizen's query with demographic facts (e.g., 'elderly rural farmer 2 acres bpl agriculture crop insurance') to ensure high recall across candidate programs."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c6_2.add_paragraph()
    p.text = "• Top-K Candidate Selection (K = 10):"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c6_2.add_paragraph()
    p.text = "  Retrieves top 10 ranked chunks, extracting unique candidate scheme IDs while recording relevance scores."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c6_2.add_paragraph()
    p.text = "• Chunk Citation Linkage for GroundingGate:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c6_2.add_paragraph()
    p.text = "  Every candidate retains explicit chunk IDs (e.g., `PM-KISAN::chunk_0`). Without valid chunk citations, downstream GroundingGate blocks recommendations."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c6_2.add_paragraph()
    p.text = "• Memory Writes:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c6_2.add_paragraph()
    p.text = "  Writes `retrieved_chunks` and `retrieved_scheme_ids` into shared UserProfileMemory."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 8: Agent 3 - Eligibility Rule Agent
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Agent 3: Eligibility Rule Agent (Deterministic Strategy Engine)", "SPECIALIZED AGENT BREAKDOWN", 8)

    c7_1 = create_card(s7, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "Strategy Pattern Rule Evaluator")
    c7_1.paragraphs[0].text = "• Strategy Pattern Comparator Dispatch:"
    c7_1.paragraphs[0].font.bold = True
    c7_1.paragraphs[0].font.size = Pt(12.5)
    p = c7_1.add_paragraph()
    p.text = "  `_OPERATOR_STRATEGIES` table maps `RuleOperator` enums to pure, stateless comparator functions:\n  - LTE / GTE / LT / GT (Numerical thresholds)\n  - EQ / NEQ (Case-normalized equality)\n  - IN / NOT_IN (Categorical inclusion)\n  - BOOL_IS (Boolean conditions)"
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c7_1.add_paragraph()
    p.text = "• Strictly Bounded to RAG Candidates:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c7_1.add_paragraph()
    p.text = "  The agent evaluates ONLY schemes retrieved by RAG, completely preventing hallucination of arbitrary non-existent programs."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c7_1.add_paragraph()
    p.text = "• Composite Rule Structure:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c7_1.add_paragraph()
    p.text = "  - all_of (Mandatory Conjunction): Every criterion must pass.\n  - any_of_groups (Alternative Disjunction): Passes if >= 1 branch passes."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c7_2 = create_card(s7, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Tri-State Classification & Audit Trail")
    c7_2.paragraphs[0].text = "• Tri-State Eligibility Decision Logic:"
    c7_2.paragraphs[0].font.bold = True
    c7_2.paragraphs[0].font.size = Pt(12.5)
    p = c7_2.add_paragraph()
    p.text = "  1. ELIGIBLE:\n     Passed all rules with zero failures and zero missing fields.\n  2. POTENTIAL:\n     Passed rules, zero failures, but pending confirmation of 1-2 unstated fields.\n  3. INELIGIBLE:\n     Violated >= 1 statutory criteria (e.g., govt employee, income ceiling exceeded)."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c7_2.add_paragraph()
    p.text = "• Transparent Rule Audit Trail:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c7_2.add_paragraph()
    p.text = "  Every evaluated scheme produces a `SchemeEligibilityResult` with exact actual vs expected criteria (e.g., 'Passed: land_acres=2.0 <= 5.0, income=90000 <= 200000')."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c7_2.add_paragraph()
    p.text = "• Localized Justifications:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c7_2.add_paragraph()
    p.text = "  Translates reasons into citizen's native language using `LanguagePackRegistry`."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 9: Agent 4 - Document Checklist Agent
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Agent 4: Document Checklist Agent (Deduplication & Authorities)", "SPECIALIZED AGENT BREAKDOWN", 9)

    c8_1 = create_card(s8, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "Cross-Scheme Merging & Deduplication")
    c8_1.paragraphs[0].text = "• The Multi-Scheme Document Problem:"
    c8_1.paragraphs[0].font.bold = True
    c8_1.paragraphs[0].font.size = Pt(12.5)
    p = c8_1.add_paragraph()
    p.text = "  When a citizen qualifies for 4 schemes (PM-KISAN, PMFBY, PMAY-G, AB-PMJAY), naive systems output 4 duplicate 'Aadhaar Card' and 'Bank Passbook' instructions, confusing the citizen."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c8_1.add_paragraph()
    p.text = "• Intelligent Merging Algorithm:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c8_1.add_paragraph()
    p.text = "  Maintains a keyed dictionary `merged_docs: dict[str, DocumentRequirement]`. When a document is required by multiple schemes, it consolidates it into a single entry while maintaining full scheme linkage in `required_for_schemes`."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c8_1.add_paragraph()
    p.text = "• Localized Document Names:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c8_1.add_paragraph()
    p.text = "  Resolves document titles into the citizen's target language (e.g., 'ಆಧಾರ್ ಕಾರ್ಡ್', 'భూమి పట్టాదారు పాస్ పుస్తకం', 'ਜਮੀਨ ਦੀ ਜਮ੍ਹਾਬੰਦੀ')."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c8_2 = create_card(s8, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Issuing Authorities & Action Guidance")
    c8_2.paragraphs[0].text = "• Statutory Issuing Authority Attribution:"
    c8_2.paragraphs[0].font.bold = True
    c8_2.paragraphs[0].font.size = Pt(12.5)
    p = c8_2.add_paragraph()
    p.text = "  Every paper specifies where to obtain it, eliminating bureaucratic confusion:\n  - Aadhaar Card -> UIDAI / Aadhaar Seva Kendra\n  - BPL / Ration Card -> Food & Civil Supplies Dept\n  - Income / Caste Cert -> Tehsildar / Revenue Dept / CSC\n  - Land Records -> Revenue Patwari / Bhulekh Portal\n  - Disability Cert -> CMO / District Medical Board\n  - Job Card -> Gram Panchayat / Block Office"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c8_2.add_paragraph()
    p.text = "• Mandatory vs Optional Tagging:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c8_2.add_paragraph()
    p.text = "  Clearly marks mandatory identity papers vs optional subsidy papers."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c8_2.add_paragraph()
    p.text = "• Memory Writes:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c8_2.add_paragraph()
    p.text = "  Writes deduplicated `document_checklist` to shared UserProfileMemory."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 10: Agent 5 - Guide Manager Agent & GroundingGate
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Agent 5: Guide Manager Agent & GroundingGate Verification", "SPECIALIZED AGENT BREAKDOWN", 10)

    c9_1 = create_card(s9, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "The GroundingGate Audit Check")
    c9_1.paragraphs[0].text = "• Three Mandatory Grounding Invariants:"
    c9_1.paragraphs[0].font.bold = True
    c9_1.paragraphs[0].font.size = Pt(12.5)
    p = c9_1.add_paragraph()
    p.text = "  Executed by `GroundingGate.verify(memory)` before compiling any citizen guide:\n\n  1. Invariant 1 (RAG Retrieval Lineage):\n     Scheme must exist in `retrieved_scheme_ids` and possess non-empty chunk evidence IDs.\n\n  2. Invariant 2 (Deterministic Rule Passage):\n     Scheme must have 0 failed rules and >= 1 passed rule.\n\n  3. Invariant 3 (Document Lineage):\n     Every checklist document must link to at least one verified eligible scheme."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c9_1.add_paragraph()
    p.text = "• Hallucination Mitigation:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c9_1.add_paragraph()
    p.text = "  Ungrounded schemes are stripped immediately from `verified_scheme_ids` and logged in `ungrounded_claims`."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c9_2 = create_card(s9, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Direct Official Portals & Guide Synthesis")
    c9_2.paragraphs[0].text = "• Official Portals for Matched & Non-Matched Policies:"
    c9_2.paragraphs[0].font.bold = True
    c9_2.paragraphs[0].font.size = Pt(12.5)
    p = c9_2.add_paragraph()
    p.text = "  1. Eligible Schemes (Matched):\n     - Official scheme title verbatim intact\n     - Localized benefit summary & qualification reason\n     - Direct official portal link (.gov.in/.nic.in) & helpline\n     - Step-by-step application guidance\n\n  2. Potential Schemes (Pending Facts):\n     - Lists unconfirmed criteria + direct official portal link\n\n  3. Non-Matched Schemes (Other Evaluated Policies):\n     - Transparent reason why profile did not qualify\n     - Direct link to official government portal so citizen can read policy details, criteria updates, and learn more."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c9_2.add_paragraph()
    p.text = "• Transparent Citizen Empowerment:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c9_2.add_paragraph()
    p.text = "  Eliminates dead ends: citizens receive direct official portals for every evaluated program, enabling independent verification on official ministry websites."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c9_2.add_paragraph()
    p.text = "• Memory Writes:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c9_2.add_paragraph()
    p.text = "  Writes `draft_guide_text` and `grounding_report`."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 11: Agent 6 - Language-Consistency Reviewer Agent
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Agent 6: Language Reviewer Agent (Group-of-3 Quality Add-On)", "SPECIALIZED AGENT BREAKDOWN", 11)

    c10_1 = create_card(s10, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "Two Quality Invariants Audited")
    c10_1.paragraphs[0].text = "• Invariant 1: Target Language Script Consistency:"
    c10_1.paragraphs[0].font.bold = True
    c10_1.paragraphs[0].font.size = Pt(12.5)
    p = c10_1.add_paragraph()
    p.text = "  Computes script match ratio: R_script = Target_Chars / Total_Alpha_Chars.\n  - For Indic languages: Enforces R_script >= 0.35 and verifies native greeting/headings are present.\n  - For English: Enforces R_script >= 0.60."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c10_1.add_paragraph()
    p.text = "• Invariant 2: Verbatim Scheme Name Preservation:"
    c10_1.paragraphs[0].font.bold = True
    c10_1.paragraphs[0].font.size = Pt(12.5)
    p = c10_1.add_paragraph()
    p.text = "  Government scheme titles (e.g., 'Pradhan Mantri Kisan Samman Nidhi', 'Ayushman Bharat PM-JAY') are legal entities.\n  Translating them into dictionary words makes it impossible for citizens to find the scheme at physical CSC kiosks.\n  The agent verifies every official name appears verbatim intact."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c10_2 = create_card(s10, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Deterministic Auto-Repair & Telemetry")
    c10_2.paragraphs[0].text = "• Deterministic Auto-Repair Engine:"
    c10_2.paragraphs[0].font.bold = True
    c10_2.paragraphs[0].font.size = Pt(12.5)
    p = c10_2.add_paragraph()
    p.text = "  If any official scheme name is altered or omitted, the reviewer automatically restores the canonical scheme title in a formatted block and marks `repaired = True`.\n  If localized greetings were dropped, it restores native greetings."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c10_2.add_paragraph()
    p.text = "• LanguageReviewReport Telemetry:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c10_2.add_paragraph()
    p.text = "  Records target language, detected reply language, script match ratio, intact names list, missing names list, repairs applied, and diagnostic notes."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c10_2.add_paragraph()
    p.text = "• Final Memory Write:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c10_2.add_paragraph()
    p.text = "  Commits `final_reply_text` and `language_review_report` to UserProfileMemory."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 12: Multilingual NLP & Voice Service
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Multilingual Voice & Speech Microservice Architecture", "MULTILINGUAL NLP & VOICE", 12)

    c11_1 = create_card(s11, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "12 Indian Languages & Voice Locales")
    c11_1.paragraphs[0].text = "• Supported Languages Across India:"
    c11_1.paragraphs[0].font.bold = True
    c11_1.paragraphs[0].font.size = Pt(12.5)
    p = c11_1.add_paragraph()
    p.text = "  1. English (en-IN)        7. Marathi (mr-IN)\n  2. Hindi (hi-IN)          8. Kannada (kn-IN)\n  3. Punjabi (pa-IN)        9. Gujarati (gu-IN)\n  4. Telugu (te-IN)         10. Malayalam (ml-IN)\n  5. Tamil (ta-IN)          11. Odia (or-IN)\n  6. Bengali (bn-IN)        12. Urdu (ur-IN, RTL)"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c11_1.add_paragraph()
    p.text = "• Urdu Right-to-Left (RTL) Layout:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c11_1.add_paragraph()
    p.text = "  Dynamically flips UI text direction (`dir='rtl'`) when Urdu is selected, formatting Nastaliq text naturally."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c11_1.add_paragraph()
    p.text = "• Indic Numeral Handling:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c11_1.add_paragraph()
    p.text = "  Handles both written Indic digits (e.g. ੬੫, ६५) and spoken colloquial numbers effortlessly."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c11_2 = create_card(s11, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Voice Microservice & Dynamic UI Localization")
    c11_2.paragraphs[0].text = "• Real-Time Full-Page Dynamic UI Localization:"
    c11_2.paragraphs[0].font.bold = True
    c11_2.paragraphs[0].font.size = Pt(12)
    p = c11_2.add_paragraph()
    p.text = "  Selecting any language dynamically re-translates all navbar elements, tabs, form labels, voice buttons, and scheme metrics without page reload."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c11_2.add_paragraph()
    p.text = "• Live Audio Waveform Equalizer & Voice Sync:"
    p.font.bold = True
    p.font.size = Pt(12)
    p = c11_2.add_paragraph()
    p.text = "  6-bar animated audio equalizer in the voice dock pulsates dynamically during STT dictation and TTS playback. Speech recognition & synthesis auto-switch BCP-47 locale."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c11_2.add_paragraph()
    p.text = "• Scheme Data Visualizer & Comparative Metrics:"
    p.font.bold = True
    p.font.size = Pt(12)
    p = c11_2.add_paragraph()
    p.text = "  Every scheme card features an SVG radial match gauge (100%/75%/35%), financial benefit KPI pill, 4-bar comparative analytics (Match, Financial Index, Process Ease, Document Simplicity), and category filter toolbar."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    p = c11_2.add_paragraph()
    p.text = "• Markdown-to-Speech Sanitizer Endpoint:"
    p.font.bold = True
    p.font.size = Pt(12)
    p = c11_2.add_paragraph()
    p.text = "  `POST /api/v1/voice/sanitize-speech` cleans Markdown tables, URLs, and asterisks for smooth native TTS playback."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 13: Database Design & Redis Two-Tier Caching
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "PostgreSQL 16 Schema & Profile-Guarded Redis Cache", "DATA & CACHING ARCHITECTURE", 13)

    c12_1 = create_card(s12, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "PostgreSQL 16 Relational + JSONB Schema")
    c12_1.paragraphs[0].text = "• Relational 3NF Entities:"
    c12_1.paragraphs[0].font.bold = True
    c12_1.paragraphs[0].font.size = Pt(12.5)
    p = c12_1.add_paragraph()
    p.text = "  - SCHEMES: Primary metadata, official portals, helplines.\n  - SCHEME_CHUNKS: 1:N pre-embedded RAG policy chunks.\n  - CITIZEN_SESSIONS: Normalized profile & memory snapshots.\n  - AGENT_AUDIT_LOGS: Granular read/write audit entries.\n  - EVALUATION_RUNS: Historical benchmark records."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c12_1.add_paragraph()
    p.text = "• JSONB Dynamic Columns:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c12_1.add_paragraph()
    p.text = "  Stores flexible eligibility rule definitions (`rules_json`), required documents, and 12-language localized summaries without schema migrations."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c12_1.add_paragraph()
    p.text = "• Repository & Unit-of-Work Pattern:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c12_1.add_paragraph()
    p.text = "  SQLAlchemy 2.0 ORM repositories with session scopes and automatic SQLite local fallback."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c12_2 = create_card(s12, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Two-Tier Accurate Redis Caching Engine")
    c12_2.paragraphs[0].text = "• The Demographic Collision Hazard:"
    c12_2.paragraphs[0].font.bold = True
    c12_2.paragraphs[0].font.size = Pt(12.5)
    p = c12_2.add_paragraph()
    p.text = "  Naive semantic caching risks serving a rural farmer's welfare response to an urban college student who asked a similar question."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c12_2.add_paragraph()
    p.text = "• Canonical Profile Signature Guard:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c12_2.add_paragraph()
    p.text = "  Computes SHA-256 `profile_hash` over normalized demographic facts before cache lookup, strictly partitioning cache buckets by demographic profile."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c12_2.add_paragraph()
    p.text = "• Two Cache Tiers:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c12_2.add_paragraph()
    p.text = "  - Tier 1 (Exact Hit): O(1) lookup on `<profile_hash>:<query_hash>`. Latency < 5ms.\n  - Tier 2 (Semantic Paraphrase): Cosine similarity >= 0.90 within the same demographic profile bucket.\n  - Tier 3: RAG chunk cache and session memory write-through."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 14: Software Engineering & Low-Level Design (LLD)
    # -------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Software Engineering Rigor: SOLID Principles & Design Patterns", "LOW-LEVEL DESIGN (LLD)", 14)

    c13_1 = create_card(s13, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "SOLID Principles Implementation")
    c13_1.paragraphs[0].text = "• Single Responsibility (SRP):"
    c13_1.paragraphs[0].font.bold = True
    c13_1.paragraphs[0].font.size = Pt(12.5)
    p = c13_1.add_paragraph()
    p.text = "  Every agent isolates one task (e.g. `ProfileIntakeAgent` only extracts demographics; `DocumentChecklistAgent` only deduplicates papers)."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c13_1.add_paragraph()
    p.text = "• Open / Closed (OCP):"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c13_1.add_paragraph()
    p.text = "  New rule operators added to `_OPERATOR_STRATEGIES` and new languages added to `language_packs.py` without modifying core pipeline evaluators."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c13_1.add_paragraph()
    p.text = "• Liskov Substitution (LSP):"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c13_1.add_paragraph()
    p.text = "  `RedisCacheStore` and `InMemoryCacheStore` identically fulfill `ICacheStore`; `HttpProfileMemoryClient` and `LocalProfileMemoryClient` fulfill `IProfileMemoryClient`."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c13_1.add_paragraph()
    p.text = "• Interface Segregation & Dependency Inversion (ISP/DIP):"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c13_1.add_paragraph()
    p.text = "  Targeted contracts in `shared/interfaces/`. Pipeline depends strictly on abstract interfaces injected at runtime."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    c13_2 = create_card(s13, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "GoF Design Patterns Applied")
    c13_2.paragraphs[0].text = "• Template Method Pattern:"
    c13_2.paragraphs[0].font.bold = True
    c13_2.paragraphs[0].font.size = Pt(12.5)
    p = c13_2.add_paragraph()
    p.text = "  `SpecializedPipelineAgent` orchestrates lifecycle timing, MAF context hooks, and audit logging while subclasses implement domain `execute_step()`."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c13_2.add_paragraph()
    p.text = "• Strategy Pattern:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c13_2.add_paragraph()
    p.text = "  - Eligibility rule operator strategies (`_OPERATOR_STRATEGIES`)\n  - Chat client backends (`ChatClientFactory`)\n  - Embedding provider strategies (`HybridTextEmbedder`)."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c13_2.add_paragraph()
    p.text = "• Repository & Unit of Work Pattern:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c13_2.add_paragraph()
    p.text = "  Decouples data access from business logic via `SqlProfileMemoryRepository` and `SqlSchemeRepository`."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    p = c13_2.add_paragraph()
    p.text = "• Cache-Aside & Decorator Pattern:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c13_2.add_paragraph()
    p.text = "  `SemanticQueryCacheService` intercepts pipeline requests, checks exact/semantic tiers, and transparently caches outputs."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 15: Experimental Evaluation & Benchmark (CO3 & CO4)
    # -------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Quantitative Evaluation Benchmark (10 Multilingual Profiles)", "CO3 & CO4 EVALUATION", 15)

    # 4 Metric Callout Boxes
    metric_configs = [
        ("Macro Precision", "100.0%", "1.0000", GREEN, Inches(0.8)),
        ("Macro Recall", "100.0%", "1.0000", GREEN, Inches(3.8)),
        ("Grounding Pass", "100.0%", "Zero Hallucination", BLUE, Inches(6.8)),
        ("Name Preservation", "100.0%", "Verbatim Intact", SAFFRON, Inches(9.8)),
    ]
    for label, big_val, sub_val, col, left_pos in metric_configs:
        m_box = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(1.4), Inches(2.733), Inches(1.2))
        m_box.fill.solid()
        m_box.fill.fore_color.rgb = CARD_BG
        m_box.line.color.rgb = col
        m_box.line.width = Pt(1.5)
        tf_m = m_box.text_frame
        tf_m.word_wrap = True
        p_l = tf_m.paragraphs[0]
        p_l.alignment = PP_ALIGN.CENTER
        p_l.text = label.upper()
        p_l.font.size = Pt(9.5)
        p_l.font.bold = True
        p_l.font.color.rgb = TEXT_MUTED
        p_v = tf_m.add_paragraph()
        p_v.alignment = PP_ALIGN.CENTER
        p_v.text = big_val
        p_v.font.size = Pt(22)
        p_v.font.bold = True
        p_v.font.color.rgb = col
        p_s = tf_m.add_paragraph()
        p_s.alignment = PP_ALIGN.CENTER
        p_s.text = sub_val
        p_s.font.size = Pt(9)
        p_s.font.color.rgb = TEXT_MUTED

    # Table of Evaluated Profiles
    t_shape = s14.shapes.add_table(6, 6, Inches(0.8), Inches(2.8), Inches(11.733), Inches(3.9))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(0.9)  # ID
    tbl.columns[1].width = Inches(0.9)  # Lang
    tbl.columns[2].width = Inches(3.8)  # Profile Description
    tbl.columns[3].width = Inches(3.9)  # Expected Schemes
    tbl.columns[4].width = Inches(1.1)  # Precision
    tbl.columns[5].width = Inches(1.133) # Recall

    headers = ["ID", "Lang", "Citizen Profile Description", "Ground-Truth Welfare Schemes", "Precision", "Recall"]
    for col_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER if col_idx in (0, 1, 4, 5) else PP_ALIGN.LEFT

    eval_rows = [
        ("P01", "hi", "Elderly Rural Small Farmer (BPL, 2 Acres, No Pucca House)", "PM-KISAN, PMFBY, PMAY-G, AB-PMJAY, IGNOAPS, MGNREGA", "1.00", "1.00"),
        ("P02", "te", "Rural Widowed Woman Laborer (BPL, No LPG, No Pucca House)", "PMAY-G, AB-PMJAY, PMUY, IGNWPS, MGNREGA", "1.00", "1.00"),
        ("P04", "ta", "Rural Pregnant Woman (SC Category, Low Income, No LPG)", "AB-PMJAY, PMUY, PMMVY, MGNREGA", "1.00", "1.00"),
        ("P07", "kn", "Rural Citizen with 85% Disability (BPL, Unemployed)", "PMAY-G, AB-PMJAY, IGNDPS, ADIP-DIVYANG, MGNREGA", "1.00", "1.00"),
        ("P10", "en", "High-Income Urban Govt Employee (Negative Control)", "(None) -> Correctly disqualified from welfare", "1.00", "1.00"),
    ]
    for row_idx, row_data in enumerate(eval_rows, start=1):
        for col_idx, val in enumerate(row_data):
            cell = tbl.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 1 else WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_DARK
            p.alignment = PP_ALIGN.CENTER if col_idx in (0, 1, 4, 5) else PP_ALIGN.LEFT
            if col_idx in (4, 5):
                p.font.bold = True
                p.font.color.rgb = GREEN

    # -------------------------------------------------------------
    # SLIDE 16: Deployment & Verification
    # -------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "Three Flexible Deployment Modes & Automated Verification", "DEPLOYMENT & EXECUTION", 16)

    c15_1 = create_card(s15, Inches(0.8), Inches(1.4), Inches(3.7), Inches(5.3), "Option A: Docker Compose")
    c15_1.paragraphs[0].text = "• Production Microservice Stack:"
    c15_1.paragraphs[0].font.bold = True
    c15_1.paragraphs[0].font.size = Pt(12)
    p = c15_1.add_paragraph()
    p.text = "  Launches all 8 containers:\n  - frontend-ui (:3000)\n  - api-gateway (:8000)\n  - profile-memory (:8001)\n  - rag-retrieval (:8002)\n  - orchestrator (:8003)\n  - voice-speech (:8004)\n  - postgres (:5432)\n  - redis (:6379)\n\n  Command:\n  `docker compose up --build`"
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    c15_2 = create_card(s15, Inches(4.8), Inches(1.4), Inches(3.7), Inches(5.3), "Option B: Single Portable Docker")
    c15_2.paragraphs[0].text = "• All-in-One Portable Image:"
    c15_2.paragraphs[0].font.bold = True
    c15_2.paragraphs[0].font.size = Pt(12)
    p = c15_2.add_paragraph()
    p.text = "  Self-contained image packing SQLite, in-memory cache, static UI, and API Gateway on port 8000.\n  Ideal for offline demos, class evaluation, and cloud run.\n\n  Commands:\n  `docker build -t jansahayak .`\n  `docker run -p 8000:8000 jansahayak`"
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    c15_3 = create_card(s15, Inches(8.8), Inches(1.4), Inches(3.7), Inches(5.3), "Option C: Local Python & Tests")
    c15_3.paragraphs[0].text = "• Native Local Execution:"
    c15_3.paragraphs[0].font.bold = True
    c15_3.paragraphs[0].font.size = Pt(12)
    p = c15_3.add_paragraph()
    p.text = "  Zero Docker setup:\n  `set ORCHESTRATION_MODE=local_inproc`\n  `uvicorn services.api_gateway.main:app --port 8000`\n\n• Automated Test Suite:\n  19 pytest tests covering:\n  - 10-profile benchmark\n  - Live HTTP cluster test\n  - Redis 2-tier cache\n  - GroundingGate invariant\n  - 12-language pipeline\n  `pytest -v` (19 passed in ~54s)"
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 17: Summary, Academic Impact & Future Roadmap
    # -------------------------------------------------------------
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "Project Summary, Academic Attainment & Future Roadmap", "CONCLUSION & Q&A", 17)

    c16_1 = create_card(s16, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.3), "Academic Learning Outcomes Fulfilled")
    c16_1.paragraphs[0].text = "• CO3 Attainment (Multi-Agent Architecture & RAG):"
    c16_1.paragraphs[0].font.bold = True
    c16_1.paragraphs[0].font.size = Pt(12.5)
    p = c16_1.add_paragraph()
    p.text = "  - Built a 6-agent sequential pipeline on Microsoft Agent Framework (`SequentialBuilder`).\n  - Implemented shared context provider (`UserProfileMemoryContextProvider`).\n  - Dual-tier hybrid BM25 + dense trigram vector RAG over 17 government schemes."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c16_1.add_paragraph()
    p.text = "• CO4 Attainment (Evaluation & Benchmarking):"
    c16_1.paragraphs[0].font.bold = True
    c16_1.paragraphs[0].font.size = Pt(12.5)
    p = c16_1.add_paragraph()
    p.text = "  - Evaluated on 10 realistic multilingual profiles in 7 Indian languages.\n  - 100% Macro/Micro Precision, 100% Recall, 100% Grounding Pass Rate.\n  - Bloom's Taxonomy Cognitive Levels L4 (Analyze), L5 (Evaluate), L6 (Create) achieved."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    c16_2 = create_card(s16, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3), "Future Roadmap & Project Links")
    c16_2.paragraphs[0].text = "• Future Roadmap Enhancements:"
    c16_2.paragraphs[0].font.bold = True
    c16_2.paragraphs[0].font.size = Pt(12.5)
    p = c16_2.add_paragraph()
    p.text = "  1. DigiLocker API Integration: One-click Aadhaar/certificate verification.\n  2. Offline Edge Speech Models: AI4Bharat IndicWav2Vec for remote panchayats.\n  3. State Gazette Crawlers: Automated scraping of newly announced state welfare schemes."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    p = c16_2.add_paragraph()
    p.text = "• Official GitHub Repository:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p = c16_2.add_paragraph()
    p.text = "  https://github.com/SudeepReddyEaga/JanSahayak\n  (Full source code, tests, documentation, and Dockerfiles)"
    p.font.size = Pt(11)
    p.font.color.rgb = BLUE

    p = c16_2.add_paragraph()
    p.text = "• Thank You! Questions & Discussion:"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p.font.color.rgb = SAFFRON
    p = c16_2.add_paragraph()
    p.text = "  Ready for live system demonstration on http://localhost:3000."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK

    # Save presentation
    output_path = "JanSahayak_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_deck()
