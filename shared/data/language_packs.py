"""
Multilingual Language Packs, Script Detectors, Digit Normalizers, and Natural-Language
Citizen Profile Extractors covering 12 languages:
  English (en), Hindi (hi), Punjabi (pa), Telugu (te), Tamil (ta), Bengali (bn),
  Marathi (mr), Kannada (kn), Gujarati (gu), Malayalam (ml), Odia (or), Urdu (ur).
"""

import re
from typing import Any

from shared.domain.enums import LanguageCode
from shared.domain.models import CitizenProfile

# Mapping of native Indic & Urdu Unicode numerals to standard ASCII digits for uniform regex parsing
_INDIC_DIGIT_TRANSLATION = str.maketrans(
    "०१२३४५६७८९"  # Devanagari (Hindi / Marathi)
    "੦੧੨੩੪੫੬੭੮੯"  # Gurmukhi (Punjabi)
    "౦౧౨౩౪౫౬౭౮౯"  # Telugu
    "௦௧௨௩௪௫௬௭௮௯"  # Tamil
    "০১২৩৪৫৬৭৮৯"  # Bengali
    "೦೧೨೩೪೫೬೭೮೯"  # Kannada
    "૦૧૨૩૪૫૬૭૮૯"  # Gujarati
    "൦൧൨൩൪൫൬൭൮൯"  # Malayalam
    "୦୧୨୩୪୫୬୭୮୯"  # Odia
    "۰۱۲۳۴۵۶۷۸۹"  # Extended Arabic-Indic (Urdu)
    "٠١٢٣٤٥٦٧٨٩",  # Arabic-Indic fallback
    "0123456789" * 11,
)


def normalize_digits(text: str) -> str:
    """Convert any Indic-script numerals inside text into ASCII 0-9 digits."""
    return text.translate(_INDIC_DIGIT_TRANSLATION)


