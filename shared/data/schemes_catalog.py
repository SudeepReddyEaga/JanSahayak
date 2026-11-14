"""
Canonical Catalog of 17 Indian Central Government Welfare Schemes.
Each SchemeDefinition acts as the single source of truth for:
  - RAG full-text knowledge documents & multilingual keywords (12 languages)
  - Deterministic EligibilityRuleGroup trees evaluated by EligibilityRuleAgent
  - Grounded DocumentRequirement checklists & official application workflows
"""

from shared.domain.enums import RuleOperator
from shared.domain.models import (
    DocumentRequirement,
    EligibilityRuleGroup,
    RuleCondition,
    SchemeDefinition,
)

# ==============================================================================
# Reusable Document Definitions (DRY Principle - avoids duplicating doc specs)
# ==============================================================================


def _doc(
    doc_id: str,
    name: str,
    description: str,
    where: str,
    schemes: list[str],
    hi: str,
    te: str,
    ta: str,
    bn: str,
    mr: str,
    kn: str,
) -> DocumentRequirement:
    """Factory helper constructing a multilingual DocumentRequirement entity."""
    return DocumentRequirement(
        doc_id=doc_id,
        name=name,
        localized_names={
            "en": name,
            "hi": hi,
            "te": te,
            "ta": ta,
            "bn": bn,
            "mr": mr,
            "kn": kn,
        },
        description=description,
        where_to_obtain=where,
        mandatory=True,
        required_for_schemes=schemes,
    )


# Shared canonical documents referenced across schemes
DOC_AADHAAR = _doc(
    "DOC-AADHAAR",
    "Aadhaar Card",
    "12-digit biometric identity card linked with active mobile number for e-KYC.",
    "UIDAI Aadhaar Seva Kendra / Common Service Centre (CSC)",
    [],
    "आधार कार्ड (Aadhaar Card)",
    "ఆధార్ కార్డు (Aadhaar Card)",
    "ஆதார் அட்டை (Aadhaar Card)",
    "আধার কার্ড (Aadhaar Card)",
    "आधार कार्ड (Aadhaar Card)",
    "ಆಧಾರ್ ಕಾರ್ಡ್ (Aadhaar Card)",
)

DOC_BANK = _doc(
    "DOC-BANK",
    "Aadhaar-Seeded Bank Passbook",
    "Front page of active savings bank or post office account passbook enabled for DBT.",
    "Respective Bank Branch or India Post Payments Bank",
    [],
    "बैंक पासबुक (आधार से लिंक)",
    "ఆధార్ లింక్ చేసిన బ్యాంకు పాస్‌బుక్",
    "ஆதார் இணைக்கப்பட்ட வங்கி பாஸ்புக்",
    "আধার সংযুক্ত ব্যাংক পাসবুক",
    "आधार-लिंक्ड बँक पासबुक",
    "ಆಧಾರ್ ಲಿಂಕ್ ಮಾಡಿದ ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್",
)

DOC_INCOME = _doc(
    "DOC-INCOME",
    "Family Annual Income Certificate",
    "Official income certificate issued by Tehsildar / Revenue Officer / Mandal Office.",
    "State e-District Portal / Tehsil / MeeSeva / CSC",
    [],
    "वार्षिक आय प्रमाण पत्र",
    "కుటుంబ వార్షిక ఆదాయ ధృవీకరణ పత్రం",
    "குடும்ப ஆண்டு வருமானச் சான்றிதழ்",
    "বার্ষিক পারিবারিক আয়ের শংসাপত্র",
    "वार्षिक उत्पन्न प्रमाणपत्र",
    "ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ",
)

DOC_BPL_RATION = _doc(
    "DOC-RATION-BPL",
    "BPL / Ration Card",
    "Below Poverty Line or Antyodaya / Priority Household Ration Card listing family members.",
    "Food & Civil Supplies Department / Gram Panchayat / Fair Price Shop",
    [],
    "बीपीएल / राशन कार्ड",
    "బీపీఎల్ / రేషన్ కార్డు",
    "பிபிஎல் / ரேஷன் கார்டு",
    "বিপিএল / রেশন কার্ড",
    "बीपीएल / रेशन कार्ड",
    "ಬಿಪಿಎಲ್ / ರೇಷನ್ ಕಾರ್ಡ್",
)

DOC_CASTE = _doc(
    "DOC-CASTE",
    "Caste / Community Certificate (SC/ST/OBC/EBC)",
    "Authorized social category certificate issued by Revenue / SDM authority.",
    "State e-District / Tehsildar / Revenue Office",
    [],
    "जाति प्रमाण पत्र",
    "కుల ధృవీకరణ పత్రం",
    "சாதிச் சான்றிதழ்",
    "জাতিগত শংসাপত্র",
    "जात प्रमाणपत्र",
    "ಜಾತಿ ಪ್ರಮಾಣಪತ್ರ",
)

DOC_PHOTO = _doc(
    "DOC-PHOTO",
    "Passport-Size Photographs (2 copies)",
    "Recent color passport-size photographs of the applicant.",
    "Local Photo Studio / CSC",
    [],
    "पासपोर्ट साइज फोटो (2 प्रतियां)",
    "పాస్‌పోర్ట్ సైజు ఫోటోలు (2)",
    "பாஸ்போர்ட் அளவு புகைப்படங்கள் (2)",
    "পাসপোর্ট সাইজের ছবি (২ কপি)",
    "पासपोर्ट आकाराचे फोटो (2 प्रती)",
    "ಪಾಸ್‌ಪೋರ್ಟ್ ಅಳತೆಯ ಭಾವಚಿತ್ರಗಳು (2)",
)


def _with_scheme(doc: DocumentRequirement, scheme_id: str) -> DocumentRequirement:
    """Clone a shared DocumentRequirement tagged specifically with scheme_id."""
    return doc.model_copy(update={"required_for_schemes": [scheme_id]})


# ==============================================================================
# Complete 16-Scheme Catalog
# ==============================================================================

