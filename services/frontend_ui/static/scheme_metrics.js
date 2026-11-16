/**
 * Scheme Metrics & Visual Analytics Engine
 * Provides quantitative data, categorization, and rich interactive visual
 * KPI meters (Radial SVG Match Gauges, Financial Benefit Pills, Multi-Dimension
 * Comparative Metric Bars, and Category Badges) for all 17 Government Schemes.
 */

const SCHEME_METRICS_CATALOG = {
  "PM-KISAN": {
    category: "agri",
    category_name: "Agriculture & Farmers",
    color: "#10b981",
    gradient: "linear-gradient(135deg, #059669 0%, #10b981 100%)",
    annual_benefit: "₹6,000 / year",
    annual_benefit_raw: 6000,
    financial_impact_score: 75,
    ease_of_application_score: 90,
    document_simplicity_score: 85,
    processing_track: "⚡ Direct Benefit Transfer (DBT) · 3 Installments",
    national_reach: "👥 11.8+ Crore Landholding Farmers",
    disbursement_mode: "Aadhaar DBT to Bank",
    steps_count: 5,
    docs_count: 3,
  },
  "AB-PMJAY": {
    category: "health",
    category_name: "Healthcare & Wellness",
    color: "#06b6d4",
    gradient: "linear-gradient(135deg, #0891b2 0%, #06b6d4 100%)",
    annual_benefit: "₹5,00,000 / year",
    annual_benefit_raw: 500000,
    financial_impact_score: 98,
    ease_of_application_score: 92,
    document_simplicity_score: 90,
    processing_track: "🏥 Cashless Hospitalization · Instant e-Card",
    national_reach: "👥 55+ Crore Vulnerable Citizens (Top 40%)",
    disbursement_mode: "Cashless Empaneled Hospitals",
    steps_count: 4,
    docs_count: 2,
  },
  "PMAY-G": {
    category: "housing",
    category_name: "Housing & Rural Development",
    color: "#f59e0b",
    gradient: "linear-gradient(135deg, #d97706 0%, #f59e0b 100%)",
    annual_benefit: "₹1,20,000 - ₹1,30,000",
    annual_benefit_raw: 130000,
    financial_impact_score: 92,
    ease_of_application_score: 78,
    document_simplicity_score: 75,
    processing_track: "🏠 Geo-Tagged Construction Stages · DBT Transfer",
    national_reach: "👥 3.2+ Crore Pucca Houses Sanctioned",
    disbursement_mode: "Direct Bank Transfer per Milestone",
    steps_count: 5,
    docs_count: 4,
  },
  "PM-SVANIDHI": {
    category: "msme",
    category_name: "Livelihood & Street Vendors",
    color: "#8b5cf6",
    gradient: "linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%)",
    annual_benefit: "₹10,000 - ₹50,000 (Loan @ 7% Subsidy)",
    annual_benefit_raw: 50000,
    financial_impact_score: 80,
    ease_of_application_score: 88,
    document_simplicity_score: 85,
    processing_track: "💼 Collateral-Free Micro-Credit · 7-Day Approval",
    national_reach: "👥 65+ Lakh Urban Street Vendors",
    disbursement_mode: "Bank / Digital Lending App",
    steps_count: 4,
    docs_count: 3,
  },
  "PM-VISHWAKARMA": {
    category: "msme",
    category_name: "Artisans & Traditional Crafts",
    color: "#a855f7",
    gradient: "linear-gradient(135deg, #9333ea 0%, #a855f7 100%)",
    annual_benefit: "₹3,00,000 Loan @ 5% + ₹15k Tool Grant",
    annual_benefit_raw: 315000,
    financial_impact_score: 94,
    ease_of_application_score: 82,
    document_simplicity_score: 80,
    processing_track: "🛠️ Skill Training (₹500/day) + Tool Toolkit Incentive",
    national_reach: "👥 30+ Lakh Traditional Artisans (18 Trades)",
    disbursement_mode: "e-Voucher & Bank Credit",
    steps_count: 5,
    docs_count: 3,
  },
  "APY": {
    category: "pension",
    category_name: "Pensions & Social Security",
    color: "#3b82f6",
    gradient: "linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%)",
    annual_benefit: "₹1,000 - ₹5,000 / month Pension",
    annual_benefit_raw: 60000,
    financial_impact_score: 86,
    ease_of_application_score: 95,
    document_simplicity_score: 95,
    processing_track: "👴 Guaranteed Sovereign Pension from Age 60",
    national_reach: "👥 6.2+ Crore Unorganized Workers",
    disbursement_mode: "Auto-Debit Bank Account",
    steps_count: 4,
    docs_count: 2,
  },
  "PMSYM": {
    category: "pension",
    category_name: "Unorganized Worker Pension",
    color: "#2563eb",
    gradient: "linear-gradient(135deg, #1e40af 0%, #2563eb 100%)",
    annual_benefit: "₹3,000 / month Guaranteed Pension",
    annual_benefit_raw: 36000,
    financial_impact_score: 82,
    ease_of_application_score: 90,
    document_simplicity_score: 90,
    processing_track: "👵 50:50 Govt Matching Contribution",
    national_reach: "👥 50+ Lakh Gig & Domestic Workers",
    disbursement_mode: "CSC & LIC Pension Portal",
    steps_count: 4,
    docs_count: 2,
  },
  "PM-UY": {
    category: "women",
    category_name: "Women Empowerment & Clean Energy",
    color: "#ec4899",
    gradient: "linear-gradient(135deg, #db2777 0%, #ec4899 100%)",
    annual_benefit: "Free LPG Connection + ₹300 Subsidy/cylinder",
    annual_benefit_raw: 4500,
    financial_impact_score: 78,
    ease_of_application_score: 86,
    document_simplicity_score: 80,
    processing_track: "🔥 1st Free Cylinder & Stove + Direct Subsidy",
    national_reach: "👥 10.3+ Crore Rural BPL Households",
    disbursement_mode: "LPG Distributor & PAHAL DBT",
    steps_count: 4,
    docs_count: 3,
  },
  "SSY": {
    category: "women",
    category_name: "Girl Child Education & Wealth",
    color: "#f43f5e",
    gradient: "linear-gradient(135deg, #e11d48 0%, #f43f5e 100%)",
    annual_benefit: "8.2% Compound Sovereign Interest (Tax-Free)",
    annual_benefit_raw: 150000,
    financial_impact_score: 90,
    ease_of_application_score: 92,
    document_simplicity_score: 88,
    processing_track: "👧 Sovereign EEE Tax Exemption Under Sec 80C",
    national_reach: "👥 3.6+ Crore Girl Child Accounts",
    disbursement_mode: "Post Office / Bank Account",
    steps_count: 4,
    docs_count: 3,
  },
  "NSAP-IGNOAPS": {
    category: "pension",
    category_name: "Elderly National Assistance",
    color: "#0284c7",
    gradient: "linear-gradient(135deg, #0369a1 0%, #0284c7 100%)",
    annual_benefit: "₹200 - ₹500 / month Non-Contributory",
    annual_benefit_raw: 6000,
    financial_impact_score: 72,
    ease_of_application_score: 75,
    document_simplicity_score: 78,
    processing_track: "👵 100% Free Senior Citizen Social Assistance",
    national_reach: "👥 2.9+ Crore Elderly BPL Citizens",
    disbursement_mode: "State Social Welfare DBT",
    steps_count: 4,
    docs_count: 3,
  },
  "PMMVY": {
    category: "women",
    category_name: "Maternal Health & Nutrition",
    color: "#fb7185",
    gradient: "linear-gradient(135deg, #f43f5e 0%, #fb7185 100%)",
    annual_benefit: "₹5,000 Direct Cash Incentive in 2 Installments",
    annual_benefit_raw: 5000,
    financial_impact_score: 76,
    ease_of_application_score: 84,
    document_simplicity_score: 82,
    processing_track: "👶 Nutrition Support + Institutional Delivery Bonus",
    national_reach: "👥 3.5+ Crore Pregnant & Lactating Mothers",
    disbursement_mode: "Anganwadi & PMMVY-CAS Portal",
    steps_count: 4,
    docs_count: 3,
  },
  "PM-MUDRA": {
    category: "msme",
    category_name: "Micro Enterprises & Business Loans",
    color: "#6366f1",
    gradient: "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)",
    annual_benefit: "Loans up to ₹10,00,000 (Shishu/Kishore/Tarun)",
    annual_benefit_raw: 1000000,
    financial_impact_score: 95,
    ease_of_application_score: 80,
    document_simplicity_score: 74,
    processing_track: "💼 No Collateral Required · Subsidized Interest",
    national_reach: "👥 48+ Crore Loans Sanctioned",
    disbursement_mode: "Commercial & Regional Rural Banks",
    steps_count: 5,
    docs_count: 4,
  },
  "STAND-UP-INDIA": {
    category: "msme",
    category_name: "SC/ST & Women Green Enterprises",
    color: "#84cc16",
    gradient: "linear-gradient(135deg, #65a30d 0%, #84cc16 100%)",
    annual_benefit: "₹10,00,000 to ₹1,00,00,000 Greenfield Loan",
    annual_benefit_raw: 5000000,
    financial_impact_score: 99,
    ease_of_application_score: 72,
    document_simplicity_score: 65,
    processing_track: "🚀 Enterprise Handholding & Credit Guarantee",
    national_reach: "👥 2.1+ Lakh SC/ST/Women Entrepreneurs",
    disbursement_mode: "Stand-Up Mitra Portal & Banks",
    steps_count: 5,
    docs_count: 5,
  },
  "PM-KMY": {
    category: "agri",
    category_name: "Small & Marginal Farmer Pension",
    color: "#14b8a6",
    gradient: "linear-gradient(135deg, #0d9488 0%, #14b8a6 100%)",
    annual_benefit: "₹3,000 / month Assured Pension from Age 60",
    annual_benefit_raw: 36000,
    financial_impact_score: 82,
    ease_of_application_score: 88,
    document_simplicity_score: 85,
    processing_track: "🌾 Voluntary & Contributory Pension Scheme",
    national_reach: "👥 23+ Lakh Registered Farmers",
    disbursement_mode: "CSC / PM-KISAN Auto-Debit",
    steps_count: 4,
    docs_count: 3,
  },
  "PMSBY": {
    category: "insurance",
    category_name: "Accident Risk Insurance",
    color: "#0284c7",
    gradient: "linear-gradient(135deg, #0369a1 0%, #0284c7 100%)",
    annual_benefit: "₹2,00,000 Accidental Death / Disability Cover",
    annual_benefit_raw: 200000,
    financial_impact_score: 88,
    ease_of_application_score: 98,
    document_simplicity_score: 96,
    processing_track: "🛡️ Only ₹20 / year Auto-Debited from Bank",
    national_reach: "👥 44+ Crore Enrolled Citizens",
    disbursement_mode: "Direct Insurer Settlement to Nominee",
    steps_count: 3,
    docs_count: 2,
  },
  "PMJJBY": {
    category: "insurance",
    category_name: "Life Term Insurance",
    color: "#0369a1",
    gradient: "linear-gradient(135deg, #075985 0%, #0369a1 100%)",
    annual_benefit: "₹2,00,000 Life Insurance Cover (Any Cause)",
    annual_benefit_raw: 200000,
    financial_impact_score: 90,
    ease_of_application_score: 96,
    document_simplicity_score: 94,
    processing_track: "🛡️ ₹436 / year Renewable Term Insurance",
    national_reach: "👥 19+ Crore Life Insured Citizens",
    disbursement_mode: "Aadhaar Linked Bank Account",
    steps_count: 3,
    docs_count: 2,
  },
  "PM-AASHA": {
    category: "agri",
    category_name: "Farmer Crop Price Support",
    color: "#16a34a",
    gradient: "linear-gradient(135deg, #15803d 0%, #16a34a 100%)",
    annual_benefit: "100% Minimum Support Price (MSP) Protection",
    annual_benefit_raw: 50000,
    financial_impact_score: 85,
    ease_of_application_score: 80,
    document_simplicity_score: 78,
    processing_track: "🌾 Price Support & Deficiency Payment Scheme (PDPS)",
    national_reach: "👥 Millions of Oilseed & Pulses Farmers",
    disbursement_mode: "State Mandi DBT Portal",
    steps_count: 4,
    docs_count: 3,
  },
  "PMFBY": {
    category: "agri",
    category_name: "Comprehensive Crop Insurance",
    color: "#15803d",
    gradient: "linear-gradient(135deg, #166534 0%, #15803d 100%)",
    annual_benefit: "Complete Crop Damage Compensation @ 1.5-2% Premium",
    annual_benefit_raw: 100000,
    financial_impact_score: 89,
    ease_of_application_score: 84,
    document_simplicity_score: 80,
    processing_track: "🛰️ Satellite & Drone Crop Yield Loss Assessment",
    national_reach: "👥 5.5+ Crore Farmer Applications Annually",
    disbursement_mode: "Insurance Company DBT to Bank",
    steps_count: 4,
    docs_count: 3,
  },
};