# Localized headings, prose connectors, and reviewer labels keyed by ISO language code
LANGUAGE_TEMPLATES: dict[str, dict[str, str]] = {
    "en": {
        "language_name": "English",
        "greeting": "Hello! Based on your citizen profile and official scheme documents, here is your verified welfare guide:",
        "eligible_heading": "Eligible Government Welfare Schemes",
        "potential_heading": "Schemes Needing One More Confirmation",
        "no_schemes": "Based on the details provided, you do not currently meet the statutory eligibility criteria for the tracked welfare schemes.",
        "reason_label": "Why you qualify",
        "benefit_label": "Benefit",
        "docs_heading": "Document Checklist (Consolidated)",
        "steps_heading": "Step-by-Step Application Guide",
        "portal_label": "Official Portal",
        "helpline_label": "Helpline",
        "missing_fields_note": "To check additional schemes accurately, please confirm",
        "grounding_note": "All recommended schemes and criteria are verified against official scheme documents.",
        "reason_prefix": "Satisfied criteria",
        "where_label": "Where to get",
        "step_prefix": "Step",
    },
    "hi": {
        "language_name": "हिन्दी (Hindi)",
        "greeting": "नमस्ते! आपकी प्रोफ़ाइल और आधिकारिक सरकारी योजना दस्तावेज़ों के आधार पर आपकी पात्रता मार्गदर्शिका नीचे दी गई है:",
        "eligible_heading": "पात्र सरकारी कल्याणकारी योजनाएं",
        "potential_heading": "अतिरिक्त पुष्टि के बाद संभावित योजनाएं",
        "no_schemes": "दी गई जानकारी के आधार पर, आप वर्तमान में उपलब्ध कल्याणकारी योजनाओं के पात्रता मानदंडों को पूरा नहीं करते हैं।",
        "reason_label": "पात्रता का कारण",
        "benefit_label": "लाभ",
        "docs_heading": "आवश्यक दस्तावेज़ों की सूची",
        "steps_heading": "आवेदन करने की चरण-दर-चरण प्रक्रिया",
        "portal_label": "आधिकारिक पोर्टल",
        "helpline_label": "हेल्पलाइन",
        "missing_fields_note": "अतिरिक्त योजनाओं की जांच के लिए कृपया पुष्टि करें",
        "grounding_note": "सभी योजनाएं और नियम आधिकारिक सरकारी दस्तावेज़ों से सत्यापित हैं।",
        "reason_prefix": "पूर्ण मानदंड",
        "where_label": "कहां से प्राप्त करें",
        "step_prefix": "चरण",
    },
    "te": {
        "language_name": "తెలుగు (Telugu)",
        "greeting": "నమస్కారం! మీ ప్రొఫైల్ మరియు అధికారిక ప్రభుత్వ పథకాల పత్రాల ఆధారంగా మీ అర్హత మార్గదర్శిని ఇక్కడ ఉంది:",
        "eligible_heading": "మీకు అర్హత ఉన్న ప్రభుత్వ సంక్షేమ పథకాలు",
        "potential_heading": "మరింత నిర్ధారణ అవసరమైన పథకాలు",
        "no_schemes": "మీరు అందించిన వివరాల ప్రకారం, ప్రస్తుతం ఏ సంక్షేమ పథకానికి అర్హత ప్రమాణాలు సరిపోలలేదు.",
        "reason_label": "అర్హత కారణం",
        "benefit_label": "ప్రయోజనం",
        "docs_heading": "అవసరమైన పత్రాల జాబితా",
        "steps_heading": "దరఖాస్తు విధానం (దశలవారీగా)",
        "portal_label": "అధికారిక పోర్టల్",
        "helpline_label": "హెల్ప్‌లైన్",
        "missing_fields_note": "మరిన్ని పథకాలను తనిఖీ చేయడానికి దయచేసి నిర్ధారించండి",
        "grounding_note": "అన్ని పథకాలు మరియు నియమాలు అధికారిక పత్రాల ద్వారా ధృవీకరించబడ్డాయి.",
        "reason_prefix": "సరిపోయిన ప్రమాణాలు",
        "where_label": "ఎక్కడ పొందాలి",
        "step_prefix": "దశ",
    },
    "ta": {
        "language_name": "தமிழ் (Tamil)",
        "greeting": "வணக்கம்! உங்கள் விவரங்கள் மற்றும் அதிகாரப்பூர்வ அரசுத் திட்ட ஆவணங்களின் அடிப்படையில் உங்கள் தகுதி வழிகாட்டி:",
        "eligible_heading": "தகுதியுள்ள அரசு நலத்திட்டங்கள்",
        "potential_heading": "மேலும் உறுதிப்படுத்தல் தேவைப்படும் திட்டங்கள்",
        "no_schemes": "வழங்கப்பட்ட விவரங்களின் அடிப்படையில், தற்போது எந்த நலத்திட்டத்திற்கும் தகுதி வரம்புகள் பொருந்தவில்லை.",
        "reason_label": "தகுதிக்கான காரணம்",
        "benefit_label": "பயன்",
        "docs_heading": "தேவையான ஆவணங்களின் பட்டியல்",
        "steps_heading": "விண்ணப்பிக்கும் படிப்படியான முறை",
        "portal_label": "அதிகாரப்பூர்வ இணையதளம்",
        "helpline_label": "உதவி எண்",
        "missing_fields_note": "கூடுதல் திட்டங்களைச் சரிபார்க்க உறுதிப்படுத்தவும்",
        "grounding_note": "அனைத்து திட்டங்களும் அதிகாரப்பூர்வ ஆவணங்களின் அடிப்படையில் சரிபார்க்கப்பட்டவை.",
        "reason_prefix": "பூர்த்தி செய்யப்பட்ட விதிகள்",
        "where_label": "எங்கே பெறுவது",
        "step_prefix": "படி",
    },
    "bn": {
        "language_name": "বাংলা (Bengali)",
        "greeting": "নমস্কার! আপনার প্রোফাইল এবং সরকারি প্রকল্পের নথির ভিত্তিতে আপনার যোগ্যতা নির্দেশিকা নিচে দেওয়া হলো:",
        "eligible_heading": "যোগ্য সরকারি কল্যাণ প্রকল্পসমূহ",
        "potential_heading": "অতিরিক্ত নিশ্চিতকরণের প্রয়োজন এমন প্রকল্প",
        "no_schemes": "প্রদত্ত তথ্যের ভিত্তিতে, আপনি বর্তমানে এই সরকারি প্রকল্পগুলোর যোগ্যতার শর্ত পূরণ করছেন না।",
        "reason_label": "যোগ্যতার কারণ",
        "benefit_label": "সুবিধা",
        "docs_heading": "প্রয়োজনীয় নথিপত্রের তালিকা",
        "steps_heading": "আবেদনের ধাপে ধাপে নিয়ম",
        "portal_label": "অফিশিয়াল পোর্টাল",
        "helpline_label": "হেল্পলাইন",
        "missing_fields_note": "আরও প্রকল্প যাচাই করতে অনুগ্রহ করে নিশ্চিত করুন",
        "grounding_note": "সমস্ত প্রকল্প এবং নিয়ম সরকারি নথি দ্বারা যাচাইকৃত।",
        "reason_prefix": "পূরণকৃত শর্তাবলি",
        "where_label": "কোথায় পাবেন",
        "step_prefix": "ধাপ",
    },
    "mr": {
        "language_name": "मराठी (Marathi)",
        "greeting": "नमस्कार! तुमच्या माहितीच्या आणि अधिकृत सरकारी योजना दस्तऐवजांच्या आधारे तुमची पात्रता मार्गदर्शिका खालीलप्रमाणे आहे:",
        "eligible_heading": "पात्र सरकारी कल्याणकारी योजना",
        "potential_heading": "अतिरिक्त खात्री आवश्यक असलेल्या योजना",
        "no_schemes": "दिलेल्या माहितीच्या आधारे, तुम्ही सध्या उपलब्ध योजनांच्या पात्रता अटी पूर्ण करत नाही.",
        "reason_label": "पात्रतेचे कारण",
        "benefit_label": "लाभ",
        "docs_heading": "आवश्यक कागदपत्रांची यादी",
        "steps_heading": "अर्ज करण्याची टप्प्याटप्प्याने प्रक्रिया",
        "portal_label": "अधिकृत पोर्टल",
        "helpline_label": "हेल्पलाइन",
        "missing_fields_note": "अधिक योजना तपासण्यासाठी कृपया पुष्टी करा",
        "grounding_note": "सर्व योजना व अटी अधिकृत सरकारी कागदपत्रांवरून पडताळलेल्या आहेत.",
        "reason_prefix": "पूर्ण झालेल्या अटी",
        "where_label": "कुठे मिळेल",
        "step_prefix": "टप्पा",
    },
    "kn": {
        "language_name": "ಕನ್ನಡ (Kannada)",
        "greeting": "ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಮತ್ತು ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಯೋಜನೆ ದಾಖಲೆಗಳ ಆಧಾರದ ಮೇಲೆ ನಿಮ್ಮ ಅರ್ಹತಾ ಮಾರ್ಗದರ್ಶಿ ಇಲ್ಲಿದೆ:",
        "eligible_heading": "ಅರ್ಹ ಸರ್ಕಾರಿ ಕಲ್ಯಾಣ ಯೋಜನೆಗಳು",
        "potential_heading": "ಹೆಚ್ಚುವರಿ ದೃಢೀಕರಣ ಅಗತ್ಯವಿರುವ ಯೋಜನೆಗಳು",
        "no_schemes": "ನೀಡಿದ ವಿವರಗಳ ಆಧಾರದ ಮೇಲೆ, ನೀವು ಪ್ರಸ್ತುತ ಯಾವುದೇ ಕಲ್ಯಾಣ ಯೋಜನೆಯ ಅರ್ಹತಾ ಮಾನದಂಡಗಳನ್ನು ಪೂರೈಸುತ್ತಿಲ್ಲ.",
        "reason_label": "ಅರ್ಹತೆಯ ಕಾರಣ",
        "benefit_label": "ಪ್ರಯೋಜನ",
        "docs_heading": "ಅಗತ್ಯ ದಾಖಲೆಗಳ ಪಟ್ಟಿ",
        "steps_heading": "ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ಹಂತ-ಹಂತದ ವಿಧಾನ",
        "portal_label": "ಅಧಿಕೃತ ಪೋರ್ಟಲ್",
        "helpline_label": "ಸಹಾಯವಾಣಿ",
        "missing_fields_note": "ಹೆಚ್ಚಿನ ಯೋಜನೆಗಳನ್ನು ಪರಿಶೀಲಿಸಲು ದಯವಿಟ್ಟು ದೃಢೀಕರಿಸಿ",
        "grounding_note": "ಎಲ್ಲಾ ಯೋಜನೆಗಳು ಮತ್ತು ನಿಯಮಗಳನ್ನು ಅಧಿಕೃತ ದಾಖಲೆಗಳಿಂದ ಪರಿಶೀಲಿಸಲಾಗಿದೆ.",
        "reason_prefix": "ಪೂರೈಸಿದ ಮಾನದಂಡಗಳು",
        "where_label": "ಎಲ್ಲಿ ಪಡೆಯಬೇಕು",
        "step_prefix": "ಹಂತ",
    },
    "pa": {
        "language_name": "ਪੰਜਾਬੀ (Punjabi)",
        "greeting": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਤੁਹਾਡੀ ਨਾਗਰਿਕ ਪ੍ਰੋਫਾਈਲ ਅਤੇ ਸਰਕਾਰੀ ਯੋਜਨਾ ਦਸਤਾਵੇਜ਼ਾਂ ਦੇ ਆਧਾਰ 'ਤੇ ਤੁਹਾਡੀ ਯੋਗਤਾ ਗਾਈਡ ਹੇਠਾਂ ਦਿੱਤੀ ਗਈ ਹੈ:",
        "eligible_heading": "ਯੋਗ ਸਰਕਾਰੀ ਭਲਾਈ ਯੋਜਨਾਵਾਂ",
        "potential_heading": "ਹੋਰ ਪੁਸ਼ਟੀ ਦੀ ਲੋੜ ਵਾਲੀਆਂ ਯੋਜਨਾਵਾਂ",
        "no_schemes": "ਦਿੱਤੇ ਵੇਰਵਿਆਂ ਦੇ ਆਧਾਰ 'ਤੇ, ਤੁਸੀਂ ਇਸ ਵੇਲੇ ਉਪਲਬਧ ਭਲਾਈ ਯੋਜਨਾਵਾਂ ਦੀਆਂ ਸ਼ਰਤਾਂ ਪੂਰੀਆਂ ਨਹੀਂ ਕਰਦੇ।",
        "reason_label": "ਯੋਗਤਾ ਦਾ ਕਾਰਨ",
        "benefit_label": "ਲਾਭ",
        "docs_heading": "ਲੋੜੀਂਦੇ ਦਸਤਾਵੇਜ਼ਾਂ ਦੀ ਸੂਚੀ",
        "steps_heading": "ਅਰਜ਼ੀ ਦੇਣ ਦੀ ਕਦਮ-ਦਰ-ਕਦਮ ਪ੍ਰਕਿਰਿਆ",
        "portal_label": "ਅਧਿਕਾਰਤ ਪੋਰਟਲ",
        "helpline_label": "ਹੈਲਪਲਾਈਨ",
        "missing_fields_note": "ਹੋਰ ਯੋਜਨਾਵਾਂ ਦੀ ਸਹੀ ਜਾਂਚ ਲਈ ਕਿਰਪਾ ਕਰਕੇ ਪੁਸ਼ਟੀ ਕਰੋ",
        "grounding_note": "ਸਾਰੀਆਂ ਯੋਜਨਾਵਾਂ ਅਤੇ ਨਿਯਮ ਅਧਿਕਾਰਤ ਸਰਕਾਰੀ ਦਸਤਾਵੇਜ਼ਾਂ ਤੋਂ ਪ੍ਰਮਾਣਿਤ ਹਨ।",
        "reason_prefix": "ਪੂਰੇ ਕੀਤੇ ਮਾਪਦੰਡ",
        "where_label": "ਕਿੱਥੋਂ ਪ੍ਰਾਪਤ ਕਰੀਏ",
        "step_prefix": "ਕਦਮ",
    },
    "gu": {
        "language_name": "ગુજરાતી (Gujarati)",
        "greeting": "નમસ્તે! તમારી નાગરિક પ્રોફાઇલ અને સત્તાવાર સરકારી યોજના દસ્તાવેજોના આધારે તમારી પાત્રતા માર્ગદર્શિકા નીચે મુજબ છે:",
        "eligible_heading": "પાત્ર સરકારી કલ્યાણ યોજનાઓ",
        "potential_heading": "વધુ પુષ્ટિની જરૂર હોય તેવી યોજનાઓ",
        "no_schemes": "આપેલી વિગતોના આધારે, તમે હાલમાં ઉપલબ્ધ કલ્યાણ યોજનાઓની પાત્રતાની શરતો પૂર્ણ કરતા નથી.",
        "reason_label": "પાત્રતાનું કારણ",
        "benefit_label": "લાભ",
        "docs_heading": "જરૂરી દસ્તાવેજોની યાદી",
        "steps_heading": "અરજી કરવાની તબક્કાવાર પ્રક્રિયા",
        "portal_label": "સત્તાવાર પોર્ટલ",
        "helpline_label": "હેલ્પલાઇન",
        "missing_fields_note": "વધારાની યોજનાઓ તપાસવા માટે કૃપા કરીને પુષ્ટિ કરો",
        "grounding_note": "બધી યોજનાઓ અને નિયમો સત્તાવાર સરકારી દસ્તાવેજો દ્વારા ચકાસાયેલ છે.",
        "reason_prefix": "પૂર્ણ થયેલ માપદંડ",
        "where_label": "ક્યાંથી મેળવવું",
        "step_prefix": "પગલું",
    },
    "ml": {
        "language_name": "മലയാളം (Malayalam)",
        "greeting": "നമസ്കാരം! നിങ്ങളുടെ പ്രൊഫൈലും ഔദ്യോഗിക സർക്കാർ പദ്ധതി രേഖകളും അടിസ്ഥാനമാക്കിയുള്ള യോഗ്യതാ മാർഗ്ഗനിർദ്ദേശം താഴെ നൽകുന്നു:",
        "eligible_heading": "യോഗ്യമായ സർക്കാർ ക്ഷേമ പദ്ധതികൾ",
        "potential_heading": "കൂടുതൽ സ്ഥിരീകരണം ആവശ്യമായ പദ്ധതികൾ",
        "no_schemes": "നൽകിയ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ, നിലവിൽ ലഭ്യമായ ക്ഷേമ പദ്ധതികളുടെ യോഗ്യതാ മാനദണ്ഡങ്ങൾ നിങ്ങൾ പാലിക്കുന്നില്ല.",
        "reason_label": "യോഗ്യതയ്ക്കുള്ള കാരണം",
        "benefit_label": "ആനുകൂല്യം",
        "docs_heading": "ആവശ്യമായ രേഖകളുടെ പട്ടിക",
        "steps_heading": "അപേക്ഷിക്കാനുള്ള ഘട്ടം ഘട്ടമായുള്ള നടപടിക്രമം",
        "portal_label": "ഔദ്യോഗിക പോർട്ടൽ",
        "helpline_label": "ഹെൽപ്പ്‌ലൈൻ",
        "missing_fields_note": "കൂടുതൽ പദ്ധതികൾ പരിശോധിക്കാൻ ദയവായി സ്ഥിരീകരിക്കുക",
        "grounding_note": "എല്ലാ പദ്ധതികളും നിബന്ധനകളും ഔദ്യോഗിക രേഖകളിൽ നിന്ന് സ്ഥിരീകരിച്ചിട്ടുണ്ട്.",
        "reason_prefix": "പൂർത്തിയാക്കിയ മാനദണ്ഡങ്ങൾ",
        "where_label": "എവിടെ നിന്ന് ലഭിക്കും",
        "step_prefix": "ഘട്ടം",
    },
    "or": {
        "language_name": "ଓଡ଼ିଆ (Odia)",
        "greeting": "ନମସ୍କାର! ଆପଣଙ୍କ ପ୍ରୋଫାଇଲ୍ ଏବଂ ସରକାରୀ ଯୋଜନା ଦସ୍ତାବିଜ୍ ଆଧାରରେ ଆପଣଙ୍କ ଯୋଗ୍ୟତା ମାର୍ଗଦର୍ଶିକା ନିମ୍ନରେ ଦିଆଯାଇଛି:",
        "eligible_heading": "ଯୋଗ୍ୟ ସରକାରୀ କଲ୍ୟାଣ ଯୋଜନା",
        "potential_heading": "ଅଧିକ ନିଶ୍ଚିତକରଣ ଆବଶ୍ୟକ କରୁଥିବା ଯୋଜନା",
        "no_schemes": "ଦିଆଯାଇଥିବା ସୂଚନା ଆଧାରରେ, ଆପଣ ବର୍ତ୍ତମାନ ଉପଲବ୍ଧ କଲ୍ୟାଣ ଯୋଜନାର ଯୋଗ୍ୟତା ସର୍ତ୍ତ ପୂରଣ କରୁନାହାନ୍ତି।",
        "reason_label": "ଯୋଗ୍ୟତାର କାରଣ",
        "benefit_label": "ଲାଭ",
        "docs_heading": "ଆବଶ୍ୟକ ଦସ୍ତାବିଜ୍ ତାଲିକା",
        "steps_heading": "ଆବେଦନ କରିବାର ପର୍ଯ୍ୟାୟକ୍ରମ ପଦ୍ଧତି",
        "portal_label": "ସରକାରୀ ପୋର୍ଟାଲ୍",
        "helpline_label": "ହେଲ୍ପଲାଇନ୍",
        "missing_fields_note": "ଅଧିକ ଯୋଜନା ଯାଞ୍ଚ କରିବାକୁ ଦୟାକରି ନିଶ୍ଚିତ କରନ୍ତୁ",
        "grounding_note": "ସମସ୍ତ ଯୋଜନା ଏବଂ ନିୟମ ସରକାରୀ ଦସ୍ତାବିଜ୍ ଦ୍ୱାରା ଯାଞ୍ଚ କରାଯାଇଛି।",
        "reason_prefix": "ପୂରଣ ହୋଇଥିବା ମାନଦଣ୍ଡ",
        "where_label": "କେଉଁଠାରୁ ମିଳିବ",
        "step_prefix": "ପର୍ଯ୍ୟାୟ",
    },
    "ur": {
        "language_name": "اردو (Urdu)",
        "greeting": "آداب! آپ کی پروفائل اور سرکاری اسکیموں کی سرکاری دستاویزات کی بنیاد پر آپ کی اہلیت کا رہنما نامہ درج ذیل ہے:",
        "eligible_heading": "اہل سرکاری فلاحی اسکیمیں",
        "potential_heading": "مزید تصدیق کی محتاج اسکیمیں",
        "no_schemes": "فراہم کردہ تفصیلات کی بنیاد پر، آپ فی الحال دستیاب فلاحی اسکیموں کی اہلیت کے معیار پر پورا نہیں اترتے۔",
        "reason_label": "اہلیت کی وجہ",
        "benefit_label": "فائدہ",
        "docs_heading": "ضروری دستاویزات کی فہرست",
        "steps_heading": "درخواست دینے کا مرحلہ وار طریقہ",
        "portal_label": "سرکاری پورٹل",
        "helpline_label": "ہیلپ لائن",
        "missing_fields_note": "مزید اسکیموں کی درست جانچ کے لیے براہ کرم تصدیق کریں",
        "grounding_note": "تمام اسکیمیں اور قواعد سرکاری دستاویزات سے تصدیق شدہ ہیں۔",
        "reason_prefix": "پورے کیے گئے معیار",
        "where_label": "کہاں سے حاصل کریں",
        "step_prefix": "مرحلہ",
    },
}