SCHEMES_CATALOG: list[SchemeDefinition] = [
    # --------------------------------------------------------------------------
    # 1. PM-KISAN
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="PM-KISAN",
        official_name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        short_code="PM-KISAN",
        ministry="Ministry of Agriculture and Farmers Welfare",
        benefit_summary="Rs. 6,000 per year income support paid directly to bank accounts in three equal installments of Rs. 2,000 every four months.",
        localized_summaries={
            "en": "Rs. 6,000/year direct income support in 3 installments of Rs. 2,000 for landholding farmer families.",
            "hi": "भूमिधारक किसान परिवारों को प्रति वर्ष ₹6,000 की सीधी आर्थिक सहायता (₹2,000 की 3 किस्तों में)।",
            "te": "భూమి కలిగిన రైతు కుటుంబాలకు సంవత్సరానికి రూ. 6,000 (రూ. 2,000 చొప్పుन 3 విడతల్లో) నేరుగా ఖాతాలో జమ.",
            "ta": "நிலம் வைத்திருக்கும் விவசாயக் குடும்பங்களுக்கு ஆண்டுக்கு ரூ. 6,000 (ரூ. 2,000 வீதம் 3 தவணைகளில்) நேரடி நிதி உதவி.",
            "bn": "জমির মালিক কৃষক পরিবারকে বছরে ₹6,000 সরাসরি আর্থিক সহায়তা (₹2,000 করে ৩ কিস্তিতে)।",
            "mr": "शेतजमीन असलेल्या शेतकरी कुटुंबांना वर्षाला ₹6,000 थेट आर्थिक मदत (₹2,000 च्या 3 हप्त्यांमध्ये).",
            "kn": "ಕೃಷಿ ಭೂಮಿ ಹೊಂದಿರುವ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವರ್ಷಕ್ಕೆ ರೂ. 6,000 ನೇರ ಆರ್ಥಿಕ ನೆರವು (ರೂ. 2,000 ರ 3 ಕಂತುಗಳಲ್ಲಿ).",
        },
        target_tags=["farmer", "agriculture", "landholding", "rural", "dbt"],
        multilingual_keywords=[
            "farmer", "kisan", "land", "cultivable", "acre", "agriculture", "किसान", "खेती", "जमीन",
            "రైతు", "భూమి", "వ్యవసాయం", "விவசாயி", "நிலம்", "কৃষক", "জমি", "शेतकरी", "शेतजमीन", "ರೈತ", "ಭೂಮಿ",
        ],
        full_document_text=(
            "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) provides Rs. 6,000 annual income support to "
            "all landholding farmer families across India having cultivable land in their name. "
            "Eligibility criteria: applicant must be a farmer owning cultivable agricultural land, "
            "must not be an active regular government employee or high-income taxpayer (household income <= Rs. 6,00,000). "
            "Requires Aadhaar e-KYC, land ownership RoR/Khatauni records, and Aadhaar-seeded bank account."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="occupation",
                    operator=RuleOperator.IN,
                    value=["farmer", "agricultural_worker"],
                    description="Citizen must be engaged in farming/agriculture.",
                ),
                RuleCondition(
                    field="owns_cultivable_land",
                    operator=RuleOperator.BOOL_IS,
                    value=True,
                    description="Citizen family must own cultivable agricultural land.",
                ),
                RuleCondition(
                    field="annual_income_inr",
                    operator=RuleOperator.LTE,
                    value=600000,
                    description="Annual household income must be <= Rs. 6,00,000 (non-taxpayer threshold).",
                ),
                RuleCondition(
                    field="is_govt_employee",
                    operator=RuleOperator.BOOL_IS,
                    value=False,
                    description="Serving regular government employees are excluded.",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "PM-KISAN"),
            _doc(
                "DOC-LAND-ROR",
                "Cultivable Land Ownership Record (Khatauni / RoR / Patta)",
                "Revenue extract proving cultivable agricultural land ownership.",
                "State Bhulekh Portal / Village Revenue Officer / Patwari",
                ["PM-KISAN"],
                "खेती की जमीन के कागजात (खतौनी / भूलेख रिकॉर्ड)",
                "భూమి యాజమాన్య పట్టాదార్ పాస్‌బుక్ / ఆర్‌ఓఆర్",
                "பட்டா / சிட்டா / நில உரிமை ஆவணம்",
                "জমির খতিয়ান / পর্চা নথি",
                "शेतजमिनीचा 7/12 उतारा",
                "ಪಹಣಿ / ಆರ್‌ಟಿಸಿ (RTC) ಭೂ ದಾಖಲೆ",
            ),
            _with_scheme(DOC_BANK, "PM-KISAN"),
        ],
        application_steps=[
            "Visit pmkisan.gov.in and select 'New Farmer Registration' or visit your nearest Common Service Centre (CSC).",
            "Enter your Aadhaar number, mobile number, and State, then verify OTP.",
            "Upload your cultivable land Khatauni/Patta details and Aadhaar-linked bank account details.",
            "Complete mandatory Aadhaar e-KYC online or via biometric scan at CSC.",
            "Track approval status through 'Know Your Status' on pmkisan.gov.in.",
        ],
        official_portal="https://pmkisan.gov.in",
        helpline="155261 / 011-24300606",
    ),

    # --------------------------------------------------------------------------
    # 2. PMFBY (Crop Insurance)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="PMFBY",
        official_name="Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        short_code="PMFBY",
        ministry="Ministry of Agriculture and Farmers Welfare",
        benefit_summary="Low-premium comprehensive crop insurance (2% Kharif, 1.5% Rabi) protecting farmers against drought, flood, pests, and post-harvest loss.",
        localized_summaries={
            "en": "Subsidized crop insurance (1.5%–2% farmer premium) covering natural calamities, pests, and crop yield loss.",
            "hi": "कम प्रीमियम (1.5%-2%) पर फसल बीमा जो बाढ़, सूखा, कीट व फसल नुकसान की भरपाई करता है।",
            "te": "తక్కువ ప్రీమియం (1.5%-2%) తో ప్రకృతి వైపరీత్యాలు మరియు పంట నష్టానికి పూర్తి పంట బీమా.",
            "ta": "குறைந்த பிரீமியத்தில் (1.5%-2%) இயற்கை பேரிடர் மற்றும் பயிர் இழப்புக்கு முழு பயிர் காப்பீடு.",
            "bn": "স্বল্প প্রিমিয়ামে (১.৫%-২%) প্রাকৃতিক দুর্যোগ ও ফসল ক্ষতির সম্পূর্ণ শস্য বীমা।",
            "mr": "कमी हप्त्यात (1.5%-2%) नैसर्गिक आपत्ती व पीक नुकसानीपासून संपूर्ण पीक विमा संरक्षण.",
            "kn": "ಕಡಿಮೆ ಪ್ರೀಮಿಯಂನಲ್ಲಿ (1.5%-2%) ನೈಸರ್ಗಿಕ ವಿಕೋಪ ಮತ್ತು ಬೆಳೆ ನಷ್ಟಕ್ಕೆ ಸಮಗ್ರ ಬೆಳೆ ವಿಮೆ.",
        },
        target_tags=["farmer", "crop insurance", "agriculture", "rural"],
        multilingual_keywords=[
            "farmer", "crop", "insurance", "fasal", "harvest", "किसान", "फसल", "बीमा", "రైతు", "పంట", "బీమా",
            "விவசாயி", "பயிர்", "காப்பீடு", "কৃষক", "ফসল", "বীমা", "शेतकरी", "पीक", "विमा", "ರೈತ", "ಬೆಳೆ", "ವಿಮೆ",
        ],
        full_document_text=(
            "Pradhan Mantri Fasal Bima Yojana (PMFBY) offers financial protection to farmers suffering crop loss "
            "due to unforeseen natural calamities, pests, or diseases. All adult farmers (age >= 18), including "
            "landowners, tenant farmers, and sharecroppers cultivating notified crops, are eligible."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="occupation",
                    operator=RuleOperator.IN,
                    value=["farmer", "tenant_farmer", "sharecropper"],
                    description="Applicant must be an active farmer, tenant farmer, or sharecropper.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=18,
                    description="Farmer applicant must be an adult (age >= 18).",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "PMFBY"),
            _doc(
                "DOC-SOWING",
                "Sowing Certificate / Crop Declaration & Land/Tenancy Proof",
                "Proof of sown crop area from Patwari/Village Officer or tenancy contract.",
                "Gram Panchayat / Agriculture Officer / Bank",
                ["PMFBY"],
                "बुवाई प्रमाण पत्र एवं भूमि/बटाईदार प्रमाण",
                "పంట సాగు ధృవీకరణ పత్రం మరియు భూమి/కౌలు పత్రం",
                "பயிர் சாகுபடி சான்றிதழ் மற்றும் நில/குத்தகை ஆவணம்",
                "বপন শংসাপত্র এবং জমি/বর্গা চুক্তিপত্র",
                "पेरणी प्रमाणपत्र आणि जमीन/कसेल करार",
                "ಬಿತ್ತನೆ ಪ್ರಮಾಣಪತ್ರ ಮತ್ತು ಭೂ/ಗೇಣಿ ದಾಖಲೆ",
            ),
            _with_scheme(DOC_BANK, "PMFBY"),
        ],
        application_steps=[
            "Visit pmfby.gov.in (Farmer Corner) or your nearest Bank / PACS / CSC before the seasonal cutoff date.",
            "Select your State, District, Season (Kharif/Rabi), and notified crop.",
            "Upload Aadhaar, sowing certificate, and land/tenancy record and pay the subsidized farmer premium.",
            "Save the policy acknowledgment number and report any calamity within 72 hours via the Crop Insurance App or helpline.",
        ],
        official_portal="https://pmfby.gov.in",
        helpline="14447",
    ),

    # --------------------------------------------------------------------------
    # 3. PMAY-G (Rural Housing)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="PMAY-G",
        official_name="Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)",
        short_code="PMAY-G",
        ministry="Ministry of Rural Development",
        benefit_summary="Financial assistance of Rs. 1,20,000 (plain areas) or Rs. 1,30,000 (hilly/difficult areas) plus toilet & MGNREGA wage support to build a pucca house.",
        localized_summaries={
            "en": "Rs. 1,20,000–1,30,000 rural housing construction grant for homeless or kutcha-house low-income families.",
            "hi": "कच्चे घर या बेघर ग्रामीण परिवारों को पक्का घर बनाने के लिए ₹1,20,000 से ₹1,30,000 की आर्थिक सहायता।",
            "te": "పక్కా ఇల్లు లేని గ్రామీణ పేద కుటుంబాలకు ఇల్లు కట్టుకోవడానికి రూ. 1,20,000–1,30,000 ఆర్థిక సహాయం.",
            "ta": "நிரந்தர வீடு இல்லாத கிராமப்புற ஏழைக் குடும்பங்களுக்கு கான்கிரீட் வீடு கட்ட ரூ. 1,20,000–1,30,000 மானியம்.",
            "bn": "পাকা বাড়িহীন গ্রামীণ দরিদ্র পরিবারকে পাকা বাড়ি তৈরির জন্য ₹1,20,000–₹1,30,000 অনুদান।",
            "mr": "पक्के घर नसलेल्या ग्रामीण कुटुंबांना घरकुल बांधण्यासाठी ₹1,20,000–₹1,30,000 अनुदान.",
            "kn": "ಪಕ್ಕಾ ಮನೆ ಇಲ್ಲದ ಗ್ರಾಮೀಣ ಬಡ ಕುಟುಂಬಗಳಿಗೆ ಮನೆ ನಿರ್ಮಾಣಕ್ಕೆ ರೂ. 1,20,000–1,30,000 ಸಹಾಯಧನ.",
        },
        target_tags=["rural", "housing", "pucca house", "bpl", "shelter"],
        multilingual_keywords=[
            "rural", "village", "house", "pucca", "kutcha", "awas", "homeless", "गांव", "पक्का घर", "मकान",
            "గ్రామం", "పక్కా ఇల్లు", "ఇల్లు", "கிராமம்", "வீடு", "গ্রাম", "বাড়ি", "ग्रामीण", "घर", "ಹಳ್ಳಿ", "ಮನೆ",
        ],
        full_document_text=(
            "Pradhan Mantri Awaas Yojana - Gramin (PMAY-G) helps rural households living in zero, one, or two room "
            "kutcha houses construct a resilient pucca house with hygienic cooking space. "
            "Eligibility: applicant must reside in a rural area, must NOT own a pucca house, be >= 18 years old, "
            "and have household annual income <= Rs. 3,00,000."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="residence_type",
                    operator=RuleOperator.EQ,
                    value="rural",
                    description="Citizen must reside in a rural area / village.",
                ),
                RuleCondition(
                    field="owns_pucca_house",
                    operator=RuleOperator.BOOL_IS,
                    value=False,
                    description="Household must not already own a permanent pucca house.",
                ),
                RuleCondition(
                    field="annual_income_inr",
                    operator=RuleOperator.LTE,
                    value=300000,
                    description="Annual household income must be <= Rs. 3,00,000.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=18,
                    description="Applicant must be at least 18 years old.",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "PMAY-G"),
            _with_scheme(DOC_BPL_RATION, "PMAY-G"),
            _with_scheme(DOC_INCOME, "PMAY-G"),
            _doc(
                "DOC-NO-HOUSE-DECL",
                "Self-Declaration of No Pucca House & MGNREGA Job Card (if held)",
                "Signed affidavit confirming absence of a pucca house plus MGNREGA Job Card for convergence wages.",
                "Gram Panchayat / Block Development Office (BDO)",
                ["PMAY-G"],
                "पक्का घर न होने का स्व-घोषणा पत्र एवं मनरेगा जॉब कार्ड",
                "పక్కా ఇల్లు లేదని స్వీయ ధృవీకరణ పత్రం",
                "நிரந்தர வீடு இல்லை என்பதற்கான சுய அறிவிப்பு",
                "পাকা বাড়ি না থাকার স্ব-ঘোষণাপত্র",
                "पक्के घर नसल्याचे स्वयंघोषणापत्र",
                "ಪಕ್ಕಾ ಮನೆ ಇಲ್ಲದಿರುವ ಸ್ವಯಂ ಘೋಷಣೆ ಪತ್ರ",
            ),
            _with_scheme(DOC_BANK, "PMAY-G"),
        ],
        application_steps=[
            "Contact your Gram Panchayat Secretary or Block Development Officer (BDO) to check inclusion in the Awaas+ / SECC priority list.",
            "Submit Aadhaar, Ration/BPL Card, Bank Passbook, and No-Pucca-House declaration for Gram Sabha verification.",
            "Once geo-tagged and sanctioned, the grant is released in 3–4 installments linked to construction milestones.",
            "Track installment status on pmayg.nic.in using your Registration ID.",
        ],
        official_portal="https://pmayg.nic.in",
        helpline="1800-11-6446",
    ),

    # --------------------------------------------------------------------------
    # 4. AB-PMJAY (Ayushman Bharat Health Cover)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="AB-PMJAY",
        official_name="Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
        short_code="AB-PMJAY",
        ministry="Ministry of Health and Family Welfare",
        benefit_summary="Rs. 5,00,000 per family per year cashless secondary and tertiary hospitalization cover across empanelled public and private hospitals.",
        localized_summaries={
            "en": "Rs. 5,00,000/year free cashless hospital treatment cover for low-income/BPL families and senior citizens aged 70+.",
            "hi": "कम आय/BPL परिवारों तथा 70+ वरिष्ठ नागरिकों को प्रति वर्ष ₹5,00,000 तक का मुफ्त कैशलेस अस्पताल इलाज।",
            "te": "తక్కువ ఆదాయం/బీపీఎల్ కుటుంబాలకు మరియు 70+ వృద్ధులకు సంవత్సరానికి రూ. 5,00,000 ఉచిత నగదు రహిత వైద్య బీమా.",
            "ta": "குறைந்த வருமானம்/பிபிஎல் குடும்பங்கள் மற்றும் 70+ மூத்த குடிமக்களுக்கு ஆண்டுக்கு ரூ. 5,00,000 இலவச மருத்துவக் காப்பீடு.",
            "bn": "স্বল্প আয়ের/বিপিএল পরিবার ও ৭০+ প্রবীণ নাগরিকদের বছরে ₹5,00,000 বিনামূল্যে ক্যাশলেস চিকিৎসা সুরক্ষা।",
            "mr": "कमी उत्पन्न/बीपीएल कुटुंबे आणि 70+ ज्येष्ठ नागरिकांसाठी दरवर्षी ₹5,00,000 मोफत कॅशलेस उपचार विमा.",
            "kn": "ಕಡಿಮೆ ಆದಾಯ/ಬಿಪಿಎಲ್ ಕುಟುಂಬಗಳಿಗೆ ಹಾಗೂ 70+ ಹಿರಿಯ ನಾಗರಿಕರಿಗೆ ವರ್ಷಕ್ಕೆ ರೂ. 5,00,000 ಉಚಿತ ನಗದು ರಹಿತ ಚಿಕಿತ್ಸೆ.",
        },
        target_tags=["health", "hospital", "medical", "bpl", "senior citizen"],
        multilingual_keywords=[
            "health", "hospital", "medical", "ayushman", "bpl", "senior", "treatment", "बीमार", "अस्पताल", "आयुष्मान", "बीपीएल",
            "ఆరోగ్య", "ఆసుపత్రి", "బీపీఎల్", "மருத்துவ", "ஆயுஷ்மான்", "স্বাস্থ্য", "হাসপাতাল", "आरोग्य", "रुग्णालय", "ಆರೋಗ್ಯ", "ಆಸ್ಪತ್ರೆ",
        ],
        full_document_text=(
            "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY) provides Rs. 5 lakh per family per year "
            "for cashless hospitalization across India. Eligible if ANY of the following holds: "
            "household has a BPL/Antyodaya card, annual household income <= Rs. 2,50,000, OR citizen is aged 70 years or above."
        ),
        rules=EligibilityRuleGroup(
            any_of_groups=[
                [
                    RuleCondition(
                        field="has_bpl_card",
                        operator=RuleOperator.BOOL_IS,
                        value=True,
                        description="Household holds a BPL / SECC priority ration card.",
                    ),
                    RuleCondition(
                        field="annual_income_inr",
                        operator=RuleOperator.LTE,
                        value=250000,
                        description="Annual household income is <= Rs. 2,50,000.",
                    ),
                    RuleCondition(
                        field="age",
                        operator=RuleOperator.GTE,
                        value=70,
                        description="Senior citizens aged 70+ qualify unconditionally under Vaya Vandana extension.",
                    ),
                ]
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "AB-PMJAY"),
            _with_scheme(DOC_BPL_RATION, "AB-PMJAY"),
            _with_scheme(DOC_INCOME, "AB-PMJAY"),
        ],
        application_steps=[
            "Visit beneficiary.nha.gov.in or download the Ayushman App and log in via mobile OTP.",
            "Search your eligibility using Aadhaar, Ration Card, or Senior Citizen 70+ Vaya Vandana option.",
            "Complete Aadhaar e-KYC and download your Ayushman Card.",
            "Present the Ayushman Card at any empanelled hospital Ayushman Mitra desk for cashless admission.",
        ],
        official_portal="https://beneficiary.nha.gov.in",
        helpline="14555 / 1800-11-4477",
    ),

    # --------------------------------------------------------------------------
    # 5. PMUY (Ujjwala LPG)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="PMUY",
        official_name="Pradhan Mantri Ujjwala Yojana (PMUY)",
        short_code="PMUY",
        ministry="Ministry of Petroleum and Natural Gas",
        benefit_summary="Deposit-free clean LPG gas connection, Rs. 1,600 assistance towards cylinder/regulator/hose, free first refill & stove support.",
        localized_summaries={
            "en": "Deposit-free LPG cooking gas connection and Rs. 1,600 support for adult women from low-income/BPL/SC/ST households.",
            "hi": "कम आय, BPL या SC/ST परिवार की वयस्क महिलाओं को बिना सिक्योरिटी जमा मुफ्त एलपीजी गैस कनेक्शन।",
            "te": "తక్కువ ఆదాయం, బీపీఎల్ లేదా ఎస్సీ/ఎస్టీ కుటుంబాల మహిళలకు డిపాజిట్ లేకుండా ఉచిత LPG గ్యాస్ కనెక్షన్.",
            "ta": "குறைந்த வருமானம், பிபிஎல் அல்லது எஸ்சி/எஸ்டி குடும்பப் பெண்களுக்கு வைப்புத்தொகையின்றி இலவச எல்பிஜி சமையல் எரிவாயு இணைப்பு.",
            "bn": "স্বল্প আয়, বিপিএল বা এসসি/এসটি পরিবারের প্রাপ্তবয়স্ক মহিলাদের বিনামূল্যে ডিপোজিট-মুক্ত এলপিজি গ্যাস সংযোগ।",
            "mr": "कमी उत्पन्न, बीपीएल किंवा एससी/एसटी कुटुंबातील महिलांना अनामत शुल्काशिवाय मोफत एलपीजी गॅस जोडणी.",
            "kn": "ಕಡಿಮೆ ಆದಾಯ, ಬಿಪಿಎಲ್ ಅಥವಾ ಎಸ್‌ಸಿ/ಎಸ್‌ಟಿ ಕುಟುಂಬಗಳ ಮಹಿಳೆಯರಿಗೆ ಠೇವಣಿ ರಹಿತ ಉಚಿತ ಎಲ್‌ಪಿಜಿ ಅಡುಗೆ ಅನಿಲ ಸಂಪರ್ಕ.",
        },
        target_tags=["women", "lpg", "gas", "cooking", "bpl", "sc", "st"],
        multilingual_keywords=[
            "woman", "female", "lpg", "gas", "cooking", "ujjwala", "bpl", "महिला", "गैस", "उज्ज्वला",
            "మహిళ", "గ్యాస్", "వంట", "பெண்", "எரிவாயு", "கேஸ்", "মহিলা", "গ্যাস", "स्त्री", "गॅस", "ಮಹಿಳೆ", "ಗ್ಯಾಸ್",
        ],
        full_document_text=(
            "Pradhan Mantri Ujjwala Yojana (PMUY) provides deposit-free LPG connections to adult women (age >= 18) "
            "whose household does not currently have any LPG connection, and belongs to BPL, SC/ST category, or has annual income <= Rs. 2,00,000."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="gender",
                    operator=RuleOperator.EQ,
                    value="female",
                    description="Applicant must be a woman.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=18,
                    description="Applicant must be at least 18 years old.",
                ),
                RuleCondition(
                    field="has_lpg_connection",
                    operator=RuleOperator.BOOL_IS,
                    value=False,
                    description="Household must not already hold an active LPG connection.",
                ),
            ],
            any_of_groups=[
                [
                    RuleCondition(
                        field="has_bpl_card",
                        operator=RuleOperator.BOOL_IS,
                        value=True,
                        description="Household has a BPL / Antyodaya card.",
                    ),
                    RuleCondition(
                        field="annual_income_inr",
                        operator=RuleOperator.LTE,
                        value=200000,
                        description="Annual household income is <= Rs. 2,00,000.",
                    ),
                    RuleCondition(
                        field="social_category",
                        operator=RuleOperator.IN,
                        value=["SC", "ST"],
                        description="Household belongs to SC or ST priority category.",
                    ),
                ]
            ],
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "PMUY"),
            _with_scheme(DOC_BPL_RATION, "PMUY"),
            _with_scheme(DOC_BANK, "PMUY"),
            _with_scheme(DOC_PHOTO, "PMUY"),
        ],
        application_steps=[
            "Visit pmuy.gov.in ('Apply for New Ujjwala 2.0 Connection') or your nearest Indane / Bharatgas / HP Gas distributor.",
            "Choose your preferred Oil Marketing Company and fill the KYC form with Aadhaar, Ration Card, and Bank details.",
            "Submit self-declaration confirming no prior LPG connection in the household.",
            "Collect your deposit-free cylinder and regulator after distributor verification.",
        ],
        official_portal="https://pmuy.gov.in",
        helpline="1800-266-6696",
    ),

    # --------------------------------------------------------------------------
    # 6. PMMVY (Maternity Benefit)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="PMMVY",
        official_name="Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        short_code="PMMVY",
        ministry="Ministry of Women and Child Development",
        benefit_summary="Rs. 5,000 maternity cash benefit (Rs. 6,000 for second girl child) for pregnant women and lactating mothers to support nutrition and wage loss.",
        localized_summaries={
            "en": "Rs. 5,000–6,000 maternity cash incentive for pregnant and lactating women (non-government employees).",
            "hi": "गर्भवती और स्तनपान कराने वाली महिलाओं (गैर-सरकारी) को पोषण व मातृत्व सहायता हेतु ₹5,000–₹6,000 की नकद राशि।",
            "te": "గర్భిణీ మరియు పాలిచ్చే తల్లులకు (ప్రభుత్వ ఉద్యోగి కాని వారికి) పోషకాహారం కోసం రూ. 5,000–6,000 ఆర్థిక సహాయం.",
            "ta": "கர்ப்பிணி மற்றும் பாலூட்டும் தாய்மார்களுக்கு (அரசு ஊழியர் அல்லாதவர்களுக்கு) ரூ. 5,000–6,000 மகப்பேறு நிதி உதவி.",
            "bn": "গর্ভবতী ও স্তন্যদানকারী মায়েদের (অ-সরকারি) পুষ্টি ও মজুরি সহায়তার জন্য ₹5,000–₹6,000 নগদ সহায়তা।",
            "mr": "गर्भवती व स्तनदा मातांना (गैर-सरकारी) पोषण व प्रसूती मदतीसाठी ₹5,000–₹6,000 थेट लाभ.",
            "kn": "ಗರ್ಭಿಣಿ ಮತ್ತು ಹಾಲುಣಿಸುವ ತಾಯಂದಿರಿಗೆ (ಸರ್ಕಾರಿ ನೌಕರರಲ್ಲದವರಿಗೆ) ರೂ. 5,000–6,000 ಮಾತೃ ಸಹಾಯಧನ.",
        },
        target_tags=["pregnant", "maternity", "mother", "women", "nutrition"],
        multilingual_keywords=[
            "pregnant", "lactating", "maternity", "mother", "childbirth", "गर्भवती", "मातृ", "గర్భిణి", "గర్భవతి",
            "கர்ப்பிணி", "தாய்", "গর্ভবতী", "माता", "ಗರ್ಭಿಣಿ",
        ],
        full_document_text=(
            "Pradhan Mantri Matru Vandana Yojana (PMMVY) provides Rs. 5,000 in installments directly into the bank account "
            "of pregnant women and lactating mothers aged 19 to 45 who are not regular government employees."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="gender",
                    operator=RuleOperator.EQ,
                    value="female",
                    description="Applicant must be female.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=19,
                    description="Minimum age for maternity benefit under PMMVY is 19 years.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.LTE,
                    value=45,
                    description="Applicant age within maternal eligibility range (<= 45).",
                ),
                RuleCondition(
                    field="is_pregnant_or_lactating",
                    operator=RuleOperator.BOOL_IS,
                    value=True,
                    description="Applicant must be pregnant or a lactating mother.",
                ),
                RuleCondition(
                    field="is_govt_employee",
                    operator=RuleOperator.BOOL_IS,
                    value=False,
                    description="Regular government/PSU employees receiving paid maternity leave are excluded.",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "PMMVY"),
            _doc(
                "DOC-MCP-CARD",
                "Mother and Child Protection (MCP) Card",
                "Antenatal registration card issued by Anganwadi or Primary Health Centre.",
                "Nearest Anganwadi Centre / ASHA Worker / PHC",
                ["PMMVY"],
                "मातृ एवं शिशु सुरक्षा (MCP) कार्ड",
                "తల్లి మరియు శిశు రక్షణ (MCP) కార్డు",
                "தாய் மற்றும் சேய் பாதுகாப்பு அட்டை (MCP Card)",
                "মা ও শিশু সুরক্ষা (MCP) কার্ড",
                "माता व बाल संरक्षण (MCP) कार्ड",
                "ತಾಯಿ ಮತ್ತು ಮಗು ರಕ್ಷಣಾ (MCP) ಕಾರ್ಡ್",
            ),
            _with_scheme(DOC_BANK, "PMMVY"),
        ],
        application_steps=[
            "Register pregnancy at your nearest Anganwadi Centre (AWC) or via pmmvy.wcd.gov.in.",
            "Obtain your Mother and Child Protection (MCP) Card with LMP and ANC checkup dates.",
            "Submit Aadhaar card and Aadhaar-seeded Bank/Post Office Passbook details.",
            "Receive installments directly via DBT upon antenatal checkups and childbirth/immunization milestones.",
        ],
        official_portal="https://pmmvy.wcd.gov.in",
        helpline="14408",
    ),

    # --------------------------------------------------------------------------
    # 7. IGNOAPS (Old Age Pension)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="IGNOAPS",
        official_name="Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        short_code="IGNOAPS",
        ministry="Ministry of Rural Development (NSAP)",
        benefit_summary="Guaranteed monthly old-age pension (Central base Rs. 200–500 + State top-ups typically totaling Rs. 1,000–2,500/month).",
        localized_summaries={
            "en": "Monthly old-age pension for senior citizens aged 60+ from BPL / low-income households (<= Rs. 1,50,000/year).",
            "hi": "60 वर्ष या अधिक आयु के BPL / कम आय (≤ ₹1.5 लाख) वाले वरिष्ठ नागरिकों को मासिक वृद्धावस्था पेंशन।",
            "te": "60 ఏళ్లు నిండిన బీపీఎల్ / తక్కువ ఆదాయ (<= రూ. 1.5 లక్షలు) వృద్ధులకు నెలవారీ వృద్ధాప్య పెన్షన్.",
            "ta": "60 வயதுக்கு மேற்பட்ட பிபிஎல் / குறைந்த வருமானம் (<= ரூ. 1.5 லட்சம்) கொண்ட முதியவர்களுக்கு மாதாந்திர ஓய்வூதியம்.",
            "bn": "৬০+ বয়সী বিপিএল / স্বল্প আয়ের (≤ ₹১.৫ লক্ষ) প্রবীণ নাগরিকদের মাসিক বার্ধক্য ভাতা।",
            "mr": "60 वर्षांवरील बीपीएल / कमी उत्पन्न (≤ ₹1.5 लाख) ज्येष्ठ नागरिकांना मासिक वृद्धापकाळ निवृत्तीवेतन.",
            "kn": "60 ವರ್ಷ ಮೇಲ್ಪಟ್ಟ ಬಿಪಿಎಲ್ / ಕಡಿಮೆ ಆದಾಯದ (<= ರೂ. 1.5 ಲಕ್ಷ) ಹಿರಿಯ ನಾಗರಿಕರಿಗೆ ಮಾಸಿಕ ವೃದ್ಧಾಪ್ಯ ವೇತನ.",
        },
        target_tags=["senior", "old age", "pension", "elderly", "bpl"],
        multilingual_keywords=[
            "old", "age", "pension", "senior", "elderly", "60", "बुजुर्ग", "पेंशन", "वृद्ध",
            "వృద్ధాప్య", "పెన్షన్", "முதியோர்", "ஓய்வூதியம்", "বার্ধক্য", "ভাতা", "ज्येष्ठ", "पेन्शन", "ಹಿರಿಯ", "ಪಿಂಚಣಿ",
        ],
        full_document_text=(
            "Indira Gandhi National Old Age Pension Scheme (IGNOAPS) under NSAP supports senior citizens aged 60 years "
            "or older belonging to BPL households or having annual household income <= Rs. 1,50,000."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=60,
                    description="Citizen must be aged 60 years or older.",
                )
            ],
            any_of_groups=[
                [
                    RuleCondition(
                        field="has_bpl_card",
                        operator=RuleOperator.BOOL_IS,
                        value=True,
                        description="Citizen belongs to a BPL household.",
                    ),
                    RuleCondition(
                        field="annual_income_inr",
                        operator=RuleOperator.LTE,
                        value=150000,
                        description="Annual household income is <= Rs. 1,50,000.",
                    ),
                ]
            ],
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "IGNOAPS"),
            _with_scheme(DOC_BPL_RATION, "IGNOAPS"),
            _with_scheme(DOC_INCOME, "IGNOAPS"),
            _with_scheme(DOC_BANK, "IGNOAPS"),
        ],
        application_steps=[
            "Visit the UMANG portal/app, State Social Welfare Portal, or your local Gram Panchayat / Municipal Ward Office.",
            "Fill the NSAP Old Age Pension form and attach Aadhaar, age proof, BPL/Income certificate, and Bank Passbook.",
            "After local revenue/social welfare verification, monthly pension is credited directly via DBT.",
        ],
        official_portal="https://nsap.nic.in",
        helpline="1800-11-6446",
    ),

    # --------------------------------------------------------------------------
    # 8. IGNWPS (Widow Pension)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="IGNWPS",
        official_name="Indira Gandhi National Widow Pension Scheme (IGNWPS)",
        short_code="IGNWPS",
        ministry="Ministry of Rural Development (NSAP)",
        benefit_summary="Monthly social security pension (Central base Rs. 300–500 + State top-up) for widowed women aged 40–79.",
        localized_summaries={
            "en": "Monthly financial pension for widowed women aged 40–79 from BPL / low-income households.",
            "hi": "40 से 79 वर्ष की BPL / कम आय वाली विधवा महिलाओं को मासिक आर्थिक पेंशन सहायता।",
            "te": "40–79 ఏళ్ల మధ్య గల బీపీఎల్ / తక్కువ ఆదాయ వితంతువు మహిళలకు నెలవారీ పెన్షన్.",
            "ta": "40–79 வயதுக்குட்பட்ட பிபிஎல் / குறைந்த வருமானம் கொண்ட விதவைப் பெண்களுக்கு மாதாந்திர ஓய்வூதியம்.",
            "bn": "৪০–৭৯ বছর বয়সী বিপিএল / স্বল্প আয়ের বিধবা মহিলাদের মাসিক আর্থিক ভাতা।",
            "mr": "40–79 वयोगटातील बीपीएल / कमी उत्पन्न विधवा महिलांसाठी मासिक पेन्शन योजना.",
            "kn": "40–79 ವರ್ಷ ವಯಸ್ಸಿನ ಬಿಪಿಎಲ್ / ಕಡಿಮೆ ಆದಾಯದ ವಿಧವಾ ಮಹಿಳೆಯರಿಗೆ ಮಾಸಿಕ ಪಿಂಚಣಿ.",
        },
        target_tags=["widow", "women", "pension", "bpl"],
        multilingual_keywords=[
            "widow", "widowed", "pension", "woman", "विधवा", "पेंशन", "వితంతువు", "పెన్షన్",
            "விதவை", "ஓய்வூதியம்", "বিধবা", "ভাতা", "विधवा", "पेन्शन", "ವಿಧವೆ", "ಪಿಂಚಣಿ",
        ],
        full_document_text=(
            "Indira Gandhi National Widow Pension Scheme (IGNWPS) provides monthly pension support to widowed women "
            "aged 40 to 79 years belonging to BPL households or having annual income <= Rs. 1,50,000."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="gender",
                    operator=RuleOperator.EQ,
                    value="female",
                    description="Applicant must be a woman.",
                ),
                RuleCondition(
                    field="marital_status",
                    operator=RuleOperator.EQ,
                    value="widowed",
                    description="Applicant must be widowed.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=40,
                    description="Applicant age must be >= 40 years.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.LTE,
                    value=79,
                    description="Applicant age must be <= 79 years (80+ transitions to senior pension).",
                ),
            ],
            any_of_groups=[
                [
                    RuleCondition(
                        field="has_bpl_card",
                        operator=RuleOperator.BOOL_IS,
                        value=True,
                        description="Applicant holds a BPL card.",
                    ),
                    RuleCondition(
                        field="annual_income_inr",
                        operator=RuleOperator.LTE,
                        value=150000,
                        description="Annual household income is <= Rs. 1,50,000.",
                    ),
                ]
            ],
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "IGNWPS"),
            _doc(
                "DOC-DEATH-CERT",
                "Spouse's Death Certificate",
                "Official death certificate of deceased husband issued by Municipal/Gram Registrar.",
                "Registrar of Births & Deaths / Municipal / Panchayat Office",
                ["IGNWPS"],
                "पति का मृत्यु प्रमाण पत्र",
                "భర్త మరణ ధృవీకరణ పత్రం",
                "கணவரின் இறப்புச் சான்றிதழ்",
                "স্বামীর মৃত্যু শংসাপত্র",
                "पतीचे मृत्यू प्रमाणपत्र",
                "ಪತಿಯ ಮರಣ ಪ್ರಮಾಣಪತ್ರ",
            ),
            _with_scheme(DOC_BPL_RATION, "IGNWPS"),
            _with_scheme(DOC_BANK, "IGNWPS"),
        ],
        application_steps=[
            "Apply at your State Social Welfare Portal, UMANG app, or Gram Panchayat / Municipal Office.",
            "Submit Aadhaar Card, Husband's Death Certificate, BPL/Income Proof, and Bank Passbook.",
            "Upon verification by District Social Welfare Officer, monthly pension starts automatically via DBT.",
        ],
        official_portal="https://nsap.nic.in",
        helpline="1800-11-6446",
    ),

    # --------------------------------------------------------------------------
    # 9. IGNDPS (Severe Disability Pension)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="IGNDPS",
        official_name="Indira Gandhi National Disability Pension Scheme (IGNDPS)",
        short_code="IGNDPS",
        ministry="Ministry of Rural Development (NSAP)",
        benefit_summary="Monthly disability pension (Central base + State top-ups) for citizens with severe (>=80%) or multiple disabilities.",
        localized_summaries={
            "en": "Monthly pension assistance for low-income/BPL citizens aged 18–79 with severe (>=80%) disability.",
            "hi": "80% या अधिक गंभीर दिव्यांगता वाले 18–79 वर्ष के BPL/कम आय नागरिकों को मासिक दिव्यांग पेंशन।",
            "te": "80% లేదా అంతకంటే ఎక్కువ అంగవైకల్యం ఉన్న 18–79 ఏళ్ల బీపీఎల్/తక్కువ ఆదాయ వ్యక్తులకు నెలవారీ పెన్షన్.",
            "ta": "80% அல்லது அதற்கு மேற்பட்ட தீவிர மாற்றுத்திறன் கொண்ட 18–79 வயது பிபிஎல்/குறைந்த வருமான நபர்களுக்கு மாதாந்திர ஓய்வூதியம்.",
            "bn": "৮০% বা তার বেশি গুরুতর প্রতিবন্ধী ১৮–৭৯ বছর বয়সী বিপিএল/স্বল্প আয়ের নাগরিকদের মাসিক ভাতা।",
            "mr": "80% किंवा अधिक गंभीर अपंगत्व असलेल्या 18–79 वयोगटातील बीपीएल/कमी उत्पन्न नागरिकांसाठी मासिक निवृत्तीवेतन.",
            "kn": "80% ಅಥವಾ ಅದಕ್ಕಿಂತ ಹೆಚ್ಚು ತೀವ್ರ ಅಂಗವೈಕಲ್ಯ ಹೊಂದಿರುವ 18–79 ವರ್ಷದ ಬಿಪಿಎಲ್/ಕಡಿಮೆ ಆದಾಯದ ವ್ಯಕ್ತಿಗಳಿಗೆ ಮಾಸಿಕ ಪಿಂಚಣಿ.",
        },
        target_tags=["disability", "divyang", "pension", "bpl"],
        multilingual_keywords=[
            "disability", "disabled", "divyang", "handicapped", "pension", "दिव्यांग", "विकलांग",
            "అంగవైకల్యం", "వికలాంగ", "மாற்றுத்திறனாளி", "প্রতিবন্ধী", "अपंग", "ಅಂಗವೈಕಲ್ಯ", "ವಿಕಲಚೇತನ",
        ],
        full_document_text=(
            "Indira Gandhi National Disability Pension Scheme (IGNDPS) grants monthly pension to persons aged 18–79 "
            "with severe or multiple disabilities (>= 80% certified) from BPL or <= Rs. 1,50,000 income households."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="has_disability",
                    operator=RuleOperator.BOOL_IS,
                    value=True,
                    description="Citizen must have a certified disability.",
                ),
                RuleCondition(
                    field="disability_percentage",
                    operator=RuleOperator.GTE,
                    value=80,
                    description="Certified disability percentage must be >= 80% (severe/multiple disability).",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=18,
                    description="Citizen must be >= 18 years old.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.LTE,
                    value=79,
                    description="Citizen must be <= 79 years old.",
                ),
            ],
            any_of_groups=[
                [
                    RuleCondition(
                        field="has_bpl_card",
                        operator=RuleOperator.BOOL_IS,
                        value=True,
                        description="Citizen belongs to a BPL household.",
                    ),
                    RuleCondition(
                        field="annual_income_inr",
                        operator=RuleOperator.LTE,
                        value=150000,
                        description="Annual household income is <= Rs. 1,50,000.",
                    ),
                ]
            ],
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "IGNDPS"),
            _doc(
                "DOC-UDID",
                "UDID Card / Medical Disability Certificate (>= 80%)",
                "Unique Disability ID card or District Medical Board disability certificate.",
                "swavlambancard.gov.in / District Government Hospital",
                ["IGNDPS"],
                "यूडीआईडी (UDID) कार्ड / मेडिकल दिव्यांगता प्रमाण पत्र",
                "యుడిఐడి (UDID) కార్డు / మెడికల్ వైకల్య ధృవీకరణ పత్రం",
                "யுடிஐடி (UDID) அட்டை / மருத்துவ மாற்றுத்திறன் சான்றிதழ்",
                "ইউডিআইডি (UDID) কার্ড / প্রতিবন্ধী শংসাপত্র",
                "यूडीआयडी (UDID) कार्ड / वैद्यकीय अपंगत्व प्रमाणपत्र",
                "ಯುಡಿಐಡಿ (UDID) ಕಾರ್ಡ್ / ವೈದ್ಯಕೀಯ ಅಂಗವೈಕಲ್ಯ ಪ್ರಮಾಣಪತ್ರ",
            ),
            _with_scheme(DOC_BPL_RATION, "IGNDPS"),
            _with_scheme(DOC_BANK, "IGNDPS"),
        ],
        application_steps=[
            "Ensure you possess a UDID card from swavlambancard.gov.in showing disability percentage >= 80%.",
            "Submit the IGNDPS application at your Gram Panchayat, Municipal Office, or UMANG / State Social Welfare portal.",
            "Attach Aadhaar, UDID/Medical Certificate, BPL/Income Proof, and Bank Passbook.",
            "Receive monthly disability pension directly via DBT after district approval.",
        ],
        official_portal="https://nsap.nic.in",
        helpline="1800-11-6446",
    ),

    # --------------------------------------------------------------------------
    # 10. ADIP-DIVYANG (Assistive Devices for >=40% Disability)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="ADIP-DIVYANG",
        official_name="Assistance to Disabled Persons for Purchase/Fitting of Aids and Appliances (ADIP)",
        short_code="ADIP-DIVYANG",
        ministry="Ministry of Social Justice and Empowerment",
        benefit_summary="Free or subsidized modern assistive devices (motorized tricycles, wheelchairs, hearing aids, Braille kits, prosthetics) up to Rs. 30,000+.",
        localized_summaries={
            "en": "Free assistive aids & appliances (wheelchairs, hearing aids, tricycles, prosthetics) for >=40% disabled citizens.",
            "hi": "40% या अधिक दिव्यांग नागरिकों को मुफ्त सहायक उपकरण (व्हीलचेयर, ट्राइसाइकिल, श्रवण यंत्र, कृत्रिम अंग)।",
            "te": "40% లేదా అంతకంటే ఎక్కువ వైకల్యం ఉన్నవారికి ఉచిత సహాయక పరికరాలు (వీల్‌చైర్, వినికిడి యంత్రం, ట్రైసైకిల్).",
            "ta": "40% அல்லது அதற்கு மேற்பட்ட மாற்றுத்திறனாளிகளுக்கு இலவச உதவி உபகரணங்கள் (சக்கர நாற்காலி, காது கேட்கும் கருவி).",
            "bn": "৪০% বা ততোধিক প্রতিবন্ধী ব্যক্তিদের বিনামূল্যে সহায়ক যন্ত্রপাতি (হুইলচেয়ার, হিয়ারিং এইড, ট্রাইসাইকেল)।",
            "mr": "40% किंवा अधिक अपंग असलेल्या व्यक्तींना मोफत सहाय्यक साधने (व्हीलचेअर, श्रवणयंत्र, ट्रायसायकल).",
            "kn": "40% ಅಥವಾ ಅದಕ್ಕಿಂತ ಹೆಚ್ಚು ಅಂಗವೈಕಲ್ಯ ಹೊಂದಿರುವವರಿಗೆ ಉಚಿತ ಸಹಾಯಕ ಸಾಧನಗಳು (ವೀಲ್‌ಚೇರ್, ಶ್ರವಣ ಸಾಧನ).",
        },
        target_tags=["disability", "divyang", "assistive devices", "wheelchair", "aids"],
        multilingual_keywords=[
            "disability", "divyang", "wheelchair", "aids", "appliances", "दिव्यांग", "అంగవైకల్యం",
            "மாற்றுத்திறனாளி", "প্রতিবন্ধী", "अपंग", "ಅಂಗವೈಕಲ್ಯ",
        ],
        full_document_text=(
            "The ADIP Scheme provides modern, standardized assistive aids and appliances to Persons with Disabilities "
            "(>= 40% disability certified by UDID/Medical Board) whose annual household income is <= Rs. 3,60,000."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="has_disability",
                    operator=RuleOperator.BOOL_IS,
                    value=True,
                    description="Citizen must have a certified disability.",
                ),
                RuleCondition(
                    field="disability_percentage",
                    operator=RuleOperator.GTE,
                    value=40,
                    description="Disability percentage must be >= 40% benchmark disability.",
                ),
                RuleCondition(
                    field="annual_income_inr",
                    operator=RuleOperator.LTE,
                    value=360000,
                    description="Annual household income must be <= Rs. 3,60,000 (Rs. 30,000/month).",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "ADIP-DIVYANG"),
            _doc(
                "DOC-UDID-40",
                "UDID Card / Disability Certificate (>= 40%)",
                "Certified benchmark disability card showing >= 40% impairment.",
                "swavlambancard.gov.in / District Civil Hospital",
                ["ADIP-DIVYANG"],
                "यूडीआईडी (UDID) कार्ड (≥40% दिव्यांगता)",
                "యుడిఐడి (UDID) కార్డు (>=40% వైకల్యం)",
                "யுடிஐடி அட்டை (>=40% மாற்றுத்திறன்)",
                "ইউডিআইডি কার্ড (≥৪০% প্রতিবন্ধকতা)",
                "यूडीआयडी कार्ड (≥40% अपंगत्व)",
                "ಯುಡಿಐಡಿ ಕಾರ್ಡ್ (>=40% ಅಂಗವೈಕಲ್ಯ)",
            ),
            _with_scheme(DOC_INCOME, "ADIP-DIVYANG"),
            _with_scheme(DOC_PHOTO, "ADIP-DIVYANG"),
        ],
        application_steps=[
            "Check upcoming ALIMCO / District Disability Rehabilitation Centre (DDRC) assessment camps or apply via disabilityaffairs.gov.in.",
            "Bring Aadhaar, UDID (>=40%), Income Certificate, and passport photos for clinical assessment.",
            "Collect prescribed assistive aid/appliance free of cost at the distribution camp.",
        ],
        official_portal="https://disabilityaffairs.gov.in",
        helpline="1800-572-6422",
    ),

    # --------------------------------------------------------------------------
    # 11. NSP-PMS (Post-Matric Scholarship)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="NSP-PMS",
        official_name="National Post-Matric Scholarship Scheme (NSP-PMS)",
        short_code="NSP-PMS",
        ministry="Ministry of Social Justice / Tribal Affairs / Minority Affairs",
        benefit_summary="Full compulsory tuition fee reimbursement plus monthly academic maintenance allowance for SC/ST/OBC/EBC/Minority college & post-matric students.",
        localized_summaries={
            "en": "Tuition fee reimbursement and monthly maintenance allowance for SC/ST/OBC/EBC/Minority students after Class 10.",
            "hi": "SC/ST/OBC/EBC/अल्पसंख्यक कॉलेज व उच्चतर छात्रों को पूरी ट्यूशन फीस व मासिक छात्रवृत्ति सहायता।",
            "te": "SC/ST/OBC/EBC/మైనారిటీ కళాశాల మరియు ఉన్నత విద్యార్థులకు పూర్తి ట్యూషన్ ఫీజు మరియు నెలవారీ స్కాలర్‌షిప్.",
            "ta": "SC/ST/OBC/EBC/சிறுபான்மையின கல்லூரி மாணவர்களுக்கு முழு கல்விக் கட்டணம் மற்றும் மாதாந்திர உதவித்தொகை.",
            "bn": "SC/ST/OBC/EBC/সংখ্যালঘু কলেজ শিক্ষার্থীদের সম্পূর্ণ টিউশন ফি ও মাসিক বৃত্তি।",
            "mr": "SC/ST/OBC/EBC/अल्पसंख्याक महाविद्यालयीन विद्यार्थ्यांना संपूर्ण शैक्षणिक शुल्क व मासिक शिष्यवृत्ती.",
            "kn": "SC/ST/OBC/EBC/ಅಲ್ಪಸಂಖ್ಯಾತ ಕಾಲೇಜು ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಸಂಪೂರ್ಣ ಶುಲ್ಕ ಮರುಪಾವತಿ ಮತ್ತು ಮಾಸಿಕ ವಿದ್ಯಾರ್ಥಿವೇತನ.",
        },
        target_tags=["student", "scholarship", "college", "education", "obc", "sc", "st"],
        multilingual_keywords=[
            "student", "scholarship", "college", "undergraduate", "postgraduate", "diploma", "obc", "sc", "st", "education",
            "छात्र", "छात्रवृत्ति", "कॉलेज", "విద్యార్థి", "స్కాలర్‌షిప్", "మాణவர்", "மாணவர்", "উপবৃত্তি", "ছাত্র", "शिष्यवृत्ती", "ವಿದ್ಯಾರ್ಥಿ", "ವಿದ್ಯಾರ್ಥಿವೇತನ",
        ],
        full_document_text=(
            "National Post-Matric Scholarship Scheme (NSP-PMS) supports students pursuing Class 11/12, diploma, "
            "undergraduate, or postgraduate studies who belong to SC, ST, OBC, EBC, or Minority categories, "
            "are aged 15–35, and have annual family income <= Rs. 2,50,000."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="occupation",
                    operator=RuleOperator.EQ,
                    value="student",
                    description="Citizen must currently be an enrolled student.",
                ),
                RuleCondition(
                    field="education_level",
                    operator=RuleOperator.IN,
                    value=["class_11_12", "high_school_completed", "diploma", "undergraduate", "postgraduate"],
                    description="Student must be pursuing post-matric education (Class 11/12, Diploma, UG, or PG).",
                ),
                RuleCondition(
                    field="social_category",
                    operator=RuleOperator.IN,
                    value=["SC", "ST", "OBC", "EBC", "Minority"],
                    description="Student must belong to SC, ST, OBC, EBC, or Minority category.",
                ),
                RuleCondition(
                    field="annual_income_inr",
                    operator=RuleOperator.LTE,
                    value=250000,
                    description="Annual family income must be <= Rs. 2,50,000.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=15,
                    description="Student age must be >= 15 years.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.LTE,
                    value=35,
                    description="Student age must be <= 35 years.",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "NSP-PMS"),
            _with_scheme(DOC_CASTE, "NSP-PMS"),
            _with_scheme(DOC_INCOME, "NSP-PMS"),
            _doc(
                "DOC-BONAFIDE",
                "Bonafide Student Certificate, Fee Receipt & Previous Marksheet",
                "Current academic year enrollment proof and last qualifying exam marksheet.",
                "School / College Principal or Registrar Office",
                ["NSP-PMS", "PM-YASASVI"],
                "बोनाफाइड छात्र प्रमाण पत्र, शुल्क रसीद एवं पिछली अंकसूची",
                "బోనఫైడ్ సర్టిఫికెట్, ఫీజు రసీదు మరియు గత మార్కుల జాబితా",
                "கல்லூரி போனபைட் சான்றிதழ், கட்டண ரசீது மற்றும் மதிப்பெண் பட்டியல்",
                "বোনাফাইড শংসাপত্র, ফি রসিদ ও পূর্ববর্তী মার্কশিট",
                "बोनाफाईड प्रमाणपत्र, फी पावती व मागील गुणपत्रिका",
                "ಬೋನಾಫೈಡ್ ಪ್ರಮಾಣಪತ್ರ, ಶುಲ್ಕ ರಶೀದಿ ಮತ್ತು ಹಿಂದಿನ ಅಂಕಪಟ್ಟಿ",
            ),
            _with_scheme(DOC_BANK, "NSP-PMS"),
        ],
        application_steps=[
            "Register on scholarships.gov.in (National Scholarship Portal) and generate your One-Time Registration (OTR) ID.",
            "Log in, select 'Post-Matric Scholarship' matching your category, and upload caste, income, marksheet, and fee receipt.",
            "Submit printout to your college/institute nodal officer for online verification.",
            "Track DBT disbursement directly on the NSP portal.",
        ],
        official_portal="https://scholarships.gov.in",
        helpline="0120-6619540",
    ),

    # --------------------------------------------------------------------------
    # 12. PM-YASASVI
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="PM-YASASVI",
        official_name="PM Young Achievers Scholarship Award Scheme (PM-YASASVI)",
        short_code="PM-YASASVI",
        ministry="Ministry of Social Justice and Empowerment",
        benefit_summary="Merit-cum-means scholarship grant up to Rs. 75,000/year (Class 9–10) and Rs. 1,25,000/year (Class 11–12 / Top-Class College) for OBC/EBC/DNT students.",
        localized_summaries={
            "en": "Up to Rs. 75,000–1,25,000/year scholarship for OBC, EBC, and DNT students aged 13–22 with family income <= Rs. 2.5L.",
            "hi": "OBC, EBC और DNT वर्ग के छात्रों (13–22 वर्ष, आय ≤ ₹2.5 लाख) को ₹75,000–₹1,25,000/वर्ष तक की छात्रवृत्ति।",
            "te": "OBC, EBC మరియు DNT విద్యార్థులకు (13–22 ఏళ్లు, ఆదాయం <= రూ. 2.5 లక్షలు) రూ. 75,000–1,25,000/సంవత్సరం స్కాలర్‌షిప్.",
            "ta": "OBC, EBC மற்றும் DNT மாணவர்களுக்கு (13–22 வயது, வருமானம் <= ரூ. 2.5 லட்சம்) ஆண்டுக்கு ரூ. 75,000–1,25,000 உதவித்தொகை.",
            "bn": "OBC, EBC ও DNT শিক্ষার্থীদের (১৩–২২ বছর, আয় ≤ ₹২.৫ লক্ষ) বছরে ₹75,000–₹1,25,000 পর্যন্ত বৃত্তি।",
            "mr": "OBC, EBC आणि DNT विद्यार्थ्यांना (वय 13–22, उत्पन्न ≤ ₹2.5 लाख) दरवर्षी ₹75,000–₹1,25,000 शिष्यवृत्ती.",
            "kn": "OBC, EBC ಮತ್ತು DNT ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ (13–22 ವರ್ಷ, ಆದಾಯ <= ರೂ. 2.5 ಲಕ್ಷ) ವರ್ಷಕ್ಕೆ ರೂ. 75,000–1,25,000 ವಿದ್ಯಾರ್ಥಿವೇತನ.",
        },
        target_tags=["student", "scholarship", "obc", "ebc", "dnt", "merit"],
        multilingual_keywords=[
            "student", "yasasvi", "scholarship", "obc", "ebc", "college", "school", "छात्र", "ओबीसी", "విద్యార్థి",
            "மாணவர்", "ছাত্র", "विद्यार्थी", "ವಿದ್ಯಾರ್ಥಿ",
        ],
        full_document_text=(
            "PM Young Achievers Scholarship Award Scheme (PM-YASASVI) awards high-value scholarships for OBC, EBC, "
            "and DNT students aged 13 to 22 with annual family income <= Rs. 2,50,000."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="occupation",
                    operator=RuleOperator.EQ,
                    value="student",
                    description="Applicant must be a student.",
                ),
                RuleCondition(
                    field="social_category",
                    operator=RuleOperator.IN,
                    value=["OBC", "EBC", "DNT"],
                    description="Student must belong to OBC, EBC, or DNT social category.",
                ),
                RuleCondition(
                    field="annual_income_inr",
                    operator=RuleOperator.LTE,
                    value=250000,
                    description="Annual family income must be <= Rs. 2,50,000.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=13,
                    description="Student age must be >= 13 years.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.LTE,
                    value=22,
                    description="Student age must be <= 22 years.",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "PM-YASASVI"),
            _with_scheme(DOC_CASTE, "PM-YASASVI"),
            _with_scheme(DOC_INCOME, "PM-YASASVI"),
            _doc(
                "DOC-ADMISSION-MARKSHEET",
                "Institution Admission Proof & Previous Class Marksheet",
                "Verified admission letter / Bonafide proof and latest board/semester marksheet.",
                "School / College Administration",
                ["PM-YASASVI"],
                "प्रवेश प्रमाण एवं पिछली कक्षा की अंकसूची",
                "ప్రవేశ ధృవీకరణ మరియు మార్కుల జాబితా",
                "சேர்க்கை சான்றிதழ் மற்றும் மதிப்பெண் பட்டியல்",
                "ভর্তির প্রমাণপত্র ও পূর্ববর্তী মার্কশিট",
                "प्रवेश प्रमाणपत्र व मागील गुणपत्रिका",
                "ಪ್ರವೇಶ ಪತ್ರ ಮತ್ತು ಹಿಂದಿನ ಅಂಕಪಟ್ಟಿ",
            ),
            _with_scheme(DOC_BANK, "PM-YASASVI"),
        ],
        application_steps=[
            "Apply through the National Scholarship Portal (scholarships.gov.in) under the PM-YASASVI scheme window.",
            "Upload OBC/EBC/DNT certificate, Income certificate, marksheet, and Aadhaar-seeded bank passbook.",
            "Complete institution and state nodal officer verification to receive annual scholarship DBT.",
        ],
        official_portal="https://yet.nta.ac.in",
        helpline="011-40759000",
    ),

    # --------------------------------------------------------------------------
    # 13. PM-SVANIDHI (Street Vendor Micro-Credit)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="PM-SVANIDHI",
        official_name="PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)",
        short_code="PM-SVANIDHI",
        ministry="Ministry of Housing and Urban Affairs",
        benefit_summary="Collateral-free working capital micro-loan starting at Rs. 10,000 (scalable to Rs. 20,000 and Rs. 50,000) with 7% interest subsidy and digital cashback.",
        localized_summaries={
            "en": "Collateral-free Rs. 10,000–50,000 working capital loan with 7% interest subsidy for urban street vendors.",
            "hi": "शहरी रेहड़ी-पटरी विक्रेताओं को बिना गारंटी ₹10,000 से ₹50,000 तक कार्यशील पूंजी ऋण व 7% ब्याज सब्सिडी।",
            "te": "పట్టణ వీధి వ్యాపారులకు హామీ లేకుండా రూ. 10,000–50,000 రుణం మరియు 7% వడ్డీ రాయితీ.",
            "ta": "நகர்ப்புற தெரு வியாபாரிகளுக்கு பிணையில்லா ரூ. 10,000–50,000 கடன் மற்றும் 7% வட்டி மானியம்.",
            "bn": "শহরের রাস্তার হকারদের জামানত-মুক্ত ₹10,000–₹50,000 ঋণ ও ৭% সুদে ভর্তুকি।",
            "mr": "शहरी पथविक्रेत्यांना विनातारण ₹10,000–₹50,000 खेळते भांडवल कर्ज व 7% व्याज अनुदान.",
            "kn": "ನಗರ ಬೀದಿ ಬದಿ ವ್ಯಾಪಾರಿಗಳಿಗೆ ಭದ್ರತೆ ರಹಿತ ರೂ. 10,000–50,000 ಸಾಲ ಮತ್ತು 7% ಬಡ್ಡಿ ಸಹಾಯಧನ.",
        },
        target_tags=["street vendor", "urban", "micro loan", "hawker", "business"],
        multilingual_keywords=[
            "street vendor", "vendor", "hawker", "urban", "svanidhi", "रेहड़ी", "पटरी", "हॉकर",
            "వీధి వ్యాపారి", "தெரு வியாபாரி", "রাস্তার হকার", "पथविक्रेता", "ಬೀದಿ ವ್ಯಾಪಾರಿ",
        ],
        full_document_text=(
            "PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi) empowers adult street vendors / hawkers (age >= 18) "
            "operating in urban or semi-urban areas with collateral-free working capital loans."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="occupation",
                    operator=RuleOperator.EQ,
                    value="street_vendor",
                    description="Citizen must be a street vendor / hawker.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=18,
                    description="Applicant must be >= 18 years old.",
                ),
                RuleCondition(
                    field="residence_type",
                    operator=RuleOperator.IN,
                    value=["urban", "semi_urban"],
                    description="Vendor must operate within urban or semi-urban municipal limits.",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "PM-SVANIDHI"),
            _doc(
                "DOC-VENDING-CERT",
                "Certificate of Vending (CoV) or ULB Letter of Recommendation",
                "Municipal vending ID or Urban Local Body recommendation letter.",
                "Municipal Corporation / Town Vending Committee / CSC",
                ["PM-SVANIDHI"],
                "वेंडिंग प्रमाण पत्र (CoV) या नगर निगम अनुशंसा पत्र",
                "వీధి వ్యాపార సర్టిఫికెట్ (CoV) / మున్సిపల్ లేఖ",
                "தெரு வியாபார சான்றிதழ் (CoV) / நகராட்சி பரிந்துரை",
                "হকার শংসাপত্র (CoV) বা পৌরসভার সুপারিশপত্র",
                "पथविक्रेता प्रमाणपत्र (CoV) / महानगरपालिका शिफारस पत्र",
                "ಬೀದಿ ವ್ಯಾಪಾರ ಪ್ರಮಾಣಪತ್ರ (CoV) / ನಗರಸಭೆ ಪತ್ರ",
            ),
            _with_scheme(DOC_BANK, "PM-SVANIDHI"),
        ],
        application_steps=[
            "Visit pmsvanidhi.mohua.gov.in or your nearest CSC with your Aadhaar-linked mobile number.",
            "Enter Certificate of Vending (CoV) / Survey ID or request a municipal Letter of Recommendation online.",
            "Choose your preferred lending bank/MFI and submit KYC.",
            "Upon loan disbursal, accept UPI payments to earn monthly digital cashback and 7% interest subsidy.",
        ],
        official_portal="https://pmsvanidhi.mohua.gov.in",
        helpline="1800-11-1979",
    ),

    # --------------------------------------------------------------------------
    # 14. PM-VISHWAKARMA (Traditional Artisans & Craftspeople)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="PM-VISHWAKARMA",
        official_name="PM Vishwakarma Yojana",
        short_code="PM-VISHWAKARMA",
        ministry="Ministry of Micro, Small and Medium Enterprises",
        benefit_summary="Official Vishwakarma ID & certificate, Rs. 500/day skill training stipend, Rs. 15,000 toolkit e-voucher, and collateral-free enterprise loan up to Rs. 3,00,000 at 5% interest.",
        localized_summaries={
            "en": "Rs. 15,000 toolkit grant, Rs. 500/day training stipend, and 5% low-interest credit up to Rs. 3L for traditional artisans.",
            "hi": "पारंपरिक कारीगरों (कुम्हार, बढ़ई, दर्जी, बुनकर आदि) को ₹15,000 टूलकिट अनुदान, ₹500/दिन प्रशिक्षण व 5% ब्याज पर ₹3 लाख ऋण।",
            "te": "సాంప్రదాయ హస్తకళాకారులకు (కుమ్మరి, వడ్రంగి, టైలర్, నేత) రూ. 15,000 టూల్‌కిట్, రూ. 500/రోజు శిక్షణ భత్యం మరియు 5% వడ్డీకి రూ. 3 లక్షల రుణం.",
            "ta": "பாரம்பரிய கைவினைஞர்களுக்கு (தச்சர், குயவர், தையல்காரர், நெசவாளர்) ரூ. 15,000 கருவி மானியம் மற்றும் 5% வட்டியில் ரூ. 3 லட்சம் கடன்.",
            "bn": "ঐতিহ্যবাহী কারিগরদের (কুমোর, ছুতার, দর্জি, তাঁতি) ₹15,000 টুলকিট অনুদান ও ৫% সুদে ₹৩ লক্ষ ঋণ।",
            "mr": "पारंपारिक कारागिरांना (कुंभार, सुतार, शिंपी, विणकर) ₹15,000 टूलकिट अनुदान व 5% दराने ₹3 लाख कर्ज.",
            "kn": "ಸಾಂಪ್ರದಾಯಿಕ ಕುಶಲಕರ್ಮಿಗಳಿಗೆ (ಕುಂಬಾರ, ಬಡಗಿ, ದರ್ಜಿ, ನೇಕಾರ) ರೂ. 15,000 ಟೂಲ್‌ಕಿಟ್ ಮತ್ತು 5% ಬಡ್ಡಿಯಲ್ಲಿ ರೂ. 3 ಲಕ್ಷ ಸಾಲ.",
        },
        target_tags=["artisan", "craftsperson", "potter", "carpenter", "tailor", "weaver", "toolkit"],
        multilingual_keywords=[
            "artisan", "craftsperson", "potter", "carpenter", "tailor", "weaver", "blacksmith", "barber", "goldsmith",
            "कारीगर", "कुम्हार", "बढ़ई", "दर्जी", "बुनकर", "కుమ్మరి", "చేనేత", "கைவினைஞர்", "কারিগর", "কুমোর", "कारागीर", "कुंभार", "ಕುಶಲಕರ್ಮಿ", "ಕುಂಬಾರ",
        ],
        full_document_text=(
            "PM Vishwakarma Yojana supports traditional self-employed artisans and craftspeople across 18 trades "
            "(carpenters, potters, blacksmiths, tailors, cobblers, weavers, goldsmiths, barbers) aged >= 18 who are not government employees."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="occupation",
                    operator=RuleOperator.IN,
                    value=[
                        "artisan", "craftsperson", "carpenter", "blacksmith",
                        "potter", "tailor", "cobbler", "weaver", "goldsmith", "barber",
                    ],
                    description="Citizen must work in one of the recognized traditional artisan trades.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=18,
                    description="Artisan must be at least 18 years old.",
                ),
                RuleCondition(
                    field="is_govt_employee",
                    operator=RuleOperator.BOOL_IS,
                    value=False,
                    description="Government employees and their immediate family are excluded.",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "PM-VISHWAKARMA"),
            _with_scheme(DOC_BPL_RATION, "PM-VISHWAKARMA"),
            _with_scheme(DOC_BANK, "PM-VISHWAKARMA"),
        ],
        application_steps=[
            "Visit your nearest Common Service Centre (CSC) for biometric Aadhaar registration on pmvishwakarma.gov.in.",
            "Select your traditional trade and submit Ration Card and Bank Passbook details.",
            "Complete 3-stage verification by Gram Panchayat / ULB and District Committee.",
            "Attend 5–7 day skill training (Rs. 500/day stipend) to unlock Rs. 15,000 toolkit voucher and 5% credit.",
        ],
        official_portal="https://pmvishwakarma.gov.in",
        helpline="1800-267-7777",
    ),

    # --------------------------------------------------------------------------
    # 15. PMMY (MUDRA Micro/Small Business Loan)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="PMMY",
        official_name="Pradhan Mantri MUDRA Yojana (PMMY)",
        short_code="PMMY",
        ministry="Ministry of Finance",
        benefit_summary="Collateral-free institutional business loans up to Rs. 10,00,000 (Shishu <=50k, Kishore <=5L, Tarun <=10L) for micro/small enterprises.",
        localized_summaries={
            "en": "Collateral-free micro & small business loans up to Rs. 10,00,000 (Shishu/Kishore/Tarun) for entrepreneurs and artisans.",
            "hi": "छोटे व्यापारियों, स्वरोजगार व कारीगरों को बिना गारंटी ₹10,00,000 तक का मुद्रा बिजनेस लोन।",
            "te": "చిన్న వ్యాపారులు, స్వయం ఉపాధి మరియు హస్తకళాకారులకు హామీ లేకుండా రూ. 10,00,000 వరకు ముద్రా వ్యాపార రుణం.",
            "ta": "சிறு வணிகர்கள் மற்றும் சுயதொழில் முனைவோருக்கு பிணையில்லா ரூ. 10,00,000 வரை முத்ரா தொழில் கடன்.",
            "bn": "ক্ষুদ্র ব্যবসায়ী, স্বনিযুক্ত ও কারিগরদের জামানত-মুক্ত ₹10,00,000 পর্যন্ত মুদ্রা ব্যবসা ঋণ।",
            "mr": "लहान व्यावसायिक, स्वयंरोजगार व कारागिरांना विनातारण ₹10,00,000 पर्यंत मुद्रा व्यवसाय कर्ज.",
            "kn": "ಸಣ್ಣ ವ್ಯಾಪಾರಿಗಳು, ಸ್ವಯಂ ಉದ್ಯೋಗಿಗಳಿಗೆ ಭದ್ರತೆ ರಹಿತ ರೂ. 10,00,000 ವರೆಗೆ ಮುದ್ರಾ ವ್ಯಾಪಾರ ಸಾಲ.",
        },
        target_tags=["business", "loan", "mudra", "entrepreneur", "shopkeeper", "artisan"],
        multilingual_keywords=[
            "business", "loan", "mudra", "self employed", "shopkeeper", "vendor", "artisan", "entrepreneur",
            "व्यापार", "बिजनेस", "दुकान", "వ్యాపారం", "రుణం", "வணிகம்", "கடன்", "ব্যবসা", "ঋণ", "व्यवसाय", "कर्ज", "ವ್ಯಾಪಾರ", "ಸಾಲ",
        ],
        full_document_text=(
            "Pradhan Mantri MUDRA Yojana (PMMY) provides collateral-free loans up to Rs. 10 lakh to non-corporate, "
            "non-farm small/micro enterprises including small businesses, shopkeepers, street vendors, and artisans aged 18–65."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="occupation",
                    operator=RuleOperator.IN,
                    value=[
                        "small_business", "self_employed", "artisan", "street_vendor",
                        "micro_entrepreneur", "tailor", "shopkeeper", "craftsperson",
                    ],
                    description="Citizen must run or start a small/micro non-farm business, trade, or service.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=18,
                    description="Applicant must be >= 18 years old.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.LTE,
                    value=65,
                    description="Applicant must be <= 65 years old.",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "PMMY"),
            _doc(
                "DOC-PAN-BIZ",
                "PAN Card & Business Activity / Address Proof",
                "Applicant PAN card and simple business quote/bill/udyam proof.",
                "Income Tax Portal / Udyam Registration Portal",
                ["PMMY"],
                "पैन कार्ड एवं व्यवसाय का प्रमाण",
                "పాన్ కార్డు మరియు వ్యాపార చిరునామా రుజువు",
                "பான் கார்டு மற்றும் தொழில் சான்று",
                "প্যান কার্ড ও ব্যবসার প্রমাণপত্র",
                "पॅन कार्ड आणि व्यवसायाचा पुरावा",
                "ಪ್ಯಾನ್ ಕಾರ್ಡ್ ಮತ್ತು ವ್ಯಾಪಾರದ ದಾಖಲೆ",
            ),
            _with_scheme(DOC_BANK, "PMMY"),
            _with_scheme(DOC_PHOTO, "PMMY"),
        ],
        application_steps=[
            "Apply online via jansamarth.in or udyamimitra.in, or visit any Public/Private Sector Bank or RRB branch.",
            "Select Shishu (up to Rs. 50,000), Kishore (up to Rs. 5L), or Tarun (up to Rs. 10L) category.",
            "Submit Aadhaar, PAN, passport photos, and business plan/quotation (no collateral security required).",
            "Receive Mudra Loan sanction directly to your business bank account.",
        ],
        official_portal="https://www.jansamarth.in",
        helpline="1800-180-1111",
    ),

    # --------------------------------------------------------------------------
    # 16. SSY (Sukanya Samriddhi Yojana)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="SSY",
        official_name="Sukanya Samriddhi Yojana (SSY)",
        short_code="SSY",
        ministry="Ministry of Finance",
        benefit_summary="Government-backed savings scheme offering 8.2% p.a. compound interest with full EEE income tax exemption for a girl child's education & marriage.",
        localized_summaries={
            "en": "8.2% p.a. tax-free government savings account for parents/guardians of a girl child under 10 years.",
            "hi": "10 वर्ष से कम उम्र की बेटी के माता-पिता/अभिभावकों के लिए 8.2% ब्याज व टैक्स-फ्री सुकन्या समृद्धि बचत योजना।",
            "te": "10 ఏళ్లలోపు ఆడపిల్ల తల్లిదండ్రులకు 8.2% వడ్డీతో పన్ను రహిత సుకన్య సమృద్ధి పొదుపు ఖాతా.",
            "ta": "10 வயதுக்குட்பட்ட பெண் குழந்தையின் பெற்றோர்களுக்கு 8.2% வட்டியுடன் வரி விலக்கு பெற்ற சுகன்யா சம்ரிதி சேமிப்புத் திட்டம்.",
            "bn": "১০ বছরের কম বয়সী কন্যা সন্তানের অভিভাবকদের জন্য ৮.২% সুদে করমুক্ত সুকন্যা সমৃদ্ধি সঞ্চয় প্রকল্প।",
            "mr": "10 वर्षांखालील मुलीच्या पालकांसाठी 8.2% व्याज व करमुक्त सुकन्या समृद्धी बचत योजना.",
            "kn": "10 ವರ್ಷದೊಳಗಿನ ಹೆಣ್ಣು ಮಗುವಿನ ಪೋಷಕರಿಗೆ 8.2% ಬಡ್ಡಿ ಮತ್ತು ತೆರಿಗೆ ರಹಿತ ಸುಕನ್ಯಾ ಸಮೃದ್ಧಿ ಉಳಿತಾಯ ಯೋಜನೆ.",
        },
        target_tags=["girl child", "daughter", "savings", "education", "tax free"],
        multilingual_keywords=[
            "girl child", "daughter", "sukanya", "child", "बेटी", "सुकन्या", "ఆడపిల్ల", "పెண் குழந்தை",
            "কন্যা সন্তান", "मुलगी", "ಹೆಣ್ಣು ಮಗು",
        ],
        full_document_text=(
            "Sukanya Samriddhi Yojana (SSY) enables parents or legal guardians of a girl child below 10 years of age "
            "to open a high-interest (8.2% p.a.) tax-exempt savings account at any Post Office or authorized bank."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="has_girl_child_under_10",
                    operator=RuleOperator.BOOL_IS,
                    value=True,
                    description="Citizen must be a parent/legal guardian of a girl child aged below 10 years.",
                )
            ]
        ),
        documents=[
            _doc(
                "DOC-GIRL-BIRTH",
                "Girl Child's Birth Certificate",
                "Official birth certificate confirming the girl child is below 10 years of age.",
                "Municipal Corporation / Gram Panchayat Birth Registrar",
                ["SSY"],
                "बेटी का जन्म प्रमाण पत्र",
                "ఆడపిల్ల జనన ధృవీకరణ పత్రం",
                "பெண் குழந்தையின் பிறப்புச் சான்றிதழ்",
                "কন্যা সন্তানের জন্ম শংসাপত্র",
                "मुलीचा जन्म दाखला",
                "ಹೆಣ್ಣು ಮಗುವಿನ ಜನನ ಪ್ರಮಾಣಪತ್ರ",
            ),
            _with_scheme(DOC_AADHAAR, "SSY"),
            _with_scheme(DOC_PHOTO, "SSY"),
        ],
        application_steps=[
            "Visit any India Post Office or authorized Public/Private Bank branch.",
            "Fill out the Sukanya Samriddhi Account opening form with Parent/Guardian Aadhaar & PAN.",
            "Attach the girl child's Birth Certificate and make an initial deposit starting from Rs. 250.",
            "Deposit anytime up to Rs. 1.5 lakh/year and claim Section 80C tax exemption.",
        ],
        official_portal="https://www.indiapost.gov.in",
        helpline="1800-266-6868",
    ),

    # --------------------------------------------------------------------------
    # 17. MGNREGA (Rural Wage Employment Guarantee)
    # --------------------------------------------------------------------------
    SchemeDefinition(
        scheme_id="MGNREGA",
        official_name="Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)",
        short_code="MGNREGA",
        ministry="Ministry of Rural Development",
        benefit_summary="Legal guarantee of 100 days of paid unskilled manual wage employment per financial year to every rural household.",
        localized_summaries={
            "en": "Legal guarantee of 100 days/year of wage employment to adult rural households willing to do manual work.",
            "hi": "ग्रामीण परिवारों के वयस्क सदस्यों को प्रति वर्ष कम से कम 100 दिनों के गारंटीशुदा रोजगार का कानूनी अधिकार।",
            "te": "గ్రామీణ కుటుంబాలకు సంవత్సరానికి 100 రోజుల వేతన ఉపాధి హామీ చట్టం.",
            "ta": "கிராமப்புற குடும்பங்களுக்கு ஆண்டுக்கு 100 நாட்கள் உறுதிசெய்யப்பட்ட கூலி வேலைவாய்ப்பு.",
            "bn": "গ্রামীণ পরিবারকে বছরে ১০০ দিনের নিশ্চিত মজুরি কর্মসংস্থানের আইনি অধিকার।",
            "mr": "ग्रामीण कुटुंबांना वर्षातून 100 दिवसांच्या हमी रोजगाराचा कायदेशीर हक्क.",
            "kn": "ಗ್ರಾಮೀಣ ಕುಟುಂಬಗಳಿಗೆ ವರ್ಷಕ್ಕೆ 100 ದಿನಗಳ ಖಚಿತ ಕೂಲಿ ಉದ್ಯೋಗದ ಕಾನೂನುಬದ್ಧ ಹಕ್ಕು.",
        },
        target_tags=["rural", "employment", "wage", "laborer", "job card"],
        multilingual_keywords=[
            "rural", "employment", "wage", "laborer", "unemployed", "farmer", "artisan", "mgnrega", "job card",
            "ग्रामीण", "मजदूर", "बेरोजगार", "रोजगार", "గ్రామీణ", "కూలీ", "ఉపాధి", "கிராமம்", "வேலை", "গ্রাম", "কর্মসংস্থান", "ग्रामीण", "रोजगार", "ಗ್ರಾಮೀಣ", "ಕೂಲಿ",
        ],
        full_document_text=(
            "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA) legally guarantees 100 days of "
            "wage employment in a financial year to rural households whose adult members (age >= 18) volunteer for manual work "
            "(covering rural laborers, small farmers, unemployed youth, and rural artisans; excludes regular government employees)."
        ),
        rules=EligibilityRuleGroup(
            all_of=[
                RuleCondition(
                    field="residence_type",
                    operator=RuleOperator.EQ,
                    value="rural",
                    description="Household must reside in a rural Gram Panchayat area.",
                ),
                RuleCondition(
                    field="age",
                    operator=RuleOperator.GTE,
                    value=18,
                    description="Applicant must be an adult (>= 18 years).",
                ),
                RuleCondition(
                    field="occupation",
                    operator=RuleOperator.IN,
                    value=["daily_wage_laborer", "agricultural_worker", "unemployed", "farmer", "artisan"],
                    description="Adult rural member seeking or eligible for manual wage employment.",
                ),
                RuleCondition(
                    field="is_govt_employee",
                    operator=RuleOperator.BOOL_IS,
                    value=False,
                    description="Regular government employees are excluded.",
                ),
            ]
        ),
        documents=[
            _with_scheme(DOC_AADHAAR, "MGNREGA"),
            _with_scheme(DOC_BPL_RATION, "MGNREGA"),
            _with_scheme(DOC_BANK, "MGNREGA"),
            _with_scheme(DOC_PHOTO, "MGNREGA"),
        ],
        application_steps=[
            "Apply in person or verbally to your local Gram Panchayat for a MGNREGA Job Card.",
            "Submit Aadhaar, rural address/ration card proof, bank account details, and family photographs.",
            "Receive your free Job Card within 15 days and submit a written application demanding work.",
            "Wages are credited directly to your bank/post account within 15 days of work completion.",
        ],
        official_portal="https://nrega.nic.in",
        helpline="1800-11-0707",
    ),
]