/**
 * Return scheme analytics metadata with resilient fallbacks.
 */
function getSchemeMetrics(schemeId) {
  return (
    SCHEME_METRICS_CATALOG[schemeId] || {
      category: "general",
      category_name: "Government Welfare",
      color: "#3b82f6",
      gradient: "linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%)",
      annual_benefit: "Statutory Financial & Social Welfare Benefit",
      annual_benefit_raw: 10000,
      financial_impact_score: 80,
      ease_of_application_score: 85,
      document_simplicity_score: 85,
      processing_track: "⚡ Official Government Portal / DBT Transfer",
      national_reach: "👥 Nationwide Beneficiaries",
      disbursement_mode: "Aadhaar DBT to Bank",
      steps_count: 4,
      docs_count: 3,
    }
  );
}

/**
 * Render visual analytics matrix HTML for a scheme card:
 * Includes SVG radial match meter, KPI benefit pill, RAG score bar,
 * and 4-dimension comparative metrics visualization bars.
 */
function buildSchemeMetricsHTML(scheme, lang = "en", matchPct = 100) {
  const meta = getSchemeMetrics(scheme.scheme_id);
  const ragPct = Math.min(100, Math.round((scheme.rag_score || 0.85) * 100));
  const impactPct = meta.financial_impact_score || 80;
  const easePct = meta.ease_of_application_score || 85;
  const simplicityPct = meta.document_simplicity_score || 80;

  // SVG Circular Gauge calculation (Radius = 24, Circumference = ~150.8)
  const radius = 24;
  const circ = 2 * Math.PI * radius;
  const offset = circ - (matchPct / 100) * circ;

  const matchLabel = window.t ? window.t("metric_match_score", lang) : "Match Score";
  const benefitLabel = window.t ? window.t("metric_benefit", lang) : "Max Benefit";
  const ragLabel = window.t ? window.t("metric_rag_score", lang) : "RAG Grounding";
  const docsLabel = window.t ? window.t("metric_docs", lang) : "Documents";

  return `
    <div class="metrics-dashboard" style="border-left: 4px solid ${meta.color};">
      <!-- Top Row: Interactive KPI Badges + SVG Match Gauge -->
      <div class="metrics-kpi-row">
        <!-- SVG Radial Match Gauge -->
        <div class="metric-radial-wrap" title="${matchLabel}: ${matchPct}%">
          <svg class="radial-svg" width="60" height="60" viewBox="0 0 60 60">
            <circle class="radial-bg" cx="30" cy="30" r="${radius}" />
            <circle class="radial-progress" cx="30" cy="30" r="${radius}"
              stroke="${meta.color}"
              stroke-dasharray="${circ}"
              stroke-dashoffset="${offset}" />
          </svg>
          <div class="radial-center-text">
            <span class="radial-val">${matchPct}%</span>
          </div>
        </div>

        <!-- Financial Value Pill -->
        <div class="kpi-pill kpi-pill-benefit" style="background: ${meta.gradient};">
          <span class="kpi-sub">${benefitLabel}</span>
          <span class="kpi-title">${meta.annual_benefit}</span>
        </div>

        <!-- RAG Grounding Pill -->
        <div class="kpi-pill kpi-pill-rag">
          <span class="kpi-sub">${ragLabel}</span>
          <span class="kpi-title">✓ ${ragPct}% Verified</span>
        </div>

        <!-- National Scale Pill -->
        <div class="kpi-pill kpi-pill-reach">
          <span class="kpi-sub">National Reach</span>
          <span class="kpi-title">${meta.national_reach}</span>
        </div>
      </div>

      <!-- Visual Multi-Dimension Progress Analytics Bars -->
      <div class="metrics-bars-wrap">
        <div class="metric-bar-item">
          <div class="metric-bar-header">
            <span>🎯 Eligibility Match</span>
            <strong>${matchPct}%</strong>
          </div>
          <div class="m-track">
            <div class="m-fill" style="width: ${matchPct}%; background: ${meta.color};"></div>
          </div>
        </div>

        <div class="metric-bar-item">
          <div class="metric-bar-header">
            <span>💰 Financial Assistance Index</span>
            <strong>${impactPct}%</strong>
          </div>
          <div class="m-track">
            <div class="m-fill" style="width: ${impactPct}%; background: linear-gradient(90deg, #10b981, #06b6d4);"></div>
          </div>
        </div>

        <div class="metric-bar-item">
          <div class="metric-bar-header">
            <span>⚡ Application Process Ease</span>
            <strong>${easePct}%</strong>
          </div>
          <div class="m-track">
            <div class="m-fill" style="width: ${easePct}%; background: linear-gradient(90deg, #6366f1, #8b5cf6);"></div>
          </div>
        </div>

        <div class="metric-bar-item">
          <div class="metric-bar-header">
            <span>📄 Document Simplicity</span>
            <strong>${simplicityPct}% (${meta.docs_count} ${docsLabel})</strong>
          </div>
          <div class="m-track">
            <div class="m-fill" style="width: ${simplicityPct}%; background: linear-gradient(90deg, #f59e0b, #ef4444);"></div>
          </div>
        </div>
      </div>

      <div class="metrics-track-footer">
        <span class="track-tag">${meta.processing_track}</span>
        <span class="track-mode">Mode: ${meta.disbursement_mode}</span>
      </div>
    </div>
  `;
}

window.SCHEME_METRICS_CATALOG = SCHEME_METRICS_CATALOG;
window.getSchemeMetrics = getSchemeMetrics;
window.buildSchemeMetricsHTML = buildSchemeMetricsHTML;