# Marathi-exclusive Devanagari tokens distinguishing Marathi from Hindi
_MARATHI_MARKERS = [
    "माझे", "माझी", "माझा", "मी", "आहे", "नाही", "मला", "शेतकरी", "कारागीर", "कुंभार",
    "भागातील", "वर्षांचा", "वर्षांची", "उत्पन्न", "पक्के", "नोकरदार", "ग्रामीण भागातील", "रुपये",
]
# Wait: "रुपये" appears in both Hindi & Marathi; focus on uniquely Marathi tokens when scoring
_UNIQUE_MARATHI_TOKENS = [
    "माझे", "माझी", "माझा", "आहे", "नाही", "मला", "शेतकरी", "कारागीर",
    "कुंभार", "भागातील", "वर्षांचा", "वर्षांची", "उत्पन्न", "पक्के", "नोकरदार", "मी ",
]


class LanguagePackRegistry:
    """
    Registry providing language detection, multilingual profile extraction,
    and localized response rendering utilities across all 12 supported languages.
    """

    @staticmethod
    def get_template(lang: LanguageCode | str) -> dict[str, str]:
        """Return template dictionary for the requested language code, defaulting to English."""
        code = lang.value if isinstance(lang, LanguageCode) else str(lang)
        return LANGUAGE_TEMPLATES.get(code, LANGUAGE_TEMPLATES["en"])

    @staticmethod
    def detect_language(text: str, preferred_language: LanguageCode | None = None) -> LanguageCode:
        """
        Detect citizen language from Unicode script frequencies across all 12 supported
        languages (with Marathi vs Hindi disambiguation) unless preferred_language is supplied.
        """
        if preferred_language is not None:
            return preferred_language

        counts = {
            "pa": sum(1 for ch in text if "\u0A00" <= ch <= "\u0A7F"),
            "gu": sum(1 for ch in text if "\u0A80" <= ch <= "\u0AFF"),
            "or": sum(1 for ch in text if "\u0B00" <= ch <= "\u0B7F"),
            "ml": sum(1 for ch in text if "\u0D00" <= ch <= "\u0D7F"),
            "ur": sum(1 for ch in text if "\u0600" <= ch <= "\u06FF"),
            "te": sum(1 for ch in text if "\u0C00" <= ch <= "\u0C7F"),
            "ta": sum(1 for ch in text if "\u0B80" <= ch <= "\u0BFF"),
            "bn": sum(1 for ch in text if "\u0980" <= ch <= "\u09FF"),
            "kn": sum(1 for ch in text if "\u0C80" <= ch <= "\u0CFF"),
            "devanagari": sum(1 for ch in text if "\u0900" <= ch <= "\u097F"),
        }

        # Pick distinct non-Devanagari Indic / Perso-Arabic scripts if clearly present
        for code in ("pa", "gu", "or", "ml", "ur", "te", "ta", "bn", "kn"):
            if counts[code] >= 3:
                return LanguageCode(code)

        # Disambiguate Devanagari between Marathi (mr) and Hindi (hi)
        if counts["devanagari"] >= 3:
            marathi_hits = sum(1 for tok in _UNIQUE_MARATHI_TOKENS if tok in text)
            if marathi_hits >= 2:
                return LanguageCode.MARATHI
            return LanguageCode.HINDI

        return LanguageCode.ENGLISH

    @staticmethod
    def script_match_ratio(text: str, target_lang: LanguageCode) -> float:
        """
        Compute ratio of target-script characters among alphabetic characters (ignoring
        preserved official Latin scheme names inside parentheses/English titles).
        Used by the Language-Consistency Reviewer Agent across all 12 supported languages.
        """
        # Strip URLs, digits, and known ASCII scheme acronyms/names before measuring prose script
        stripped = re.sub(r"https?://\S+", " ", text)
        if target_lang == LanguageCode.ENGLISH:
            ascii_alpha = sum(1 for c in stripped if c.isascii() and c.isalpha())
            total_alpha = sum(1 for c in stripped if c.isalpha())
            return round(ascii_alpha / max(1, total_alpha), 4)

        script_ranges = {
            LanguageCode.HINDI: ("\u0900", "\u097F"),
            LanguageCode.MARATHI: ("\u0900", "\u097F"),
            LanguageCode.PUNJABI: ("\u0A00", "\u0A7F"),
            LanguageCode.GUJARATI: ("\u0A80", "\u0AFF"),
            LanguageCode.ODIA: ("\u0B00", "\u0B7F"),
            LanguageCode.MALAYALAM: ("\u0D00", "\u0D7F"),
            LanguageCode.URDU: ("\u0600", "\u06FF"),
            LanguageCode.TELUGU: ("\u0C00", "\u0C7F"),
            LanguageCode.TAMIL: ("\u0B80", "\u0BFF"),
            LanguageCode.BENGALI: ("\u0980", "\u09FF"),
            LanguageCode.KANNADA: ("\u0C80", "\u0CFF"),
        }
        low, high = script_ranges[target_lang]
        target_chars = sum(1 for c in stripped if low <= c <= high)
        # Count prose tokens outside official English scheme names/portals
        non_space_alpha = sum(1 for c in stripped if c.isalpha())
        if non_space_alpha == 0:
            return 0.0
        # Because official scheme names & labels are intentionally kept intact in English,
        # scale ratio relative to expected native script density
        raw_ratio = target_chars / non_space_alpha
        return round(min(1.0, raw_ratio * 1.45), 4) if target_chars >= 15 else round(raw_ratio, 4)

    @classmethod
    def extract_profile_from_text(
        cls,
        raw_text: str,
        *,
        existing: CitizenProfile | None = None,
        preferred_language: LanguageCode | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> CitizenProfile:
        """
        Parse multilingual free-text citizen description into a structured CitizenProfile,
        merging cleanly with existing memory state and optional interactive UI overrides.
        """
        lang = cls.detect_language(raw_text, preferred_language)
        norm = normalize_digits(raw_text).lower()
        data = existing.model_dump() if existing else {}
        data["language"] = lang
        data["raw_query"] = raw_text

        # --- 1. Age extraction across 12 languages ---
        age_patterns = [
            r"(?:aged|age|वय|आयु|ਉਮਰ|ઉંਮર|വയസ്സ്|വയസ്|ବୟସ|عمر|వయస్సు|వయసు|வயது|বয়স|ವಯಸ್ಸು)\s*[:\-]?\s*(\d{1,3})",
            r"(\d{1,3})\s*(?:-?\s*year|\s*years|\s*yrs|\s*yo\b|साल|वर्ष|वर्षांचा|वर्षांची|ਸਾਲ|ਸਾਲਾਂ|વર્ષ|વર્ષનો|વર્ષની|വയസ്സുള്ള|വയസ്|വർഷം|ବର୍ଷ|ବର୍ଷର|سال|برس|సంవత్సరాల|ఏళ్ల|వయసు|வயது|বছর|বয়সী|ವರ್ಷ|ವರ್ಷದ)",
        ]
        for pat in age_patterns:
            m = re.search(pat, norm)
            if m:
                age_val = int(m.group(1))
                if 0 <= age_val <= 115:
                    data["age"] = age_val
                    break

        # --- 2. Annual income extraction (handles lakhs, thousands, raw INR) ---
        lakh_pat = r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|लाख|लक्ष|ਲੱਖ|લાખ|ലക്ഷം|ଲକ୍ଷ|لاکھ|లక్ష|లక్షల|லட்சம்|লক্ষ|ಲಕ್ಷ)\b"
        thousand_pat = r"(\d+(?:\.\d+)?)\s*(?:thousand|k\b|हजार|हज़ार|ਹਜ਼ਾਰ|ਹਜਾਰ|હજાર|ആയിരം|ହଜାର|ہزار|వేల|ஆயிரம்|হাজার|ಸಾವಿರ)"
        income_context_pat = r"(?:income|salary|earn|earning|आय|उत्पन्न|ਆਮਦਨ|ਕਮਾਈ|આવક|કમાણી|വരുമാനം|ଆୟ|ରୋଜଗାର|آمدنی|آمدن|تنخواہ|आदాయం|வருமானம்|আয়|ಆದಾಯ)[^0-9]{0,25}(\d[\d,]{2,8})"
        currency_pat = r"(?:rs\.?|inr|₹|रुपये|रुपए|ਰੁਪਏ|રૂપિયા|രൂപ|ଟଙ୍କା|روپے|రూపాయలు|ரூபாய்|টাকা|ರೂಪಾಯಿ)\s*(\d[\d,]{2,8})|(\d[\d,]{3,8})\s*(?:rs\.?|inr|₹|रुपये|रुपए|ਰੁਪਏ|રૂપિયા|രൂപ|ଟଙ୍କା|روپے|రూపాయలు|ரூபாய்|টাকা|ರೂಪಾಯಿ)"

        m_lakh = re.search(lakh_pat, norm)
        m_thou = re.search(thousand_pat, norm)
        m_inc = re.search(income_context_pat, norm)
        m_curr = re.search(currency_pat, norm)

        if m_lakh:
            data["annual_income_inr"] = int(float(m_lakh.group(1)) * 100000)
        elif m_inc:
            data["annual_income_inr"] = int(m_inc.group(1).replace(",", ""))
        elif m_curr:
            val = m_curr.group(1) or m_curr.group(2)
            data["annual_income_inr"] = int(val.replace(",", ""))
        elif m_thou and any(
            w in norm
            for w in [
                "income", "earn", "salary", "आय", "उत्पन्न", "ਆਮਦਨ", "ਕਮਾਈ",
                "આવક", "വരുമാനം", "ଆୟ", "آمدنی", "आदాయం", "வருமானம்", "আয়", "ಆದಾಯ",
            ]
        ):
            data["annual_income_inr"] = int(float(m_thou.group(1)) * 1000)

        # --- 3. Gender & Marital Status ---
        female_tokens = [
            "female", "woman", "widow", "widowed", "pregnant", "lactating", "mother",
            "महिला", "औरत", "विधवा", "गर्भवती", "स्त्री",
            "ਔਰਤ", "ਮਹਿਲਾ", "ਵਿਧਵਾ", "ਗਰਭਵਤੀ",
            "મહિલા", "સ્ત્રી", "વિધવા", "ગર્ભવતી",
            "സ്ത്രീ", "വനിത", "വിധവ", "ഗർഭിണി",
            "ମହିଳା", "ସ୍ତ୍ରୀ", "ବିଧବା", "ଗର୍ଭବତୀ",
            "عورت", "خاتون", "بیوہ", "حاملہ",
            "మహిళ", "వితంతువు", "గర్భిణి",
            "பெண்", "விதவை", "கர்ப்பிணி",
            "মহিলা", "বিধবা", "গর্ভবতী",
            "ಮಹಿಳೆ", "ವಿಧವೆ", "ಗರ್ಭಿಣಿ",
        ]
        male_tokens = [
            "male", "man ", "men ", "पुरुष", "ਪੁਰਸ਼", "ਆਦਮੀ", "ਮਰਦ", "પુરુષ",
            "പുരുഷൻ", "ପୁରୁଷ", "مرد", "పురుష", "ஆண்", "পুরুষ", "ಪುರುಷ",
        ]
        if any(tok in norm for tok in female_tokens) and "girl child" not in norm.replace("woman", ""):
            data["gender"] = "female"
        elif any(tok in norm for tok in male_tokens) or (
            data.get("gender") is None
            and any(w in norm for w in ["किसान हूं", "बुजुर्ग हूं", "कारागीर आहे", "व्यक्ति", "ਕਿਸਾਨ ਹਾਂ", "ખેડૂત છું", "കർഷകനാണ്", "ଚାଷୀ ଅଟେ", "کسان ہوں"])
        ):
            # Only infer male when explicit male markers appear; keep neutral otherwise
            if any(tok in norm for tok in male_tokens) or any(
                w in norm for w in ["किसान हूं", "बुजुर्ग हूं", "कारागीर आहे", "ਕਿਸਾਨ ਹਾਂ", "ખેડૂત છું", "കർഷകനാണ്", "کسان ہوں"]
            ):
                data["gender"] = "male"

        if any(tok in norm for tok in ["widow", "widowed", "विधवा", "ਵਿਧਵਾ", "વિધવા", "വിധവ", "ବିଧବା", "بیوہ", "వితంతువు", "விதவை", "বিধবা", "ವಿಧವೆ"]):
            data["marital_status"] = "widowed"
            data["gender"] = "female"

        # --- 4. Pregnancy / Lactating Status ---
        if any(tok in norm for tok in ["pregnant", "lactating", "गर्भवती", "स्तनपान", "ਗਰਭਵਤੀ", "ગર્ભવતી", "ഗർഭിണി", "ଗର୍ଭବତୀ", "حاملہ", "గర్భిణి", "గర్భవతి", "கர்ப்பிணி", "গর্ভবতী", "ಗರ್ಭಿಣಿ"]):
            data["is_pregnant_or_lactating"] = True
            data["gender"] = "female"

        # --- 5. Residence Type (Rural vs Urban) ---
        if any(tok in norm for tok in [
            "rural", "village", "panchayat", "गांव", "गाँव", "ग्रामीण", "खेड",
            "ਪਿੰਡ", "ਪੇਂਡੂ", "ગામ", "ગ્રામીણ", "ഗ്രാമം", "ഗ്രാമീണ", "ଗାଁ", "ଗ୍ରାମୀଣ", "گاؤں", "دیہی",
            "గ్రామీణ", "గ్రామం", "கிராமம்", "கிராம", "গ্রাম", "গ্রামীণ", "ಗ್ರಾಮೀಣ", "ಹಳ್ಳಿ",
        ]):
            data["residence_type"] = "rural"
        elif any(tok in norm for tok in [
            "urban", "city", "town", "municipal", "शहर", "शहरी", "नगर",
            "ਸ਼ਹਿਰ", "ਸ਼ਹਿਰੀ", "શહેર", "શહેરી", "നഗരം", "നഗര", "ସହର", "ସହରୀ", "شہر", "شہری",
            "నగరం", "పట్టణ", "நகர", "শহর", "ನಗರ",
        ]):
            data["residence_type"] = "urban"

        # --- 6. Occupation Extraction ---
        occ_map: list[tuple[str, list[str]]] = [
            ("govt_employee", [
                "government employee", "govt employee", "सरकारी कर्मचारी", "सरकारी नौकरी", "सरकारी नोकरदार",
                "ਸਰਕਾਰੀ ਕਰਮਚਾਰੀ", "ਸਰਕਾਰੀ ਨੌਕਰੀ", "સરકારી કર્મચારી", "સરકારી નોકરી",
                "സർക്കാർ ജീവനക്കാരൻ", "സർക്കാർ ഉദ്യോഗസ്ഥൻ", "ସରକାରୀ କର୍ମଚାରୀ", "ସରକାରୀ ଚାକିରି", "سرکاری ملازم", "سرکاری نوکری",
                "ప్రభుత్వ ఉద్యోగి", "அரசு ஊழியர்", "সরকারি কর্মচারী", "ಸರ್ಕಾರಿ ನೌಕರ",
            ]),
            ("street_vendor", [
                "street vendor", "hawker", "रेहड़ी", "पटरी", "पथविक्रेता",
                "ਰੇਹੜੀ", "ਫੜ੍ਹੀ", "લારી", "ફેરિયો", "വഴിയോര കച്ചവടക്കാരൻ", "ରାସ୍ତା କଡ଼ ବିକାଳି", "ریڑھی", "پھیری والا",
                "వీధి వ్యాపారి", "தெரு வியாபாரி", "রাস্তার হকার", "ಬೀದಿ ವ್ಯಾಪಾರಿ",
            ]),
            ("farmer", [
                "farmer", "cultivator", "kisan", "किसान", "खेती", "शेतकरी",
                "ਕਿਸਾਨ", "ਖੇਤੀ", "ખેડૂત", "ખેતી", "കർഷകൻ", "കൃഷി", "ଚାଷୀ", "କୃଷକ", "ଚାଷ", "کسان", "کاشتکار", "کھیتی",
                "రైతు", "వ్యవసాయ", "விவசாயி", "কৃষক", "ರೈತ",
            ]),
            ("student", [
                "student", "undergraduate", "postgraduate", "college", "diploma", "छात्र", "छात्रा", "विद्यार्थी",
                "ਵਿਦਿਆਰਥੀ", "ਕਾਲਜ", "વિદ્યાર્થી", "કોલેજ", "വിദ്യാർത്ഥി", "കോളേജ്", "ଛାତ୍ର", "ଛାତ୍ରୀ", "ବିଦ୍ୟାର୍ଥୀ", "طالب علم", "طالبہ", "کالج",
                "విద్యార్థి", "மாணவர்", "ছাত্র", "ವಿದ್ಯಾರ್ಥಿ",
            ]),
            ("artisan", [
                "artisan", "craftsperson", "potter", "carpenter", "tailor", "weaver", "blacksmith",
                "कारीगर", "कुम्हार", "बढ़ई", "दर्जी", "कारागीर", "कुंभार",
                "ਕਾਰੀਗਰ", "ਘੁਮਿਆਰ", "ਤਰਖਾਣ", "ਦਰਜ਼ੀ", "ਜੁਲਾਹਾ", "કારીગર", "કુંભાર", "સુથાર", "દરજી",
                "കൈത്തൊഴിലാളി", "കുശവൻ", "ആശാരി", "କାରୀଗର", "କୁମ୍ଭାର", "ବଢ଼େଇ", "ତନ୍ତୀ", "کاریگر", "کمہار", "بڑھئی", "درزی", "بنکر",
                "కుమ్మరి", "చేనేత", "கைவினைஞர்", "কারিগর", "কুমোর", "ಕುಶಲಕರ್ಮಿ", "ಕುಂಬಾರ",
            ]),
            ("small_business", [
                "small business", "shopkeeper", "business owner", "दुकानदार", "व्यापारी", "व्यावसायिक",
                "ਦੁਕਾਨਦਾਰ", "ਵਪਾਰੀ", "દુકાનદાર", "વેપારી", "ചെറുകിട വ്യാപാരി", "കച്ചവടക്കാരൻ", "ଦୋକାନୀ", "ବ୍ୟବସାୟୀ", "دکاندار", "تاجر", "کاروبار",
                "వ్యాపారి", "சிறு வணிக", "ব্যবসায়ী", "ವ್ಯಾಪಾರಿ",
            ]),
            ("daily_wage_laborer", [
                "daily wage", "laborer", "labourer", "मजदूर", "मजूर",
                "ਮਜ਼ਦੂਰ", "ਦਿਹਾੜੀਦਾਰ", "મજૂર", "રોજમદાર", "കൂലിത്തൊഴിലാളി", "തൊഴിലാളി", "ଶ୍ରମିକ", "ମଜୁରିଆ", "مزدور", "دیہاڑی دار",
                "కూలీ", "தொழிலாளி", "শ্রমিক", "ಕೂಲಿ",
            ]),
            ("unemployed", [
                "unemployed", "बेरोजगार", "ਬੇਰੁਜ਼ਗਾਰ", "ਬੇਰੋਜ਼ਗਾਰ", "બેરોજગાર", "തൊഴിൽരഹിതൻ", "ବେକାର", "ବେରୋଜଗାର", "بے روزگار",
                "నిరుద్యోగి", "வேலையற்ற", "বেকার", "ನಿರುದ್ಯೋಗಿ",
            ]),
            ("retired", [
                "retired", "रिटायर्ड", "सेवानिवृत्त", "बुजुर्ग", "ਸੇਵਾਮੁਕਤ", "ਰਿਟਾਇਰਡ", "નિવૃત્ત", "വിരമിച്ച", "ଅବସରପ୍ରାପ୍ତ", "ریٹائرڈ",
                "पेंशनर", "ओய்வு", "ನಿವೃತ್ತ",
            ]),
        ]
        # Check negation of govt employee first so "not a government employee" does NOT set occupation=govt_employee
        neg_govt = any(
            neg in norm
            for neg in [
                "not a government employee", "not govt employee", "non-govt", "non government",
                "सरकारी कर्मचारी नहीं", "सरकारी नौकरी नहीं", "सरकारी नोकरदार नाही",
                "ਸਰਕਾਰੀ ਕਰਮਚਾਰੀ ਨਹੀਂ", "ਸਰਕਾਰੀ ਨੌਕਰੀ ਨਹੀਂ", "ਸਰਕਾਰੀ ਕਰਮਚਾਰੀ ਨਹੀ",
                "સરકારી કર્મચારી નથી", "સરકારી નોકરી નથી",
                "സർക്കാർ ജീവനക്കാരനല്ല", "സർക്കാർ ജീവനക്കാരിയല്ല",
                "ସରକାରୀ କର୍ମଚାରୀ ନୁହେଁ", "ସରକାରୀ କର୍ମଚାରୀ ନୁହନ୍ତି",
                "سرکاری ملازم نہیں", "سرکاری نوکری نہیں",
                "ప్రభుత్వ ఉద్యోగి కాదు", "அரசு ஊழியர் அல்ல", "সরকারি কর্মচারী নই", "ಸರ್ಕಾರಿ ನೌಕರರಲ್ಲ",
            ]
        )
        if neg_govt:
            data["is_govt_employee"] = False

        for occ_key, keywords in occ_map:
            if occ_key == "govt_employee" and neg_govt:
                continue
            if any(kw in norm for kw in keywords):
                data["occupation"] = occ_key
                if occ_key == "govt_employee":
                    data["is_govt_employee"] = True
                break

        # Default is_govt_employee=False if citizen explicitly stated another private/non-govt livelihood
        if data.get("is_govt_employee") is None and data.get("occupation") in {
            "farmer", "student", "street_vendor", "artisan", "small_business", "daily_wage_laborer", "unemployed", "retired"
        }:
            data["is_govt_employee"] = False

        # --- 7. Education Level (for scholarships) ---
        if any(w in norm for w in ["undergraduate", "b.tech", "btech", "b.sc", "b.a", "b.com", "engineering", "college", "degree", "ਗ੍ਰੈਜੂਏਟ", "બી.એ", "ബിരുദ", "ସ୍ନାତକ", "بی اے"]):
            data["education_level"] = "undergraduate"
        elif any(w in norm for w in ["postgraduate", "m.tech", "msc", "mba", "master", "ਪੋਸਟ ਗ੍ਰੈਜੂਏਟ"]):
            data["education_level"] = "postgraduate"
        elif any(w in norm for w in ["diploma", "ਡਿਪਲੋਮਾ", "ડિપ્લોમા"]):
            data["education_level"] = "diploma"
        elif any(w in norm for w in ["class 11", "class 12", "11th", "12th", "intermediate", "hsc"]):
            data["education_level"] = "class_11_12"

        # --- 8. Social Category ---
        for cat, kws in [
            ("SC", [" sc ", "sc category", "scheduled caste", "अनुसूचित जाति", "एससी", "ਐਸਸੀ", "એસસી", "എസ്‌സി", "ଏସସି", "ایس سی", "ఎస్సీ", "எஸ்சி", "এসসি"]),
            ("ST", [" st ", "st category", "scheduled tribe", "अनुसूचित जनजाति", "एसटी", "ਐਸਟੀ", "એસટી", "എസ്‌ടി", "ଏସଟି", "ایس ٹی", "ఎస్టీ", "எஸ்டி", "এসটি"]),
            ("OBC", ["obc", "other backward", "ओबीसी", "अन्य पिछड़ा", "ਓਬੀਸੀ", "ઓબીસી", "ഒബിസി", "ଓବିସି", "او بی سی", "ఓబీసీ", "ஓபிசி", "ওবিসি"]),
            ("EBC", ["ebc", "economically backward"]),
            ("DNT", ["dnt", "denotified"]),
            ("Minority", ["minority", "अल्पसंख्यक", "ਘੱਟ ਗਿਣਤੀ", "લઘુમતી", "ന്യൂനപക്ഷ", "ସଂଖ୍ୟାଲଘୁ", "اقلیت", "మైనారిటీ"]),
            ("General", ["general category", "unreserved"]),
        ]:
            padded_norm = f" {norm} "
            if any(kw in padded_norm for kw in kws):
                data["social_category"] = cat
                break

        # --- 9. Cultivable Land & Acres ---
        land_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:acre|acres|एकड़|एकर|ਏਕੜ|એકર|ഏക്കർ|ଏକର|ایکڑ|ఎకరా|ఎకరాల|ஏக்கர்|একর|ಎಕರೆ)", norm)
        if land_match:
            acres = float(land_match.group(1))
            data["land_acres"] = acres
            data["owns_cultivable_land"] = acres > 0
        elif any(w in norm for w in [
            "cultivable land", "agricultural land", "खेती की जमीन", "ਖੇਤੀ ਵਾਲੀ ਜ਼ਮੀਨ", "ਵਾਹੀਯੋਗ ਜ਼ਮੀਨ",
            "ખેતીની જમીન", "കൃഷിഭൂമി", "ଚାଷ ଜମି", "زرعی زمین", "సాగు భూమి", "விவசாய நிலம்", "চাষের জমি",
        ]):
            data["owns_cultivable_land"] = True

        # --- 10. BPL Card (positive & negative) ---
        no_bpl = any(p in norm for p in [
            "no bpl", "without bpl", "not bpl", "bpl कार्ड नहीं", "बीपीएल कार्ड नहीं",
            "ਬੀਪੀਐਲ ਕਾਰਡ ਨਹੀਂ", "ਬੀਪੀਐਲ ਨਹੀਂ", "બીપીએલ કાર્ડ નથી", "બીપીએલ નથી",
            "ബിപിഎൽ കാർഡ് ഇല്ല", "ബിപിഎൽ ഇല്ല", "ବିପିଏଲ୍ କାର୍ଡ ନାହିଁ", "ବିପିଏଲ୍ ନାହିଁ", "بی پی ایل کارڈ نہیں",
            "బీపీఎల్ కార్డు లేదు", "பிபிஎல் இல்லை",
        ])
        has_bpl = any(p in norm for p in [
            "bpl", "बीपीएल", "ਬੀਪੀਐਲ", "બીપીએલ", "ബിപിഎൽ", "ବିପିଏଲ୍", "بی پی ایل",
            "బిపిఎల్", "బీపీఎల్", "பிபிஎல்", "বিপিএল", "ಬಿಪಿಎಲ್",
        ])
        if no_bpl:
            data["has_bpl_card"] = False
        elif has_bpl:
            data["has_bpl_card"] = True

        # --- 11. Pucca House Ownership (positive & negative) ---
        no_pucca = any(
            p in norm
            for p in [
                "no pucca house", "do not own a pucca house", "don't own a pucca house", "kutcha house", "homeless",
                "पक्का घर नहीं", "पक्का मकान नहीं", "कच्चा घर", "पक्के घर नाही",
                "ਪੱਕਾ ਘਰ ਨਹੀਂ", "ਕੱਚਾ ਘਰ", "પાકું ઘર નથી", "કાચું ઘર",
                "ഉറച്ച വീട് ഇല്ല", "പക്കാ വീട് ഇല്ല", "കുടിൽ",
                "ପକ୍କା ଘର ନାହିଁ", "କଚ୍ଚା ଘର", "پکا گھر نہیں", "کچا گھر",
                "పక్కా ఇల్లు లేదు", "కచ్చా ఇల్లు", "நிரந்தர வீடு இல்லை", "পাকা বাড়ি নেই", "ಪಕ್ಕಾ ಮನೆ ಇಲ್ಲ",
            ]
        )
        has_pucca = any(p in norm for p in [
            "pucca house", "own house", "पक्का घर", "पक्के घर",
            "ਪੱਕਾ ਘਰ", "પાકું ઘર", "പക്കാ വീട്", "ପକ୍କା ଘର", "پکا گھر",
            "పక్కా ఇల్లు", "পাকা বাড়ি", "ಪಕ್ಕಾ ಮನೆ",
        ])
        if no_pucca:
            data["owns_pucca_house"] = False
        elif has_pucca:
            data["owns_pucca_house"] = True

        # --- 12. LPG Connection (positive & negative) ---
        no_lpg = any(
            p in norm
            for p in [
                "no lpg", "without lpg", "no gas connection", "गैस कनेक्शन नहीं", "एलपीजी कनेक्शन नहीं",
                "ਗੈਸ ਕਨੈਕਸ਼ਨ ਨਹੀਂ", "ਐਲਪੀਜੀ ਨਹੀਂ", "ગેસ કનેક્શન નથી", "એલપીજી નથી",
                "ഗ്യാസ് കണക്ഷൻ ഇല്ല", "എൽപിജി ഇല്ല", "ଗ୍ୟାସ୍ ସଂଯୋଗ ନାହିଁ", "ଏଲପିଜି ନାହିଁ",
                "گیس کنکشن نہیں", "ایل پی جی نہیں",
                "గ్యాస్ కనెక్షన్ లేదు", "கேஸ் இணைப்பு இல்லை", "গ্যাস সংযোগ নেই", "ಗ್ಯಾಸ್ ಸಂಪರ್ಕ ಇಲ್ಲ",
            ]
        )
        if no_lpg:
            data["has_lpg_connection"] = False
        elif any(w in norm for w in ["lpg", "gas connection", "गैस कनेक्शन", "ਗੈਸ ਕਨੈਕਸ਼ਨ", "ગેસ કનેક્શન", "ഗ്യാസ് കണക്ഷൻ", "ଗ୍ୟାସ୍ ସଂଯୋଗ", "گیس کنکشن"]):
            data["has_lpg_connection"] = True

        # --- 13. Disability & Percentage ---
        pct_match = re.search(
            r"(\d{1,3})\s*%\s*(?:disability|disabled|दिव्यांग|विकलांग|ਅਪੰਗਤਾ|ਦਿਵਿਆਂਗ|દિવ્યાંગ|വൈകല്യം|ଦିବ୍ୟାଙ୍ଗ|معذوری|వైకల్యం|అంగవైకల్యం|மாற்றுத்திறன்|প্রতিবন্ধী|अपंगत्व|ಅಂಗವೈಕಲ್ಯ)?",
            norm,
        )
        has_dis_kw = any(w in norm for w in [
            "disability", "disabled", "divyang", "दिव्यांग", "विकलांग", "अपंग",
            "ਅਪੰਗਤਾ", "ਦਿਵਿਆਂਗ", "દિવ્યાંગ", "વિકલાંગ", "ഭിന്നശേഷി", "വൈകല്യം", "ଦିବ୍ୟାଙ୍ଗ", "ଭିନ୍ନକ୍ଷମ", "معذور", "معذوری",
            "వైకల్యం", "అంగవైకల్యం", "மாற்றுத்திறனாளி", "প্রতিবন্ধী", "ಅಂಗವೈಕಲ್ಯ",
        ])
        if has_dis_kw:
            data["has_disability"] = True
            if pct_match:
                pct = int(pct_match.group(1))
                if 1 <= pct <= 100:
                    data["disability_percentage"] = pct

        # --- 14. Girl Child Under 10 ---
        girl_match = re.search(
            r"(\d{1,2})\s*-?\s*(?:year|yr|साल|वर्ष|ਸਾਲ|વર્ષ|വയസ്സ്|ବର୍ଷ|سالہ|سال|ఏళ్ల)\s*(?:-?\s*old|की|ਦੀ|ની|की|ର|کی)?\s*(?:girl child|daughter|बेटी|ਧੀ|ਬੇਟੀ|દીકરી|മകൾ|ଝିଅ|بیٹی|لڑکی)",
            norm,
        )
        if girl_match and int(girl_match.group(1)) < 10:
            data["has_girl_child_under_10"] = True
        elif any(w in norm for w in ["girl child under 10", "daughter under 10", "10 साल से कम बेटी", "बेटी", "ਧੀ", "દીકરી", "മകൾ", "ଝିଅ", "بیٹی"]):
            if any(w in norm for w in ["under 10", "below 10", "कम", "ਘੱਟ", "ઓછી", "താഴെ", "କମ୍", "کم"]):
                data["has_girl_child_under_10"] = True

        # --- 15. Merge Explicit Interactive UI Overrides (highest precedence) ---
        if overrides:
            for k, v in overrides.items():
                if v is not None and k in CitizenProfile.model_fields:
                    data[k] = v

        return CitizenProfile.model_validate(data)