# ==============================================================================
# Extended Multilingual Enrichments for Additional Languages (OCP Pattern)
# Covers Punjabi (pa), Gujarati (gu), Malayalam (ml), Odia (or), and Urdu (ur)
# without duplicating base definitions above.
# ==============================================================================

_EXTENDED_DOC_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "DOC-AADHAAR": {
        "pa": "ਆਧਾਰ ਕਾਰਡ (Aadhaar Card)",
        "gu": "આધાર કાર્ડ (Aadhaar Card)",
        "ml": "ആധാർ കാർഡ് (Aadhaar Card)",
        "or": "ଆଧାର କାର୍ଡ (Aadhaar Card)",
        "ur": "آدھار کارڈ (Aadhaar Card)",
    },
    "DOC-BANK": {
        "pa": "ਆਧਾਰ-ਲਿੰਕ ਬੈਂਕ ਪਾਸਬੁੱਕ",
        "gu": "આધાર-લિંક બેંક પાસબુક",
        "ml": "ആധാർ ലിങ്ക് ചെയ്ത ബാങ്ക് പാസ്ബുക്ക്",
        "or": "ଆଧାର ସଂଯୁକ୍ତ ବ୍ୟାଙ୍କ ପାସବୁକ୍",
        "ur": "آدھار سے منسلک بینک پاس بک",
    },
    "DOC-INCOME": {
        "pa": "ਪਰਿਵਾਰਕ ਸਾਲਾਨਾ ਆਮਦਨ ਸਰਟੀਫਿਕੇਟ",
        "gu": "કુટુંબનું વાર્ષિક આવકનું પ્રમાણપત્ર",
        "ml": "കുടുംബ വാർഷിക വരുമാന സർട്ടിഫിക്കറ്റ്",
        "or": "ବାର୍ଷିକ ପାରିବାରିକ ଆୟ ପ୍ରମାଣପତ୍ର",
        "ur": "خاندانی سالانہ آمدنی کا سرٹیفکیٹ",
    },
    "DOC-RATION-BPL": {
        "pa": "ਬੀਪੀਐਲ / ਰਾਸ਼ਨ ਕਾਰਡ",
        "gu": "બીપીએલ / રેશન કાર્ડ",
        "ml": "ബിപിഎൽ / റേഷൻ കാർഡ്",
        "or": "ବିପିଏଲ୍ / ରାସନ କାର୍ଡ",
        "ur": "بی پی ایل / راشن کارڈ",
    },
    "DOC-CASTE": {
        "pa": "ਜਾਤੀ / ਭਾਈਚਾਰਾ ਸਰਟੀਫਿਕੇਟ",
        "gu": "જાતિ / સમુદાયનું પ્રમાણપત્ર",
        "ml": "ജാതി സർട്ടിഫിക്കറ്റ്",
        "or": "ଜାତି ପ୍ରମାଣପତ୍ର",
        "ur": "ذات / برادری کا سرٹیفکیٹ",
    },
    "DOC-PHOTO": {
        "pa": "ਪਾਸਪੋਰਟ ਸਾਈਜ਼ ਫੋਟੋਆਂ (2 ਕਾਪੀਆਂ)",
        "gu": "પાસપોર્ટ સાઇઝના ફોટા (2 નકલ)",
        "ml": "പാസ്‌പോർട്ട് സൈസ് ഫോട്ടോകൾ (2 എണ്ണം)",
        "or": "ପାସପୋର୍ଟ ସାଇଜ୍ ଫଟୋ (୨ କପି)",
        "ur": "پاسپورٹ سائز تصاویر (2 کاپیاں)",
    },
    "DOC-LAND-ROR": {
        "pa": "ਖੇਤੀ ਵਾਲੀ ਜ਼ਮੀਨ ਦੀ ਫਰਦ / ਖਤੌਨੀ",
        "gu": "ખેતીની જમીનનો ૭/૧૨ ઉતારો",
        "ml": "കൃഷിഭൂമി ഉടമസ്ഥാവകാശ രേഖ (RoR)",
        "or": "ଚାଷ ଜମି ପଟ୍ଟା / ଖତିଆନ",
        "ur": "زرعی زمین کی ملکیت کا ریکارڈ (خاتونی/فرد)",
    },
    "DOC-SOWING": {
        "pa": "ਫਸਲ ਬਿਜਾਈ ਸਰਟੀਫਿਕੇਟ",
        "gu": "પાક વાવણી પ્રમાણપત્ર",
        "ml": "വിള വിതയ്ക്കൽ സർട്ടിഫിക്കറ്റ്",
        "or": "ଫସଲ ବୁଣା ପ୍ରମାଣପତ୍ର",
        "ur": "فصل بوائی کا سرٹیفکیٹ",
    },
    "DOC-NO-HOUSE-DECL": {
        "pa": "ਕੱਚੇ ਘਰ / ਬੇਘਰ ਹੋਣ ਦਾ ਸਵੈ-ਘੋਸ਼ਣਾ ਪੱਤਰ",
        "gu": "કાચા ઘર / ઘરવિહોણા હોવાનું ઘોષણાપત્ર",
        "ml": "പക്കാ വീടില്ലാത്തതിന്റെ സ്വയം പ്രഖ്യാപന രേഖ",
        "or": "କଚ୍ଚା ଘର / ଗୃହହୀନ ଘୋଷଣାପତ୍ର",
        "ur": "کچا گھر / بے گھر ہونے کا حلف نامہ",
    },
    "DOC-MCP-CARD": {
        "pa": "ਮਾਂ ਅਤੇ ਬਾਲ ਸੁਰੱਖਿਆ (MCP) ਕਾਰਡ",
        "gu": "માતા અને બાળ સુરક્ષા (MCP) કાર્ડ",
        "ml": "മാതൃ-ശിശു സംരക്ഷണ (MCP) കാർഡ്",
        "or": "ମାତୃ ଓ ଶିଶୁ ସୁରକ୍ଷା (MCP) କାର୍ଡ",
        "ur": "زچہ و بچہ حفاظتی (MCP) کارڈ",
    },
    "DOC-DEATH-CERT": {
        "pa": "ਪਤੀ ਦਾ ਮੌਤ ਸਰਟੀਫਿਕੇਟ",
        "gu": "પતિનું મૃત્યુ પ્રમાણપત્ર",
        "ml": "ഭർത്താവിന്റെ മരണ സർട്ടിഫിക്കറ്റ്",
        "or": "ସ୍ୱାମୀଙ୍କ ମୃତ୍ୟୁ ପ୍ରମାଣପତ୍ର",
        "ur": "شوہر کا ڈیتھ سرٹیفکیٹ",
    },
    "DOC-UDID": {
        "pa": "ਯੂਡੀਆਈਡੀ (UDID) / 80%+ ਅਪੰਗਤਾ ਸਰਟੀਫਿਕੇਟ",
        "gu": "UDID / 80%+ દિવ્યાંગતા પ્રમાણપત્ર",
        "ml": "യുഡിഐഡി (UDID) / 80%+ ഭിന്നശേഷി സർട്ടിഫിക്കറ്റ്",
        "or": "UDID / 80%+ ଭିନ୍ନକ୍ଷମ ପ୍ରମାଣପତ୍ର",
        "ur": "یو ڈی آئی ڈی (UDID) / 80%+ معذوری سرٹیفکیٹ",
    },
    "DOC-UDID-40": {
        "pa": "ਯੂਡੀਆਈਡੀ (UDID) / 40%+ ਅਪੰਗਤਾ ਸਰਟੀਫਿਕੇਟ",
        "gu": "UDID / 40%+ દિવ્યાંગતા પ્રમાણપત્ર",
        "ml": "യുഡിഐഡി (UDID) / 40%+ ഭിന്നശേഷി സർട്ടിഫിക്കറ്റ്",
        "or": "UDID / 40%+ ଭିନ୍ନକ୍ଷମ ପ୍ରମାଣପତ୍ର",
        "ur": "یو ڈی آئی ڈی (UDID) / 40%+ معذوری سرٹیفکیٹ",
    },
    "DOC-BONAFIDE": {
        "pa": "ਬੋਨਾਫਾਈਡ ਵਿਦਿਆਰਥੀ ਸਰਟੀਫਿਕੇਟ ਅਤੇ ਪਿਛਲੀ ਮਾਰਕਸ਼ੀਟ",
        "gu": "બોનાફાઇડ વિદ્યાર્થી પ્રમાણપત્ર અને માર્કશીટ",
        "ml": "ബോണഫൈഡ് വിദ്യാർത്ഥി സർട്ടിഫിക്കറ്റും മാർക്ക് ലിസ്റ്റും",
        "or": "ବୋନାଫାଇଡ୍ ଛାତ୍ର ପ୍ରମାଣପତ୍ର ଓ ମାର୍କସିଟ୍",
        "ur": "بونافائیڈ طالب علم سرٹیفکیٹ اور پچھلی مارک شیٹ",
    },
    "DOC-ADMISSION-MARKSHEET": {
        "pa": "ਕਾਲਜ ਦਾਖਲਾ ਪੱਤਰ ਅਤੇ ਯੋਗਤਾ ਪ੍ਰੀਖਿਆ ਮਾਰਕਸ਼ੀਟ",
        "gu": "કોલેજ પ્રવેશ પત્ર અને લાયકાત માર્કશીટ",
        "ml": "കോളേജ് പ്രവേശന രേഖയും മാർക്ക് ലിസ്റ്റും",
        "or": "କଲେଜ ନାମଲେଖା ପତ୍ର ଓ ମାର୍କସିଟ୍",
        "ur": "کالج داخلہ لیٹر اور اہلیت کی مارک شیٹ",
    },
    "DOC-VENDING-CERT": {
        "pa": "ਵਿਕਰੇਤਾ ਸਰਟੀਫਿਕੇਟ (CoV) / ਮਿਉਂਸਪਲ ਸਿਫ਼ਾਰਸ਼ ਪੱਤਰ",
        "gu": "ફેરિયા પ્રમાણપત્ર / મ્યુનિસિપਲ ભલામણ પત્ર",
        "ml": "വഴിയോര കച്ചവട സർട്ടിഫിക്കറ്റ് (CoV) / LoR",
        "or": "ବିକ୍ରେତା ପ୍ରମାଣପତ୍ର / ପୌର ସୁପାରିଶ ପତ୍ର",
        "ur": "فروخت کار سرٹیفکیٹ (CoV) / میونسپل سفارش نامہ",
    },
    "DOC-PAN-BIZ": {
        "pa": "ਪੈਨ (PAN) ਕਾਰਡ / ਛੋਟੇ ਕਾਰੋਬਾਰ ਦਾ ਪਤਾ ਸਬੂਤ",
        "gu": "પાન (PAN) કાર્ડ / નાના વ્યવસાયનું પ્રમાણ",
        "ml": "പാൻ (PAN) കാർഡ് / ബിസിനസ് രേഖ",
        "or": "ପ୍ୟାନ୍ (PAN) କାର୍ଡ / ବ୍ୟବସାୟ ପ୍ରମାଣ",
        "ur": "پین (PAN) کارڈ / کاروبار کا ثبوت",
    },
    "DOC-GIRL-BIRTH": {
        "pa": "ਬੇਟੀ ਦਾ ਜਨਮ ਸਰਟੀਫਿਕੇਟ",
        "gu": "દીકરીનું જન્મ પ્રમાણપત્ર",
        "ml": "പെൺകുട്ടിയുടെ ജനന സർട്ടിഫിക്കറ്റ്",
        "or": "ଝିଅର ଜନ୍ମ ପ୍ରମାଣପତ୍ର",
        "ur": "بچی کا پیدائشی سرٹیفکیٹ (Birth Certificate)",
    },
}

