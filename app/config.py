"""
CIHIP Configuration & Constants
Centralized Indian Healthcare Information Portal - Phase 1
ABDM / FHIR R4 / DISHA / DPDPA Compliant System
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Automatically load .env file if present in project root
_env_file = BASE_DIR / ".env"
if _env_file.is_file():
    try:
        with open(_env_file, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    _k = _k.strip()
                    _v = _v.strip().strip("'\"")
                    if _k and _k not in os.environ:
                        os.environ[_k] = _v
    except Exception:
        pass

DB_PATH = os.environ.get("CIHIP_DB_PATH", str(BASE_DIR / "cihip.db"))
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
PORT = int(os.environ.get("PORT", os.environ.get("CIHIP_PORT", "8080")))
HOST = os.environ.get("CIHIP_HOST", "0.0.0.0")

PORTAL_NAME = "Centralized Indian Healthcare Information Portal (CIHIP)"
PORTAL_TAGLINE = "National Federated Health Information Exchange — Phase 1"
VERSION = "1.0.0 (ABDM IG v6.5.0 / FHIR R4.0.1)"
GOVT_AGENCY = "Ministry of Health & Family Welfare (MoHFW) | National Health Authority (NHA)"

# Security & Compliance Constants
SECRET_KEY = os.environ.get("CIHIP_SECRET_KEY", "cihip-sec-pki-hmac-sha256-gov-india-2026")
K_ANONYMITY_THRESHOLD = 50
DIFF_PRIVACY_NOISE_SCALE = 0.5
SESSION_COOKIE_NAME = "cihip_session"
SESSION_EXPIRY_SECONDS = 86400  # 24 hours

# SMTP Outbound Email Gateway Configuration (Live Email Dispatch)
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", os.environ.get("SMTP_USER", "noreply@cihip.gov.in"))
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

# Supported Languages
LANGUAGES = {
    "en": "English",
    "hi": "हिंदी (Hindi)",
    "bn": "বাংলা (Bengali)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "mr": "मराठी (Marathi)",
}

# Multilingual UI Dictionary
TRANSLATIONS = {
    "en": {
        "portal_title": "National Healthcare Exchange",
        "home": "Home",
        "patient_portal": "Patient Portal",
        "doctor_dashboard": "Doctor Dashboard",
        "lab_worklist": "Lab Worklist",
        "hospital_admin": "Hospital Admin",
        "research_analytics": "Research & Analytics",
        "system_security": "Zero-Trust & Audit",
        "api_docs": "FHIR R4 APIs",
        "switch_role": "Switch Role",
        "emergency_break_glass": "Emergency Break-Glass",
        "logout": "Logout",
        "login": "Login",
        "search_patient": "Search Patient (UPK/ABHA)",
        "lhr_timeline": "Longitudinal Health Record",
        "prescriptions": "E-Prescriptions",
        "lab_reports": "Diagnostic Reports",
        "consent_manager": "Consent Manager",
        "order_test": "Order Diagnostic Test",
        "create_prescription": "Issue E-Prescription",
        "verified_by_nhc": "Verified by National Health Authority (NHA)",
    },
    "hi": {
        "portal_title": "राष्ट्रीय स्वास्थ्य विनिमय पोर्टल",
        "home": "मुख्य पृष्ठ",
        "patient_portal": "रोगी पोर्टल",
        "doctor_dashboard": "चिकित्सक डैशबोर्ड",
        "lab_worklist": "प्रयोगशाला कार्यसूची",
        "hospital_admin": "अस्पताल प्रशासन",
        "research_analytics": "अनुसंधान व डेटा विश्लेषण",
        "system_security": "जीरो-ट्रस्ट व ऑडिट लॉग",
        "api_docs": "FHIR R4 एपीआई",
        "switch_role": "भूमिका बदलें",
        "emergency_break_glass": "आपातकालीन ब्रेक-ग्लास एक्सेस",
        "logout": "लॉग आउट",
        "login": "लॉग इन",
        "search_patient": "रोगी खोजें (UPK/ABHA)",
        "lhr_timeline": "दीर्घकालिक स्वास्थ्य रिकॉर्ड (LHR)",
        "prescriptions": "डिजिटल नुस्खे (ई-प्रिस्क्रिप्शन)",
        "lab_reports": "जांच रिपोर्ट",
        "consent_manager": "सहमति प्रबंधक (Consent)",
        "order_test": "जांच का आदेश दें",
        "create_prescription": "ई-प्रिस्क्रिप्शन जारी करें",
        "verified_by_nhc": "राष्ट्रीय स्वास्थ्य प्राधिकरण (NHA) द्वारा सत्यापित",
    },
    "bn": {
        "portal_title": "জাতীয় স্বাস্থ্য বিনিময় পোর্টাল",
        "home": "হোম",
        "patient_portal": "রোগী পোর্টাল",
        "doctor_dashboard": "চিকিৎসক ড্যাশবোর্ড",
        "lab_worklist": "ল্যাব কার্যতালিকা",
        "hospital_admin": "হাসপাতাল প্রশাসন",
        "research_analytics": "গবেষণা ও বিশ্লেষণ",
        "system_security": "জিরো-ট্রাস্ট ও অডিট",
        "api_docs": "FHIR R4 এপিআই",
        "switch_role": "ভূমিকা পরিবর্তন",
        "emergency_break_glass": "জরুরী অ্যাক্সেস (Break-Glass)",
        "logout": "লগআউট",
        "login": "লগইন",
        "search_patient": "রোগী অনুসন্ধান (UPK/ABHA)",
        "lhr_timeline": "স্বাস্থ্য রেকর্ড ইতিহাস",
        "prescriptions": "ই-প্রেসক্রিপশন",
        "lab_reports": "পরীক্ষার রিপোর্ট",
        "consent_manager": "সম্মতি ব্যবস্থাপনা",
        "order_test": "টেস্টের নির্দেশ দিন",
        "create_prescription": "প্রেসক্রিপশন দিন",
        "verified_by_nhc": "জাতীয় স্বাস্থ্য কর্তৃপক্ষ দ্বারা যাচাইকৃত",
    },
    "ta": {
        "portal_title": "தேசிய சுகாதார தகவல் தளம்",
        "home": "முகப்பு",
        "patient_portal": "நோயாளி போர்டல்",
        "doctor_dashboard": "மருத்துவர் பலகை",
        "lab_worklist": "ஆய்வக பணிப்பட்டியல்",
        "hospital_admin": "மருத்துவமனை நிர்வாகம்",
        "research_analytics": "ஆராய்ச்சி & பகுப்பாய்வு",
        "system_security": "பூஜ்ஜிய-நம்பிக்கை & தணிக்கை",
        "api_docs": "FHIR R4 ஏபிஐ",
        "switch_role": "பங்கை மாற்றவும்",
        "emergency_break_glass": "அவசர அணுகல்",
        "logout": "வெளியேறு",
        "login": "உள்நுழைக",
        "search_patient": "நோயாளி தேடல் (UPK/ABHA)",
        "lhr_timeline": "நீண்டகால சுகாதார பதிவு",
        "prescriptions": "மருந்துச் சீட்டுகள்",
        "lab_reports": "ஆய்வக அறிக்கைகள்",
        "consent_manager": "ஒப்புதல் மேலாளர்",
        "order_test": "பரிசோதனை கட்டளையிடு",
        "create_prescription": "மருந்துச் சீட்டு உருவாக்கு",
        "verified_by_nhc": "தேசிய சுகாதார ஆணையத்தால் சரிபார்க்கப்பட்டது",
    },
    "te": {
        "portal_title": "జాతీయ ఆరోగ్య సమాచార పోర్టల్",
        "home": "హోమ్",
        "patient_portal": "రోగి పోర్టల్",
        "doctor_dashboard": "వైద్యుల డాష్‌బోర్డ్",
        "lab_worklist": "ల్యాబ్ జాబితా",
        "hospital_admin": "ఆసుపత్రి అడ్మిన్",
        "research_analytics": "పరిశోధన & విశ్లేషణ",
        "system_security": "జీరో-ట్రస్ట్ & ఆడిట్",
        "api_docs": "FHIR R4 APIలు",
        "switch_role": "పాత్రను మార్చండి",
        "emergency_break_glass": "అత్యవసర బ్రేక్-గ్లాస్",
        "logout": "లాగౌట్",
        "login": "లాగిన్",
        "search_patient": "రోగి శోధన (UPK/ABHA)",
        "lhr_timeline": "దీర్ఘకాలిక ఆరోగ్య రికార్డు",
        "prescriptions": "ఈ-ప్రిస్క్రిప్షన్లు",
        "lab_reports": "ల్యాబ్ నివేదికలు",
        "consent_manager": "సమ్మతి మేనేజర్",
        "order_test": "పరీక్షను ఆర్డర్ చేయండి",
        "create_prescription": "ప్రిస్క్రిప్షన్ జారీ చేయండి",
        "verified_by_nhc": "జాతీయ ఆరోగ్య ప్రాధికార సంస్థ ద్వారా ధృవీకరించబడింది",
    },
    "mr": {
        "portal_title": "राष्ट्रीय आरोग्य विनिमय पोर्टल",
        "home": "मुख्य पृष्ठ",
        "patient_portal": "रुग्ण पोर्टल",
        "doctor_dashboard": "डॉक्टर डॅशबोर्ड",
        "lab_worklist": "प्रयोगशाळा कार्यसूची",
        "hospital_admin": "रुग्णालय प्रशासन",
        "research_analytics": "संशोधन आणि विश्लेषण",
        "system_security": "झिरो-ट्रस्ट आणि ऑडिट",
        "api_docs": "FHIR R4 API",
        "switch_role": "भूमिका बदला",
        "emergency_break_glass": "आपत्कालीन प्रवेश",
        "logout": "लॉग आउट",
        "login": "लॉग इन",
        "search_patient": "रुग्ण शोधा (UPK/ABHA)",
        "lhr_timeline": "दीर्घकालीन आरोग्य नोंदी",
        "prescriptions": "ई-प्रिस्क्रिप्शन",
        "lab_reports": "तपासणी अहवाल",
        "consent_manager": "संमती व्यवस्थापक",
        "order_test": "तपासणी आदेश द्या",
        "create_prescription": "प्रिस्क्रिप्शन तयार करा",
        "verified_by_nhc": "राष्ट्रीय आरोग्य प्राधिकरणाद्वारे सत्यापित",
    }
}