_EXTENDED_SCHEME_SUMMARIES: dict[str, dict[str, str]] = {
    "PM-KISAN": {
        "pa": "ਜ਼ਮੀਨ ਮਾਲਕ ਕਿਸਾਨ ਪਰਿਵਾਰਾਂ ਨੂੰ ਹਰ ਸਾਲ ₹6,000 ਦੀ ਸਿੱਧੀ ਆਰਥਿਕ ਸਹਾਇਤਾ (₹2,000 ਦੀਆਂ 3 ਕਿਸ਼ਤਾਂ ਵਿੱਚ)।",
        "gu": "જમીન ધરાવતા ખેડૂત પરિવારોને દર વર્ષે ₹6,000 ની સીધી આર્થਿਕ સહાય (₹2,000 ના 3 હપ્તામાં).",
        "ml": "കൃഷിഭൂമിയുള്ള കർഷക കുടുംബങ്ങൾക്ക് വർഷം ₹6,000 നേരിട്ടുള്ള വരുമാന സഹായം (₹2,000 വീതം 3 ഗഡുക്കളായി).",
        "or": "ଚାଷଜମି ଥିବା କୃଷକ ପରିବାରକୁ ବାର୍ଷିକ ₹6,000 ସିଧାସଳଖ ଆର୍ଥିକ ସହାୟତା (₹2,000 ର ୩ଟି କିସ୍ତିରେ)।",
        "ur": "زرعی زمین رکھنے والے کسان خاندانوں کو سالانہ ₹6,000 براہِ راست مالی امداد (₹2,000 کی 3 اقساط میں)۔",
    },
    "PMFBY": {
        "pa": "ਘੱਟ ਪ੍ਰੀਮੀਅਮ (1.5%–2%) 'ਤੇ ਫਸਲ ਬੀਮਾ ਜੋ ਸੋਕੇ, ਹੜ੍ਹ ਅਤੇ ਕੀੜਿਆਂ ਦੇ ਨੁਕਸਾਨ ਦੀ ਭਰਪਾਈ ਕਰਦਾ ਹੈ।",
        "gu": "ઓછા પ્રીમિયમ (1.5%–2%) સાથે પાક વીમો જે દુષ્કાળ, પૂર અને જીવાતના નુકસાન સામે રક્ષણ આપે છે.",
        "ml": "കുറഞ്ഞ പ്രീമിയത്തിൽ (1.5%–2%) വരൾച്ച, വെള്ളപ്പൊക്കം, വിളനാശം എന്നിവയ്ക്ക് സമഗ്ര വിള ഇൻഷുറൻസ്.",
        "or": "କମ୍ ପ୍ରିମିୟମ୍ (1.5%–2%) ରେ ଫସଲ ବୀମା ଯାହା ବନ୍ୟା, ମରୁଡ଼ି ଓ ଫସଲ କ୍ଷତିରୁ ସୁରକ୍ଷା ଦିଏ।",
        "ur": "کم پریمیم (1.5%–2%) پر فصل بیمہ جو خشک سالی، سیلاب اور فصل کے نقصان سے تحفظ فراہم کرتا ہے۔",
    },
    "PMAY-G": {
        "pa": "ਪੇਂਡੂ ਬੇਘਰ ਅਤੇ ਕੱਚੇ ਘਰਾਂ ਵਾਲੇ ਪਰਿਵਾਰਾਂ ਨੂੰ ਪੱਕਾ ਘਰ ਬਣਾਉਣ ਲਈ ₹1,20,000–₹1,30,000 ਦੀ ਵਿੱਤੀ ਸਹਾਇਤਾ।",
        "gu": "ગ્રામીણ બેઘર અને કાચા મકાન ધરાવતા પરિવારોને પાકું મકાન બાંધવા ₹1,20,000–₹1,30,000 ની સહાય.",
        "ml": "ഗ്രാമീണ ഭവനരഹിതർക്കും കുടിലിൽ താമസിക്കുന്നവർക്കും പക്കാ വീട് നിർമ്മിക്കാൻ ₹1,20,000–₹1,30,000 സഹായം.",
        "or": "ଗ୍ରାମୀଣ କଚ୍ଚା ଘର ଓ ଗୃହହୀନ ପରିବାରକୁ ପକ୍କା ଘର ନିର୍ମାଣ ପାଇଁ ₹1,20,000–₹1,30,000 ସହାୟତା।",
        "ur": "دیہی بے گھر اور کچے مکان والے خاندانوں کو پکا گھر بنانے کے لیے ₹1,20,000 تا ₹1,30,000 مالی امداد۔",
    },
    "AB-PMJAY": {
        "pa": "ਸੂਚੀਬੱਧ ਹਸਪਤਾਲਾਂ ਵਿੱਚ ਪ੍ਰਤੀ ਪਰਿਵਾਰ ਪ੍ਰਤੀ ਸਾਲ ₹5,00,000 ਤੱਕ ਮੁਫ਼ਤ ਅਤੇ ਨਕਦੀ ਰਹਿਤ ਇਲਾਜ।",
        "gu": "પેનલ હોસ્પિટલોમાં કુટુંબ દીઠ વાર્ષિક ₹5,00,000 સુધીની મફત અને કેશલેસ સારવાર.",
        "ml": "അംഗീകൃത ആശുപത്രികളിൽ കുടുംബത്തിന് വർഷം ₹5,00,000 വരെ പണരഹിത ചികിത്സാ കവറേജ്.",
        "or": "ତାଲିକାଭୁକ୍ତ ହସ୍ପିଟାଲରେ ପ୍ରତି ପରିବାରକୁ ବାର୍ଷିକ ₹5,00,000 ପର୍ଯ୍ୟନ୍ତ ମାଗଣା ନଗଦ-ରହିତ ଚିକିତ୍ସା।",
        "ur": "منتخب ہسپتالوں میں فی خاندان سالانہ ₹5,00,000 تک مفت اور کیش لیس علاج کی سہولت۔",
    },
    "PMUY": {
        "pa": "ਗਰੀਬ ਪਰਿਵਾਰਾਂ ਦੀਆਂ ਬਾਲਗ ਔਰਤਾਂ ਨੂੰ ਬਿਨਾਂ ਸਿਕਿਓਰਿਟੀ ਡਿਪਾਜ਼ਿਟ ਮੁਫ਼ਤ ਐਲਪੀਜੀ ਗੈਸ ਕਨੈਕਸ਼ਨ ਅਤੇ ₹1,600 ਸਹਾਇਤਾ।",
        "gu": "ગરીબ પરિવારની પુખ્ત મહિલાઓને ડિપોઝિટ વગર મફત LPG ગેસ કનેક્શન અને ₹1,600 ની સહાય.",
        "ml": "ദരിദ്ര കുടുംബങ്ങളിലെ പ്രായപൂർത്തിയായ സ്ത്രീകൾക്ക് ഡെപ്പോസിറ്റ് രഹിത സൗജന്യ എൽപിജി കണക്ഷനും ₹1,600 സഹായവും.",
        "or": "ଦରିଦ୍ର ପରିବାରର ବୟସ୍କା ମହିଳାଙ୍କୁ ବିନା ଡିପୋଜିଟ୍ରେ ମାଗଣା LPG ଗ୍ୟାସ୍ ସଂଯୋଗ ଓ ₹1,600 ସହାୟତା।",
        "ur": "غریب خاندانوں کی بالغ خواتین کو بغیر سیکیورٹی ڈپازٹ مفت ایل پی جی گیس کنکشن اور ₹1,600 امداد۔",
    },
    "PMMVY": {
        "pa": "ਗਰਭਵਤੀ ਔਰਤਾਂ ਅਤੇ ਦੁੱਧ ਪਿਲਾਉਣ ਵਾਲੀਆਂ ਮਾਵਾਂ ਨੂੰ ਪੋਸ਼ਣ ਅਤੇ ਸਿਹਤ ਲਈ ₹5,000 (ਦੂਜੀ ਬੇਟੀ 'ਤੇ ₹6,000) ਦੀ ਸਹਾਇਤਾ।",
        "gu": "ગર્ભવતી મહિલાઓ અને સ્તનપાન કરાવતી માતાઓને પોષણ માટે ₹5,000 (બીજી દીકરી પર ₹6,000) ની સહાય.",
        "ml": "ഗർഭിണികൾക്കും മുലയൂട്ടുന്ന അമ്മമാർക്കും പോഷകാഹാര സഹായമായി ₹5,000 (രണ്ടാമത്തെ പെൺകുഞ്ഞിന് ₹6,000).",
        "or": "ଗର୍ଭବତୀ ମହିଳା ଓ ସ୍ତନ୍ୟପାନ କରାଉଥିବା ମାଆଙ୍କୁ ପୋଷଣ ପାଇଁ ₹5,000 (ଦ୍ୱିତୀୟ କନ୍ୟା ସନ୍ତାନ ପାଇଁ ₹6,000)।",
        "ur": "حاملہ اور دودھ پلانے والی ماؤں کو غذائیت کے لیے ₹5,000 (دوسری بیٹی پر ₹6,000) کی نقد امداد۔",
    },
    "IGNOAPS": {
        "pa": "60 ਸਾਲ ਤੋਂ ਵੱਧ ਉਮਰ ਦੇ ਬੀਪੀਐਲ ਬਜ਼ੁਰਗ ਨਾਗਰਿਕਾਂ ਲਈ ਗਾਰੰਟੀਸ਼ੁਦਾ ਮਾਸਿਕ ਬੁਢਾਪਾ ਪੈਨਸ਼ਨ।",
        "gu": "60 વર્ષથી વધુ ઉંમરના બીપીએਲ વરિષ્ઠ નાગરિકો માટે ખાતરીપૂર્વક માસિક વૃદ્ધાવસ્થા પેન્શન.",
        "ml": "60 വയസ്സിനു മുകളിലുള്ള ബിപിഎൽ മുതിർന്ന പൗരന്മാർക്ക് പ്രതിമാസ വാർദ്ധക്യകാല പെൻഷൻ.",
        "or": "୬୦ ବର୍ଷରୁ ଅଧିକ BPL ବରିଷ୍ଠ ନାଗରିକଙ୍କ ପାଇଁ ମାସିକ ବାର୍ଦ୍ଧକ୍ୟ ଭତ୍ତା।",
        "ur": "60 سال یا اس سے زائد عمر کے بی پی ایل بزرگ شہریوں کے لیے ماہانہ بڑھاپا پنشن۔",
    },
    "IGNWPS": {
        "pa": "40–79 ਸਾਲ ਦੀ ਉਮਰ ਦੀਆਂ ਬੀਪੀਐਲ ਵਿਧਵਾ ਔਰਤਾਂ ਲਈ ਮਾਸਿਕ ਸਮਾਜਿਕ ਸੁਰੱਖਿਆ ਪੈਨਸ਼ਨ।",
        "gu": "40–79 વર્ષની બીપીએਲ વિધવા મહિલાઓ માટે માસિક સામાજિક સુરક્ષા પેન્શન.",
        "ml": "40–79 വയസ്സുള്ള ബിപിഎൽ വിധവകളായ സ്ത്രീകൾക്ക് പ്രതിമാസ സാമൂഹിക സുരക്ഷാ പെൻഷൻ.",
        "or": "୪୦–୭୯ ବର୍ଷ ବୟସର BPL ବିଧବା ମହିଳାଙ୍କ ପାଇଁ ମାସିକ ବିଧବା ଭତ୍ତା।",
        "ur": "40 سے 79 سال عمر کی بی پی ایل بیوہ خواتین کے لیے ماہانہ سماجی تحفظ پنشن۔",
    },
    "IGNDPS": {
        "pa": "80%+ ਗੰਭੀਰ ਅਪੰਗਤਾ ਵਾਲੇ ਬੀਪੀਐਲ ਨਾਗਰਿਕਾਂ (ਉਮਰ 18+) ਲਈ ਮਾਸਿਕ ਅਪੰਗਤਾ ਪੈਨਸ਼ਨ।",
        "gu": "80%+ ગંભીર દિવ્યાંગતા ધરાવતા બીપીએલ નાગરિકો (ઉંમર 18+) માટે માસિક પેન્શન.",
        "ml": "80%+ തീവ്ര ഭിന്നശേഷിയുള്ള ബിപിഎൽ പൗരന്മാർക്ക് (18+) പ്രതിമാസ പെൻഷൻ.",
        "or": "80%+ ଗୁରୁତର ଭିନ୍ନକ୍ଷମ BPL ନାଗରିକ (୧୮+) ଙ୍କ ପାଇଁ ମାସିକ ଭତ୍ତା।",
        "ur": "80%+ شدید معذوری کے شکار بی پی ایل شہریوں (عمر 18+) کے لیے ماہانہ معذوری پنشن۔",
    },
    "ADIP-DIVYANG": {
        "pa": "40%+ ਅਪੰਗਤਾ ਵਾਲੇ ਨਾਗਰਿਕਾਂ ਨੂੰ ₹30,000+ ਤੱਕ ਮੁਫ਼ਤ/ਸਬਸਿਡੀ ਵਾਲੇ ਵ੍ਹੀਲਚੇਅਰ, ਟਰਾਈਸਾਈਕਲ ਅਤੇ ਸਹਾਇਕ ਉਪਕਰਣ।",
        "gu": "40%+ દિવ્યાંગ નાગરિકોને મફત કે સબસિડી દરે વ્હીલચેર, ટ્રાઇસિકલ અને સહાયક સાધનો.",
        "ml": "40%+ ഭിന്നശേഷിയുള്ള പൗരന്മാർക്ക് സൗജന്യ/സബ്സിഡി നിരക്കിൽ വീൽചെയറുകളും സഹായ ഉപകരണങ്ങളും.",
        "or": "40%+ ଭିନ୍ନକ୍ଷମ ନାଗରିକଙ୍କୁ ମାଗଣା ବା ରିହାତି ଦରରେ ହ୍ୱିଲଚେୟାର ଓ ସହାୟକ ଉପକରଣ।",
        "ur": "40%+ معذور شہریوں کو مفت یا رعایتی وہیل چیئر، ٹرائی سائیکل اور معاون آلات۔",
    },
    "NSP-PMS": {
        "pa": "SC/ST/OBC/EBC/ਘੱਟ ਗਿਣਤੀ ਕਾਲਜ ਵਿਦਿਆਰਥੀਆਂ ਨੂੰ ਪੂਰੀ ਟਿਊਸ਼ਨ ਫੀਸ ਵਾਪਸੀ ਅਤੇ ਮਾਸਿਕ ਵਜ਼ੀਫ਼ਾ।",
        "gu": "SC/ST/OBC/EBC/લઘુમતી કોલેજ વિદ્યાર્થીઓને સંપૂર્ણ ફી ભરપાઈ અને માસિક શિષ્યવૃત્તિ.",
        "ml": "SC/ST/OBC/EBC/ന്യൂനപക്ഷ കോളേജ് വിദ്യാർത്ഥികൾക്ക് ഫീസ് റീഇംബേഴ്സ്മെന്റും പ്രതിമാസ സ്കോളർഷിപ്പും.",
        "or": "SC/ST/OBC/EBC/ସଂଖ୍ୟାଲଘୁ କଲେଜ ଛାତ୍ରଛାତ୍ରୀଙ୍କୁ ସମ୍ପୂର୍ଣ୍ଣ ଫି ଛାଡ଼ ଓ ମାସିକ ବୃତ୍ତି।",
        "ur": "SC/ST/OBC/EBC/اقلیتی کالج طلبہ کو مکمل ٹیوشن فیس کی واپسی اور ماہانہ وظیفہ۔",
    },
    "PM-YASASVI": {
        "pa": "OBC/EBC/DNT ਵਿਦਿਆਰਥੀਆਂ ਨੂੰ ₹75,000 ਤੋਂ ₹1,25,000/ਸਾਲ ਤੱਕ ਮੈਰਿਟ-ਕਮ-ਮੀਨਜ਼ ਵਜ਼ੀਫ਼ਾ।",
        "gu": "OBC/EBC/DNT વિદ્યાર્થીઓને વાર્ષિક ₹75,000 થી ₹1,25,000 સુધીની મેરિટ શિષ્યવૃત્તિ.",
        "ml": "OBC/EBC/DNT വിദ്യാർത്ഥികൾക്ക് വർഷം ₹75,000 മുതൽ ₹1,25,000 വരെ മെറിറ്റ് സ്കോളർഷിപ്പ്.",
        "or": "OBC/EBC/DNT ଛାତ୍ରଛାତ୍ରୀଙ୍କୁ ବାର୍ଷିକ ₹75,000 ରୁ ₹1,25,000 ପର୍ଯ୍ୟନ୍ତ ମେଧା ବୃତ୍ତି।",
        "ur": "OBC/EBC/DNT طلبہ کے لیے سالانہ ₹75,000 تا ₹1,25,000 میرٹ اسکالرشپ۔",
    },
    "PM-SVANIDHI": {
        "pa": "ਸ਼ਹਿਰੀ ਰੇਹੜੀ-ਫੜ੍ਹੀ ਵਾਲਿਆਂ ਨੂੰ ਬਿਨਾਂ ਗਾਰੰਟੀ ₹10,000 (ਅੱਗੇ ₹20k/₹50k) ਕਾਰਜਸ਼ੀਲ ਪੂੰਜੀ ਕਰਜ਼ਾ ਅਤੇ 7% ਵਿਆਜ ਸਬਸਿਡੀ।",
        "gu": "શહેરી ફેરિયાઓને ગેરંટી વગર ₹10,000 થી ₹50,000 સુધીની લોન અને 7% વ્યાજ સબસિડી.",
        "ml": "നഗര വഴിയോര കച്ചവടക്കാർക്ക് ഈടില്ലാതെ ₹10,000 മുതൽ ₹50,000 വരെ വായ്പയും 7% പലിശ സബ്സിഡിയും.",
        "or": "ସହରୀ ରାସ୍ତା କଡ଼ ବିକାଳିଙ୍କୁ ବିନା ବନ୍ଧକରେ ₹10,000 ରୁ ₹50,000 ଋଣ ଓ 7% ସୁଧ ରିହାତି।",
        "ur": "شہری ریڑھی پھیری والوں کو بغیر ضمانت ₹10,000 تا ₹50,000 قرض اور 7% سود پر سبسڈی۔",
    },
    "PM-VISHWAKARMA": {
        "pa": "ਰਵਾਇਤੀ ਕਾਰੀਗਰਾਂ ਨੂੰ ₹500/ਦਿਨ ਸਿਖਲਾਈ, ₹15,000 ਟੂਲਕਿੱਟ ਵਾਊਚਰ ਅਤੇ 5% ਵਿਆਜ 'ਤੇ ₹3 ਲੱਖ ਤੱਕ ਕਰਜ਼ਾ।",
        "gu": "પરંપરાગત કારીગરોને ₹500/દિવસ તાલીમ ભથ્થું, ₹15,000 ટૂલકિટ અને 5% વ્યાજે ₹3 લાખ સુધીની લોન.",
        "ml": "പരമ്പരാഗത കൈത്തൊഴിലാളികൾക്ക് ₹500/ദിവസം പരിശീലനവും ₹15,000 ടൂൾകിറ്റും 5% പലിശയിൽ ₹3 ലക്ഷം വായ്പയും.",
        "or": "ପାରମ୍ପରିକ କାରୀଗରଙ୍କୁ ₹500/ଦିନ ପ୍ରଶିକ୍ଷଣ, ₹15,000 ଟୁଲକିଟ୍ ଓ 5% ସୁଧରେ ₹3 ଲକ୍ଷ ଋଣ।",
        "ur": "روایتی کاریگروں کو ₹500 یومیہ تربیتی وظیفہ، ₹15,000 ٹول کٹ واؤچر اور 5% سود پر ₹3 لاکھ قرض۔",
    },
    "PMMY": {
        "pa": "ਛੋਟੇ ਕਾਰੋਬਾਰੀਆਂ ਅਤੇ ਸੂਖਮ ਉਦਮੀਆਂ ਨੂੰ ਬਿਨਾਂ ਗਾਰੰਟੀ ₹10,00,000 ਤੱਕ ਮੁਦਰਾ ਕਾਰੋਬਾਰੀ ਕਰਜ਼ਾ।",
        "gu": "નાના ઉદ્યોગો અને દુકાનદારોને ગેરંટી વગર ₹10,00,000 સુધીની મુદ્રા બિઝનેસ લોન.",
        "ml": "ചെറുകിട വ്യവസായികൾക്കും സംരംഭകർക്കും ഈടില്ലാതെ ₹10,00,000 വരെ മുദ്ര ബിസിനസ് വായ്പ.",
        "or": "କ୍ଷୁଦ୍ର ବ୍ୟବସାୟୀ ଓ ଉଦ୍ୟୋଗୀଙ୍କୁ ବିନା ବନ୍ଧକରେ ₹10,00,000 ପର୍ଯ୍ୟନ୍ତ ମୁଦ୍ରା ବ୍ୟବସାୟ ଋଣ।",
        "ur": "چھوٹے کاروباریوں اور دکانداروں کو بغیر ضمانت ₹10,00,000 تک مدرا بزنس لون۔",
    },
    "SSY": {
        "pa": "10 ਸਾਲ ਤੋਂ ਘੱਟ ਉਮਰ ਦੀ ਬੇਟੀ ਦੀ ਸਿੱਖਿਆ ਅਤੇ ਭਵਿੱਖ ਲਈ 8.2% ਵਿਆਜ ਅਤੇ ਟੈਕਸ ਛੋਟ ਵਾਲੀ ਸਰਕਾਰੀ ਬੱਚਤ ਯੋਜਨਾ।",
        "gu": "10 વર્ષથી નાની દીકરીના શિક્ષણ અને ભવિષ્ય માટે 8.2% વ્યાજ અને કરમુક્ત બચત યોજના.",
        "ml": "10 വയസ്സിൽ താഴെയുള്ള പെൺകുട്ടികളുടെ ഭാവിക്കായി 8.2% പലിശയും നികുതി ഇളവുമുള്ള സമ്പാദ്യ പദ്ധതി.",
        "or": "୧୦ ବର୍ଷରୁ କମ୍ ବୟସର ଝିଅର ଶିକ୍ଷା ଓ ଭବିଷ୍ୟତ ପାଇଁ 8.2% ସୁଧ ଓ ଟିକସ ଛାଡ଼ ସଞ୍ଚୟ ଯୋଜਨਾ।",
        "ur": "10 سال سے کم عمر بیٹی کی تعلیم و مستقبل کے لیے 8.2% منافع اور ٹیکس سے مستثنیٰ سرکاری بچت اسکیم۔",
    },
    "MGNREGA": {
        "pa": "ਹਰ ਪੇਂਡੂ ਪਰਿਵਾਰ ਨੂੰ ਇੱਕ ਵਿੱਤੀ ਸਾਲ ਵਿੱਚ ਘੱਟੋ-ਘੱਟ 100 ਦਿਨਾਂ ਦੇ ਤਨਖਾਹ ਵਾਲੇ ਰੁਜ਼ਗਾਰ ਦੀ ਕਾਨੂੰਨੀ ਗਾਰੰਟੀ।",
        "gu": "દરેક ગ્રામીણ પરિવારને નાણાકીય વર્ષમાં 100 દિવસની વેતન રોજગારીની કાયદેસર ખાતરી.",
        "ml": "ഓരോ ഗ്രാമീണ കുടുംബത്തിനും വർഷത്തിൽ 100 ദിവസത്തെ വേതന തൊഴിലിന് നിയമപരമായ ഉറപ്പ്.",
        "or": "ପ୍ରତି ଗ୍ରାମୀଣ ପରିବାରକୁ ବର୍ଷକୁ ୧୦୦ ଦିନର ମଜୁରି ଭିତ୍ତିକ କର୍ମନିଯୁକ୍ତିର ଆଇନଗତ ଗ୍ୟାରେଣ୍ଟି।",
        "ur": "ہر دیہی خاندان کو مالی سال میں 100 دن کے اجرتی روزگار کی قانونی ضمانت۔",
    },
}

_EXTENDED_SCHEME_KEYWORDS: dict[str, list[str]] = {
    "PM-KISAN": ["ਕਿਸਾਨ", "ਖੇਤੀ", "ਜ਼ਮੀਨ", "ખેડૂત", "જમીન", "കർഷകൻ", "കൃഷിഭൂമി", "ଚାଷୀ", "ଜମି", "کسان", "زمین"],
    "PMFBY": ["ਫਸਲ ਬੀਮਾ", "પાક વીમો", "വിള ഇൻഷുറൻസ്", "ଫସଲ ବୀମା", "فصل بیمہ"],
    "PMAY-G": ["ਪੱਕਾ ਘਰ", "ਕੱਚਾ ਘਰ", "પાકું ઘર", "કાચું ઘર", "വീട്", "ପକ୍କା ଘର", "پکا گھر", "کچا گھر"],
    "AB-PMJAY": ["ਸਿਹਤ", "ਹਸਪਤਾਲ", "આરોગ્ય", "ആരോഗ്യ", "ସ୍ୱାସ୍ଥ୍ୟ", "صحت", "ہسپتال"],
    "PMUY": ["ਗੈਸ ਕਨੈਕਸ਼ਨ", "ਐਲਪੀਜੀ", "ગેસ", "ഗ്യാസ്", "ଗ୍ୟାସ୍", "گیس کنکشن"],
    "PMMVY": ["ਗਰਭਵਤੀ", "ગર્ભવતી", "ഗർഭിണി", "ଗର୍ଭବତୀ", "حاملہ"],
    "IGNOAPS": ["ਬੁਢਾਪਾ ਪੈਨਸ਼ਨ", "ਬਜ਼ੁਰਗ", "વૃદ્ધ પેન્શન", "വാർദ്ധക്യ പെൻഷൻ", "ବାର୍ଦ୍ଧକ୍ୟ ଭତ୍ତା", "بڑھاپا پنشن"],
    "IGNWPS": ["ਵਿਧਵਾ ਪੈਨਸ਼ਨ", "વિધવા પેન્શન", "വിധവ പെൻഷൻ", "ବିଧବା ଭତ୍ତା", "بیوہ پنشن"],
    "IGNDPS": ["ਅਪੰਗਤਾ ਪੈਨਸ਼ਨ", "દિવ્યાંગ પેન્શન", "ഭിന്നശേഷി പെൻഷൻ", "ଭିନ୍ନକ୍ଷମ ଭତ୍ତା", "معذوری پنشن"],
    "ADIP-DIVYANG": ["ਵ੍ਹੀਲਚੇਅਰ", "ਦਿਵਿਆਂਗ", "વ્હીલચેર", "വീൽചെയർ", "ହ୍ୱିଲଚେୟାର", "معذور"],
    "NSP-PMS": ["ਵਜ਼ੀਫ਼ਾ", "ਵਿਦਿਆਰਥੀ", "શિષ્યવૃત્તિ", "സ്കോളർഷിപ്പ്", "ବୃତ୍ତି", "وظیفہ", "طالب علم"],
    "PM-YASASVI": ["ਮੈਰਿਟ ਵਜ਼ੀਫ਼ਾ", "મેરિટ શિષ્યવૃત્તિ", "മെറിറ്റ് സ്കോളർഷിപ്പ്", "ମେଧା ବୃତ୍ତି", "اسکالرشپ"],
    "PM-SVANIDHI": ["ਰੇਹੜੀ", "ਫੜ੍ਹੀ", "ફેરિયો", "വഴിയോര കച്ചവടം", "ବିକାଳି", "ریڑھی"],
    "PM-VISHWAKARMA": ["ਕਾਰੀਗਰ", "ਘੁਮਿਆਰ", "ਤਰਖਾਣ", "કારીગર", "കൈത്തൊഴിലാളി", "କାରୀଗର", "کاریگر"],
    "PMMY": ["ਕਾਰੋਬਾਰ ਕਰਜ਼ਾ", "ਦੁਕਾਨਦਾਰ", "વ્યવસાય લોન", "ബിസിനസ് വായ്പ", "ବ୍ୟବସାୟ ଋଣ", "کاروباری قرض"],
    "SSY": ["ਬੇਟੀ", "ਧੀ", "દીકરી", "പെൺകുട്ടി", "ଝିଅ", "بیٹی"],
    "MGNREGA": ["ਪੇਂਡੂ ਰੁਜ਼ਗਾਰ", "ਮਜ਼ਦੂਰ", "ગ્રામીણ રોજગાર", "ഗ്രാമീണ തൊഴിൽ", "ଗ୍ରାମୀଣ ନିଯୁକ୍ତି", "مزدور"],
}


def _apply_extended_localizations() -> None:
    """
    Open/Closed enrichment pass merging pa, gu, ml, or, and ur localizations into
    shared documents and canonical schemes at module initialization.
    """
    shared_docs = [DOC_AADHAAR, DOC_BANK, DOC_INCOME, DOC_BPL_RATION, DOC_CASTE, DOC_PHOTO]
    for doc in shared_docs:
        if doc.doc_id in _EXTENDED_DOC_LOCALIZATIONS:
            doc.localized_names.update(_EXTENDED_DOC_LOCALIZATIONS[doc.doc_id])

    for scheme in SCHEMES_CATALOG:
        if scheme.scheme_id in _EXTENDED_SCHEME_SUMMARIES:
            scheme.localized_summaries.update(_EXTENDED_SCHEME_SUMMARIES[scheme.scheme_id])
        if scheme.scheme_id in _EXTENDED_SCHEME_KEYWORDS:
            existing = set(scheme.multilingual_keywords)
            for kw in _EXTENDED_SCHEME_KEYWORDS[scheme.scheme_id]:
                if kw not in existing:
                    scheme.multilingual_keywords.append(kw)
        for doc in scheme.documents:
            if doc.doc_id in _EXTENDED_DOC_LOCALIZATIONS:
                doc.localized_names.update(_EXTENDED_DOC_LOCALIZATIONS[doc.doc_id])


_apply_extended_localizations()


def get_scheme_by_id(scheme_id: str) -> SchemeDefinition | None:
    """Lookup helper returning SchemeDefinition matching scheme_id or None."""
    for scheme in SCHEMES_CATALOG:
        if scheme.scheme_id == scheme_id:
            return scheme
    return None

