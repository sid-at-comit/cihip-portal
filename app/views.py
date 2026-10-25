"""
Master Views & Dynamic HTML Component Renderer
Centralized Indian Healthcare Information Portal (CIHIP) - Phase 1
ABDM / FHIR R4 / DISHA / DPDPA Compliant User Interfaces
"""

import json
import html
from typing import Dict, Any, List, Optional
from app.config import (
    PORTAL_NAME, PORTAL_TAGLINE, VERSION, GOVT_AGENCY,
    LANGUAGES, TRANSLATIONS
)
from app.terminology import LOINC_CATALOG, SNOMED_DIAGNOSES, MEDICATIONS_CATALOG

def t(key: str, lang: str = "en") -> str:
    """Retrieve localized string."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

def render_master(
    title: str,
    content: str,
    user: Optional[Dict[str, Any]] = None,
    lang: str = "en",
    active_nav: str = "home",
    flash_message: Optional[str] = None,
    flash_type: str = "success"
) -> str:
    """Generate complete HTML document with master national design layout."""
    
    # Active role badge styling
    role = user.get("role") if user else "GUEST"
    role_badge = {
        "PATIENT": '<span class="badge badge-success">Patient</span>',
        "DOCTOR": '<span class="badge badge-primary">Doctor / Clinician</span>',
        "LAB_TECHNICIAN": '<span class="badge badge-purple">Lab Technician</span>',
        "HOSPITAL_ADMIN": '<span class="badge badge-warning">Hospital Admin</span>',
        "RESEARCHER": '<span class="badge badge-info">Researcher (ICMR)</span>',
        "SYSTEM_ADMIN": '<span class="badge badge-danger">Zero-Trust SecOps</span>',
        "GUEST": '<span class="badge badge-secondary">Guest Citizen</span>'
    }.get(role, '<span class="badge badge-secondary">User</span>')

    # Emergency break glass button (shown for doctors)
    break_glass_html = ""
    if role == "DOCTOR":
        break_glass_html = """
        <a href="/doctor/break-glass-modal" class="btn btn-danger btn-sm" style="font-weight:700;">
            🚨 Break-Glass Emergency
        </a>
        """

    # Flash alert
    flash_html = ""
    if flash_message:
        flash_html = f"""
        <div class="alert-banner alert-{flash_type}">
            <span>{html.escape(flash_message)}</span>
            <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;font-weight:bold;">&times;</button>
        </div>
        """

    # Language options
    lang_options = ""
    for code, label in LANGUAGES.items():
        selected = 'selected' if code == lang else ''
        lang_options += f'<option value="{code}" {selected}>{label}</option>'

    # Navigation items based on role
    nav_items = f"""
    <a href="/" class="nav-item {'active' if active_nav == 'home' else ''}">{t('home', lang)}</a>
    """
    if role == "PATIENT":
        nav_items += f"""
        <a href="/patient" class="nav-item {'active' if active_nav == 'patient' else ''}">{t('patient_portal', lang)}</a>
        <a href="/patient/lhr" class="nav-item {'active' if active_nav == 'lhr' else ''}">{t('lhr_timeline', lang)}</a>
        <a href="/patient/consents" class="nav-item {'active' if active_nav == 'consent' else ''}">{t('consent_manager', lang)}</a>
        """
    elif role == "DOCTOR":
        nav_items += f"""
        <a href="/doctor" class="nav-item {'active' if active_nav == 'doctor' else ''}">{t('doctor_dashboard', lang)}</a>
        <a href="/doctor/search" class="nav-item {'active' if active_nav == 'search' else ''}">{t('search_patient', lang)}</a>
        """
    elif role in ("LAB_TECHNICIAN", "LAB_ADMIN"):
        nav_items += f"""
        <a href="/lab" class="nav-item {'active' if active_nav == 'lab' else ''}">{t('lab_worklist', lang)}</a>
        """
    elif role == "HOSPITAL_ADMIN":
        nav_items += f"""
        <a href="/hospital" class="nav-item {'active' if active_nav == 'hospital' else ''}">{t('hospital_admin', lang)}</a>
        """
    elif role in ("RESEARCHER", "PUBLIC_HEALTH_ANALYST"):
        nav_items += f"""
        <a href="/research" class="nav-item {'active' if active_nav == 'research' else ''}">{t('research_analytics', lang)}</a>
        """
    elif role in ("SYSTEM_ADMIN", "SECURITY_ADMIN"):
        nav_items += f"""
        <a href="/admin/security" class="nav-item {'active' if active_nav == 'admin' else ''}">{t('system_security', lang)}</a>
        """

    # Public Navigation Links
    if not user:
        nav_items += f"""
        <a href="/signin" class="nav-item {'active' if active_nav in ('signin', 'login') else ''}">🔐 Sign In</a>
        <a href="/signup" class="nav-item {'active' if active_nav in ('signup', 'register') else ''}">📝 Register</a>
        """
    nav_items += f"""
    <a href="/admin/database" class="nav-item {'active' if active_nav == 'database' else ''}">🗄️ Database</a>
    <a href="/api/docs" class="nav-item {'active' if active_nav == 'api' else ''}">{t('api_docs', lang)}</a>
    """

    user_info_html = ""
    if user:
        user_info_html = f"""
        <div style="display:flex; align-items:center; gap:12px;">
            {break_glass_html}
            <div style="text-align:right;">
                <div style="font-weight:700; font-size:0.85rem; color:var(--primary);">{html.escape(user.get('name', 'User'))}</div>
                <div style="font-size:0.75rem;">{role_badge} <span style="color:#64748b; font-family:monospace;">{html.escape(user.get('entity_id', ''))}</span></div>
            </div>
            <a href="/logout" class="btn btn-secondary btn-sm">{t('logout', lang)}</a>
        </div>
        """
    else:
        user_info_html = f"""
        <div style="display:flex; gap:8px;">
            <a href="/signin" class="btn btn-secondary btn-sm">Sign In</a>
            <a href="/signup" class="btn btn-primary btn-sm">Register</a>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - {PORTAL_NAME}</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="national-banner"></div>
    <div class="top-bar">
        <div>🇮🇳 {GOVT_AGENCY} | Ayushman Bharat Digital Mission (ABDM)</div>
        <div style="display:flex; align-items:center; gap:12px;">
            <span>HL7 FHIR R4.0.1</span>
            <span>•</span>
            <span>DISHA / DPDPA 2023 Compliant</span>
            <span>•</span>
            <select id="langSelect" class="lang-select">
                {lang_options}
            </select>
        </div>
    </div>

    <header class="main-header">
        <div class="header-container">
            <a href="/" class="brand-section">
                <div class="emblem-icon">⚕</div>
                <div class="brand-text">
                    <h1>CIHIP National Health Exchange</h1>
                    <p>{PORTAL_TAGLINE} — Ver. {VERSION}</p>
                </div>
            </a>

            <nav class="nav-links">
                {nav_items}
            </nav>

            {user_info_html}
        </div>
    </header>

    <main class="main-wrapper">
        {flash_html}
        {content}
    </main>

    <footer>
        <div class="footer-container">
            <div>
                <strong>Centralized Indian Healthcare Information Portal (CIHIP) — Phase 1</strong><br>
                <span>Built for Ministry of Health & Family Welfare (MoHFW) & National Health Authority (NHA)</span><br>
                <small style="color:#64748b;">Compliant with DISHA 2018, DPDPA 2023, HL7 FHIR R4, SNOMED CT, LOINC & NIST SP 800-207 Zero-Trust</small>
            </div>
            <div style="text-align:right;">
                <div>National Emergency Helplines: <strong>112 / 108 / 1075</strong></div>
                <small>National Infrastructure: NIC MeghRaj Multi-Region Cloud</small>
            </div>
        </div>
    </footer>

    <script src="/static/js/app.js"></script>
</body>
</html>
"""

def render_landing_page(stats: Dict[str, Any], lang: str = "en") -> str:
    """Render national landing portal page with system stats, ecosystem architecture and quick links."""
    return f"""
    <!-- Hero Banner -->
    <div class="card" style="background: linear-gradient(135deg, #091a2b 0%, #0f2942 50%, #173b5e 100%); color:#ffffff; border:none; margin-bottom:28px; padding:36px; box-shadow:var(--shadow-lg);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:28px;">
            <div style="max-width:720px;">
                <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.18); padding:5px 14px; border-radius:9999px; margin-bottom:16px;">
                    <span style="font-size:0.78rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#93c5fd;">Government of India • ABDM & FHIR R4 Compliant</span>
                </div>
                <h1 style="font-size:2.2rem; font-weight:800; line-height:1.2; letter-spacing:-0.03em; margin-bottom:12px;">
                    Centralized Indian Healthcare Information Portal
                </h1>
                <p style="font-size:1.02rem; color:#cbd5e1; line-height:1.6; margin-bottom:24px;">
                    National federated health data exchange securely interconnecting citizens, healthcare facilities, diagnostic laboratories, and clinicians across India through <strong>Unique Patient Keys (UPK)</strong> and <strong>Unique Doctor Keys (UDK)</strong> with full patient consent governance and blockchain-grade auditability.
                </p>
                <div style="display:flex; gap:12px; flex-wrap:wrap; align-items:center;">
                    <a href="/signin" class="btn btn-primary" style="background:#ea580c; color:#ffffff; font-weight:700; padding:10px 22px; box-shadow:0 2px 4px rgba(234,88,12,0.3);">Sign In to Portal</a>
                    <a href="/signup" class="btn btn-secondary" style="background:rgba(255,255,255,0.12); color:#ffffff; border-color:rgba(255,255,255,0.25); font-weight:700; padding:10px 22px;">Register New Account</a>
                    <a href="/api/docs" class="btn btn-secondary" style="background:rgba(255,255,255,0.08); color:#93c5fd; border-color:rgba(255,255,255,0.18); font-weight:600; padding:10px 18px;">FHIR R4 APIs</a>
                </div>
            </div>
            <div style="background:rgba(255,255,255,0.06); padding:24px; border-radius:14px; border:1px solid rgba(255,255,255,0.12); min-width:300px; backdrop-filter:blur(8px);">
                <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#93c5fd; margin-bottom:8px;">Exchange Network Status</div>
                <div style="font-size:1.5rem; font-weight:800; color:#34d399; display:flex; align-items:center; gap:8px;">
                    <span style="font-size:1rem;">●</span> 99.99% Operational
                </div>
                <div style="margin-top:14px; font-size:0.82rem; color:#cbd5e1; line-height:1.7;">
                    <div>✓ ABDM Implementation Guide: <strong>v6.5.0</strong></div>
                    <div>✓ Semantic Standard: <strong>HL7 FHIR R4.0.1</strong></div>
                    <div>✓ Cryptographic Audit Trail: <strong style="color:#fde047;">VERIFIED INTACT</strong></div>
                    <div>✓ Transport Security: <strong>TLS 1.3 / AES-256</strong></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Live System Metrics Grid -->
    <div class="grid-4" style="margin-bottom:28px;">
        <div class="stat-box">
            <div class="stat-icon" style="background:#e0f2fe; color:#0369a1;">🏥</div>
            <div>
                <div class="stat-val">{stats.get('hospital_count', 4)}</div>
                <div class="stat-label">HFR Hospitals Connected</div>
            </div>
        </div>
        <div class="stat-box">
            <div class="stat-icon" style="background:#f3e8ff; color:#7e22ce;">🔬</div>
            <div>
                <div class="stat-val">{stats.get('lab_count', 3)}</div>
                <div class="stat-label">NABL Accredited Labs</div>
            </div>
        </div>
        <div class="stat-box">
            <div class="stat-icon" style="background:#dcfce7; color:#15803d;">🩺</div>
            <div>
                <div class="stat-val">{stats.get('doctor_count', 4)}</div>
                <div class="stat-label">NMC Registered Clinicians</div>
            </div>
        </div>
        <div class="stat-box">
            <div class="stat-icon" style="background:#fef3c7; color:#b45309;">🔒</div>
            <div>
                <div class="stat-val">{stats.get('audit_count', 0)}</div>
                <div class="stat-label">Audited Exchange Events</div>
            </div>
        </div>
    </div>

    <!-- 6 Role Portals Grid -->
    <div class="card" style="padding:28px;">
        <div class="card-header">
            <div>
                <div class="card-title">🌐 CIHIP Phase 1 Portal Subsystems</div>
                <div style="font-size:0.82rem; color:#64748b; margin-top:3px;">Select your designated healthcare ecosystem workspace to sign in or register:</div>
            </div>
            <span class="badge badge-primary">Zero-Trust Role Based Access</span>
        </div>
        <div class="grid-3">
            <!-- Patient Card -->
            <div style="border:1px solid #e2e8f0; border-top:4px solid #15803d; border-radius:10px; padding:22px; display:flex; flex-direction:column; justify-content:space-between; background:#ffffff; box-shadow:var(--shadow-xs);">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-size:1.6rem;">👤</span>
                        <span class="badge badge-success">Citizen & Patient</span>
                    </div>
                    <h3 style="font-size:1.15rem; font-weight:700; color:var(--primary); margin-bottom:8px;">Patient Health Portal</h3>
                    <p style="font-size:0.86rem; color:#64748b; line-height:1.5; margin-bottom:18px;">
                        Citizens access their Longitudinal Health Record (LHR), download digitally signed prescriptions with verifiable QR codes, and exercise granular consent control per DISHA & ABDM.
                    </p>
                </div>
                <div style="display:flex; gap:8px;">
                    <a href="/signin/patient" class="btn btn-primary btn-sm" style="flex:1;">Sign In →</a>
                    <a href="/signup/patient" class="btn btn-secondary btn-sm">Register</a>
                </div>
            </div>

            <!-- Doctor Card -->
            <div style="border:1px solid #e2e8f0; border-top:4px solid #1d4ed8; border-radius:10px; padding:22px; display:flex; flex-direction:column; justify-content:space-between; background:#ffffff; box-shadow:var(--shadow-xs);">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-size:1.6rem;">🩺</span>
                        <span class="badge badge-primary">Doctor / Specialist</span>
                    </div>
                    <h3 style="font-size:1.15rem; font-weight:700; color:var(--primary); margin-bottom:8px;">Clinical Consultation Desk</h3>
                    <p style="font-size:0.86rem; color:#64748b; line-height:1.5; margin-bottom:18px;">
                        Clinicians search patients by UPK/ABHA, record encounters with SNOMED CT diagnoses, place LOINC diagnostic orders, review lab reports with abnormal flags, and issue PKI-signed e-prescriptions.
                    </p>
                </div>
                <div style="display:flex; gap:8px;">
                    <a href="/signin/doctor" class="btn btn-primary btn-sm" style="flex:1;">Sign In →</a>
                    <a href="/signup/doctor" class="btn btn-secondary btn-sm">Register</a>
                </div>
            </div>

            <!-- Lab Card -->
            <div style="border:1px solid #e2e8f0; border-top:4px solid #7e22ce; border-radius:10px; padding:22px; display:flex; flex-direction:column; justify-content:space-between; background:#ffffff; box-shadow:var(--shadow-xs);">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-size:1.6rem;">🔬</span>
                        <span class="badge badge-purple">Diagnostic Laboratory</span>
                    </div>
                    <h3 style="font-size:1.15rem; font-weight:700; color:var(--primary); margin-bottom:8px;">Lab Worklist & Reporting</h3>
                    <p style="font-size:0.86rem; color:#64748b; line-height:1.5; margin-bottom:18px;">
                        NABL technicians receive routed test orders, input structured observations against universal LOINC reference standards, generate official reports, and handle amendment workflows.
                    </p>
                </div>
                <div style="display:flex; gap:8px;">
                    <a href="/signin/lab" class="btn btn-primary btn-sm" style="flex:1;">Sign In →</a>
                    <a href="/signup/lab" class="btn btn-secondary btn-sm">Register</a>
                </div>
            </div>

            <!-- Hospital Card -->
            <div style="border:1px solid #e2e8f0; border-top:4px solid #d97706; border-radius:10px; padding:22px; display:flex; flex-direction:column; justify-content:space-between; background:#ffffff; box-shadow:var(--shadow-xs);">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-size:1.6rem;">🏥</span>
                        <span class="badge badge-warning">Hospital Administration</span>
                    </div>
                    <h3 style="font-size:1.15rem; font-weight:700; color:var(--primary); margin-bottom:8px;">HFR Facility Management</h3>
                    <p style="font-size:0.86rem; color:#64748b; line-height:1.5; margin-bottom:18px;">
                        Hospital administrators supervise department registrations, verify clinical doctor rosters, review institutional order volumes, and audit facility data access metrics.
                    </p>
                </div>
                <div style="display:flex; gap:8px;">
                    <a href="/signin/hospital" class="btn btn-primary btn-sm" style="flex:1;">Sign In →</a>
                    <a href="/signup/hospital" class="btn btn-secondary btn-sm">Register</a>
                </div>
            </div>

            <!-- Research Card -->
            <div style="border:1px solid #e2e8f0; border-top:4px solid #0284c7; border-radius:10px; padding:22px; display:flex; flex-direction:column; justify-content:space-between; background:#ffffff; box-shadow:var(--shadow-xs);">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-size:1.6rem;">📊</span>
                        <span class="badge badge-info">Public Health & ICMR</span>
                    </div>
                    <h3 style="font-size:1.15rem; font-weight:700; color:var(--primary); margin-bottom:8px;">Research & Epidemiological Lake</h3>
                    <p style="font-size:0.86rem; color:#64748b; line-height:1.5; margin-bottom:18px;">
                        Authorized researchers query de-identified clinical datasets with guaranteed k-anonymity (k &ge; 50), analyze disease incidence trends, and export secure CSV/JSON/FHIR Bundles.
                    </p>
                </div>
                <div style="display:flex; gap:8px;">
                    <a href="/signin/researcher" class="btn btn-primary btn-sm" style="flex:1;">Researcher Sign In →</a>
                </div>
            </div>

            <!-- SecOps Card -->
            <div style="border:1px solid #e2e8f0; border-top:4px solid #dc2626; border-radius:10px; padding:22px; display:flex; flex-direction:column; justify-content:space-between; background:#ffffff; box-shadow:var(--shadow-xs);">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-size:1.6rem;">🛡️</span>
                        <span class="badge badge-danger">SecOps & Governance</span>
                    </div>
                    <h3 style="font-size:1.15rem; font-weight:700; color:var(--primary); margin-bottom:8px;">Zero-Trust & Audit Ledger</h3>
                    <p style="font-size:0.86rem; color:#64748b; line-height:1.5; margin-bottom:18px;">
                        Security administrators monitor real-time Zero-Trust ABAC policy evaluations and verify the cryptographic integrity of the SHA-256 blockchain-style immutable audit chain.
                    </p>
                </div>
                <div style="display:flex; gap:8px;">
                    <a href="/signin/admin" class="btn btn-primary btn-sm" style="flex:1;">SecOps Sign In →</a>
                </div>
            </div>
        </div>
    </div>
    """

def render_patient_dashboard(patient: Dict[str, Any], encounters: List[Dict[str, Any]], reports: List[Dict[str, Any]], prescriptions: List[Dict[str, Any]], consents: List[Dict[str, Any]], lang: str = "en") -> str:
    """Render patient portal home screen with demographic card, active prescriptions, recent reports, and quick LHR link."""
    upk = patient["upk"]
    abha = patient["abha_number"]

    # Recent prescriptions preview
    rx_rows = ""
    for rx in prescriptions[:3]:
        meds = json.loads(rx["medications_json"])
        med_names = ", ".join([m["name"] for m in meds])
        rx_rows += f"""
        <tr>
            <td style="font-family:monospace; font-weight:700; color:var(--primary);">{rx['rx_id']}</td>
            <td style="color:#64748b; font-size:0.84rem;">{rx['issue_time'][:10]}</td>
            <td><strong>{html.escape(med_names)}</strong></td>
            <td><span class="badge badge-success">Digitally Signed</span></td>
            <td>
                <a href="/patient/prescription/{rx['rx_id']}" class="btn btn-secondary btn-sm">View & Print Rx</a>
            </td>
        </tr>
        """
    if not rx_rows:
        rx_rows = '<tr><td colspan="5" style="text-align:center; padding:24px; color:#94a3b8;">No prescriptions on file.</td></tr>'

    # Recent reports preview
    rpt_rows = ""
    for rpt in reports[:3]:
        flag_badge = {
            "Normal": '<span class="badge badge-success">Normal</span>',
            "High": '<span class="badge badge-warning">High</span>',
            "Low": '<span class="badge badge-warning">Low</span>',
            "Critical": '<span class="badge badge-danger">Critical</span>'
        }.get(rpt["abnormal_flag"], '<span class="badge badge-info">Final</span>')

        rpt_rows += f"""
        <tr>
            <td style="font-family:monospace; font-weight:700; color:var(--primary);">{rpt['report_id']}</td>
            <td style="color:#64748b; font-size:0.84rem;">{rpt['report_time'][:10]}</td>
            <td><strong>{html.escape(rpt['test_name'])}</strong> <span style="font-size:0.75rem; color:#64748b;">({rpt['loinc_code']})</span></td>
            <td>{flag_badge}</td>
            <td>
                <a href="/patient/report/{rpt['report_id']}" class="btn btn-secondary btn-sm">View Lab Report</a>
            </td>
        </tr>
        """
    if not rpt_rows:
        rpt_rows = '<tr><td colspan="5" style="text-align:center; padding:24px; color:#94a3b8;">No diagnostic reports on file.</td></tr>'

    initials = patient['name'][0].upper() if patient.get('name') else 'P'

    return f"""
    <!-- Patient Identity & ABHA Health Card -->
    <div class="card" style="padding:28px; border-left:5px solid #059669; background:#ffffff;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:20px;">
            <div style="display:flex; align-items:flex-start; gap:18px;">
                <div style="width:58px; height:58px; border-radius:12px; background:linear-gradient(135deg, #0f2942 0%, #1e4976 100%); color:#ffffff; display:flex; align-items:center; justify-content:center; font-size:1.6rem; font-weight:800; flex-shrink:0; box-shadow:var(--shadow-sm);">
                    {initials}
                </div>
                <div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                        <span class="badge badge-success">ABHA Verified Citizen</span>
                        <span class="badge badge-info">{patient['state']}</span>
                    </div>
                    <h2 style="font-size:1.6rem; font-weight:800; color:var(--primary); margin:0 0 8px;">{patient['name']}</h2>
                    <div style="display:flex; gap:20px; flex-wrap:wrap; font-size:0.86rem; color:#475569;">
                        <div><strong>ABHA ID:</strong> <span style="font-family:monospace; font-weight:700; color:var(--primary);">{abha}</span></div>
                        <div><strong>UPK:</strong> <span style="font-family:monospace; color:#64748b;">{upk}</span></div>
                        <div><strong>DOB:</strong> {patient['dob']} ({patient['gender']})</div>
                        <div><strong>Blood Group:</strong> <span class="badge badge-danger" style="margin-left:4px;">{patient.get('blood_group', 'B+')}</span></div>
                        <div><strong>District:</strong> {patient['district']}</div>
                    </div>
                </div>
            </div>
            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                <a href="/patient/lhr" class="btn btn-primary">Longitudinal Health Record</a>
                <a href="/patient/consents" class="btn btn-secondary">Consent Manager</a>
            </div>
        </div>
    </div>

    <!-- Quick Stats Metric Cards -->
    <div class="grid-4" style="margin-bottom:24px;">
        <div class="stat-box">
            <div class="stat-icon" style="background:#eff6ff; color:#1d4ed8;">🏥</div>
            <div>
                <div class="stat-val">{len(encounters)}</div>
                <div class="stat-label">Hospital Consultations</div>
            </div>
        </div>
        <div class="stat-box">
            <div class="stat-icon" style="background:#faf5ff; color:#7e22ce;">🔬</div>
            <div>
                <div class="stat-val">{len(reports)}</div>
                <div class="stat-label">Diagnostic Reports</div>
            </div>
        </div>
        <div class="stat-box">
            <div class="stat-icon" style="background:#ecfdf5; color:#047857;">💊</div>
            <div>
                <div class="stat-val">{len(prescriptions)}</div>
                <div class="stat-label">Active E-Prescriptions</div>
            </div>
        </div>
        <div class="stat-box">
            <div class="stat-icon" style="background:#fffbeb; color:#b45309;">🔒</div>
            <div>
                <div class="stat-val">{len(consents)}</div>
                <div class="stat-label">Active Consents</div>
            </div>
        </div>
    </div>

    <!-- Active Prescriptions -->
    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">💊 Digitally Signed E-Prescriptions</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Issued under National Medical Commission digital signature standards:</div>
            </div>
            <a href="/patient/lhr?type=prescription" class="btn btn-secondary btn-sm">View All in LHR →</a>
        </div>
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Rx ID</th>
                        <th>Issued Date</th>
                        <th>Prescribed Medications</th>
                        <th>Digital Seal</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rx_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Recent Diagnostic Reports -->
    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">🔬 Recent Diagnostic Laboratory Reports</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Standardized LOINC lab observations from accredited facilities:</div>
            </div>
            <a href="/patient/lhr?type=report" class="btn btn-secondary btn-sm">View All in LHR →</a>
        </div>
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Report ID</th>
                        <th>Date</th>
                        <th>Investigation / Test Name</th>
                        <th>Status / Flag</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rpt_rows}
                </tbody>
            </table>
        </div>
    </div>
    """

def render_lhr_timeline(patient: Dict[str, Any], timeline_items: List[Dict[str, Any]], current_filter: str = "ALL") -> str:
    """Render patient's Longitudinal Health Record (LHR) chronologically across multi-hospital care providers."""
    upk = patient["upk"]

    items_html = ""
    for item in timeline_items:
        t_type = item["type"]
        date = item["date"]
        dot_class = "encounter" if t_type == "ENCOUNTER" else "lab" if t_type == "REPORT" else "rx"
        type_badge = {
            "ENCOUNTER": '<span class="badge badge-info">Hospital Encounter</span>',
            "REPORT": '<span class="badge badge-purple">Diagnostic Report</span>',
            "PRESCRIPTION": '<span class="badge badge-success">E-Prescription</span>'
        }.get(t_type)

        content_body = ""
        if t_type == "ENCOUNTER":
            vitals = json.loads(item["vitals"]) if isinstance(item["vitals"], str) else item["vitals"]
            content_body = f"""
            <div style="font-weight:700; color:var(--primary); font-size:1.05rem;">{item['department']} Consultation — {item['hospital_name']}</div>
            <div style="font-size:0.85rem; color:#475569; margin:4px 0;"><strong>Doctor:</strong> {item['doctor_name']} | <strong>Diagnosis (SNOMED):</strong> {item['diagnosis_name']} ({item['diagnosis_code']})</div>
            <div style="background:#f8fafc; padding:10px; border-radius:6px; margin:8px 0; font-size:0.85rem;">
                <strong>Chief Complaint:</strong> {item['complaint']}<br>
                <strong>Vitals:</strong> BP {vitals.get('bp', 'N/A')}, Pulse {vitals.get('pulse', 'N/A')}, SpO2 {vitals.get('spo2', 'N/A')}, BMI {vitals.get('bmi', 'N/A')}<br>
                <strong>Clinical Notes:</strong> {item.get('notes', 'Routine follow-up.')}
            </div>
            """
        elif t_type == "REPORT":
            flag = item["flag"]
            flag_badge = '<span class="badge badge-danger">CRITICAL</span>' if flag == 'Critical' else f'<span class="badge badge-warning">{flag}</span>' if flag in ('High', 'Low') else '<span class="badge badge-success">Normal</span>'
            content_body = f"""
            <div style="font-weight:700; color:var(--primary); font-size:1.05rem;">{item['test_name']} — {item['lab_name']}</div>
            <div style="font-size:0.85rem; color:#475569; margin:4px 0;"><strong>LOINC:</strong> {item['loinc']} | <strong>Result Flag:</strong> {flag_badge} | <strong>Ordered By:</strong> {item['doctor_name']}</div>
            <div style="font-size:0.85rem; margin-top:6px;"><strong>Interpretation:</strong> {item['interpretation']}</div>
            <div style="margin-top:10px;">
                <a href="/patient/report/{item['id']}" class="btn btn-secondary btn-sm">View Full Lab Report & Observations →</a>
            </div>
            """
        elif t_type == "PRESCRIPTION":
            meds = json.loads(item["medications"])
            med_list = "".join([f"<li><strong>{m['name']}</strong> — {m['dosage']} ({m['frequency']}), Duration: {m['duration']}</li>" for m in meds])
            content_body = f"""
            <div style="font-weight:700; color:var(--primary); font-size:1.05rem;">Prescription Issued — {item['doctor_name']}</div>
            <div style="font-size:0.85rem; color:#475569; margin:4px 0;"><strong>Security Seal:</strong> <span style="font-family:monospace; color:#15803d;">SHA-256 PKI DIGITALLY SIGNED</span></div>
            <ul style="font-size:0.85rem; margin:8px 0 8px 20px; line-height:1.6;">
                {med_list}
            </ul>
            <a href="/patient/prescription/{item['id']}" class="btn btn-secondary btn-sm">View Signed Prescription Sheet →</a>
            """

        items_html += f"""
        <div class="timeline-item">
            <div class="timeline-dot {dot_class}"></div>
            <div class="timeline-content">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    {type_badge}
                    <span style="font-size:0.8rem; color:#64748b; font-weight:600;">{date}</span>
                </div>
                {content_body}
            </div>
        </div>
        """

    if not items_html:
        items_html = '<div style="padding:40px; text-align:center; color:#94a3b8;">No longitudinal health records found matching this filter.</div>'

    return f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:12px;">
        <div>
            <h2 style="color:var(--primary); font-size:1.5rem;">Longitudinal Health Record (LHR)</h2>
            <p style="font-size:0.85rem; color:#64748b;">Chronological aggregation of hospital encounters, diagnostic observations, and e-prescriptions across India.</p>
        </div>
        <div style="display:flex; gap:8px;">
            <a href="/patient/lhr?filter=ALL" class="btn btn-sm {'btn-primary' if current_filter == 'ALL' else 'btn-secondary'}">All Records</a>
            <a href="/patient/lhr?filter=ENCOUNTER" class="btn btn-sm {'btn-primary' if current_filter == 'ENCOUNTER' else 'btn-secondary'}">Encounters</a>
            <a href="/patient/lhr?filter=REPORT" class="btn btn-sm {'btn-primary' if current_filter == 'REPORT' else 'btn-secondary'}">Lab Reports</a>
            <a href="/patient/lhr?filter=PRESCRIPTION" class="btn btn-sm {'btn-primary' if current_filter == 'PRESCRIPTION' else 'btn-secondary'}">Prescriptions</a>
        </div>
    </div>

    <div class="card" style="padding:16px 24px;">
        <div class="timeline">
            {items_html}
        </div>
    </div>
    """

def render_prescription_sheet(rx: Dict[str, Any], patient: Dict[str, Any], doctor: Dict[str, Any], hospital: Dict[str, Any]) -> str:
    """Render official MoHFW / NHA compliant e-prescription printable sheet with QR code & digital seal."""
    meds = json.loads(rx["medications_json"])
    med_rows = ""
    for idx, m in enumerate(meds, 1):
        med_rows += f"""
        <tr>
            <td style="font-weight:700;">{idx}.</td>
            <td>
                <strong>{m['name']}</strong><br>
                <small style="color:#64748b;">SNOMED CT: {m.get('code', '372567009')} | Route: {m.get('route', 'Oral')}</small>
            </td>
            <td><strong>{m['dosage']}</strong></td>
            <td>{m['frequency']}</td>
            <td>{m['duration']}</td>
            <td>{m.get('instructions', '-')}</td>
        </tr>
        """

    return f"""
    <div class="no-print" style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
        <a href="javascript:history.back()" class="btn btn-secondary">← Back</a>
        <button onclick="window.print()" class="btn btn-primary">Print Official PDF</button>
    </div>

    <div class="prescription-sheet">
        <!-- National Emblem Header -->
        <div class="rx-header">
            <div>
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:1.8rem; color:var(--primary);">⚕</span>
                    <div>
                        <h2 style="font-size:1.2rem; color:var(--primary); line-height:1.2;">{hospital['name']}</h2>
                        <div style="font-size:0.75rem; color:#64748b;">HFR ID: {hospital['hfr_id']} | {hospital['district']}, {hospital['state']}</div>
                    </div>
                </div>
                <div style="margin-top:10px;">
                    <div style="font-size:1.05rem; font-weight:700; color:#1e293b;">{doctor['name']}</div>
                    <div style="font-size:0.8rem; color:#475569;">{doctor['qualification']} • Specialty: {doctor['specialty']}</div>
                    <div style="font-size:0.8rem; color:#475569;"><strong>NMC Reg No:</strong> {doctor['nmc_id']} | <strong>UDK:</strong> {doctor['udk']}</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="background:#0b3954; color:#fff; padding:4px 10px; border-radius:4px; font-size:0.75rem; font-weight:700; margin-bottom:6px;">
                    E-PRESCRIPTION (ABDM)
                </div>
                <div style="font-size:0.8rem;"><strong>Rx ID:</strong> {rx['rx_id']}</div>
                <div style="font-size:0.8rem;"><strong>Date:</strong> {rx['issue_time'][:10]}</div>
                <div style="font-size:0.8rem;"><strong>Status:</strong> <span style="color:#15803d; font-weight:700;">ACTIVE</span></div>
            </div>
        </div>

        <!-- Patient Demographics Section -->
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:12px; margin-bottom:20px; display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; font-size:0.85rem;">
            <div><strong>Patient Name:</strong> {patient['name']}</div>
            <div><strong>Age / Gender:</strong> {patient['dob']} ({patient['gender']})</div>
            <div><strong>Blood Group:</strong> {patient.get('blood_group', 'B+')}</div>
            <div><strong>ABHA Number:</strong> <span style="font-family:monospace; font-weight:700;">{patient['abha_number']}</span></div>
            <div><strong>UPK:</strong> <span style="font-family:monospace;">{patient['upk']}</span></div>
            <div><strong>Phone:</strong> {patient.get('phone', '-')}</div>
        </div>

        <div class="rx-symbol">℞</div>

        <!-- Prescribed Medications Table -->
        <table class="data-table" style="margin-bottom:24px;">
            <thead>
                <tr>
                    <th style="width:40px;">#</th>
                    <th>Medicine (Generic & Brand)</th>
                    <th>Strength</th>
                    <th>Frequency</th>
                    <th>Duration</th>
                    <th>Instructions</th>
                </tr>
            </thead>
            <tbody>
                {med_rows}
            </tbody>
        </table>

        <!-- Advice & Instructions -->
        <div style="font-size:0.85rem; color:#475569; margin-bottom:24px; border-top:1px dashed #cbd5e1; padding-top:12px;">
            <strong>General Instructions:</strong> Take medications strictly as scheduled. In case of unexpected allergic reaction, report immediately to the nearest healthcare center. Generic substitution permitted.
        </div>

        <!-- Digital Signature & QR Verification Seal -->
        <div class="digital-signature-box">
            <div style="display:flex; align-items:center; gap:16px;">
                <div data-qr-payload="{rx['qr_payload']}"></div>
                <div>
                    <div style="font-size:0.85rem; font-weight:700; color:#15803d;">✓ DIGITALLY SIGNED PRESCRIPTION (PKCS#11)</div>
                    <div style="font-size:0.75rem; color:#334155; margin-top:2px;">
                        Signed by: <strong>{doctor['name']}</strong> (NMC: {doctor['nmc_id']})<br>
                        Timestamp: {rx['issue_time']}<br>
                        Canonical SHA-256 Digest: <span style="font-family:monospace;">{rx['canonical_hash'][:24]}...</span><br>
                        Digital Seal: <span style="font-family:monospace;">{rx['digital_signature'][:24]}...</span>
                    </div>
                </div>
            </div>
            <div style="text-align:right;">
                <span class="badge badge-success" style="font-size:0.8rem; padding:6px 12px;">TAMPER-EVIDENT</span>
            </div>
        </div>
    </div>
    """

def render_report_detail(rpt: Dict[str, Any], patient: Dict[str, Any], doctor: Dict[str, Any], lab: Dict[str, Any]) -> str:
    """Render full diagnostic laboratory report with structured observations, reference ranges, and flags."""
    results = json.loads(rpt["result_values_json"])
    obs_rows = ""
    for r in results:
        flag = r.get("flag", "Normal")
        flag_badge = {
            "Normal": '<span class="badge badge-success">Normal</span>',
            "High": '<span class="badge badge-warning">High</span>',
            "Low": '<span class="badge badge-warning">Low</span>',
            "Critical": '<span class="badge badge-danger">CRITICAL</span>'
        }.get(flag, '<span class="badge badge-info">Observed</span>')

        obs_rows += f"""
        <tr>
            <td><strong>{r.get('parameter', rpt['test_name'])}</strong></td>
            <td style="font-size:1.05rem; font-weight:700;">{r.get('value')} {r.get('unit')}</td>
            <td>{r.get('ref', rpt['reference_range'])}</td>
            <td>{flag_badge}</td>
        </tr>
        """

    return f"""
    <div style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
        <a href="javascript:history.back()" class="btn btn-secondary">← Back</a>
        <button onclick="window.print()" class="btn btn-primary">Print Official Lab Report</button>
    </div>

    <div class="card" style="border-top:4px solid #7c3aed;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px; border-bottom:1px solid #e2e8f0; padding-bottom:16px;">
            <div>
                <span class="badge badge-purple" style="margin-bottom:6px;">NABL ACCREDITED LABORATORY</span>
                <h2 style="color:var(--primary);">{lab['name']}</h2>
                <div style="font-size:0.8rem; color:#64748b;">NABL Cert No: <strong>{lab['nabl_id']}</strong> | Address: {lab['address']}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.85rem;"><strong>Report ID:</strong> <span style="font-family:monospace;">{rpt['report_id']}</span></div>
                <div style="font-size:0.85rem;"><strong>Order ID:</strong> <span style="font-family:monospace;">{rpt['order_id']}</span></div>
                <div style="font-size:0.85rem;"><strong>Report Date:</strong> {rpt['report_time']}</div>
                <div style="font-size:0.85rem;"><strong>Status:</strong> <span class="badge badge-success">{rpt['status']}</span></div>
            </div>
        </div>

        <div style="background:#f8fafc; border-radius:6px; padding:12px; margin-bottom:20px; display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; font-size:0.85rem;">
            <div><strong>Patient:</strong> {patient['name']}</div>
            <div><strong>ABHA / UPK:</strong> {patient['abha_number']} / {patient['upk']}</div>
            <div><strong>Ordering Clinician:</strong> {doctor['name']} (UDK: {doctor['udk']})</div>
        </div>

        <h3 style="font-size:1.1rem; color:var(--primary); margin-bottom:12px;">Structured Clinical Observations (LOINC: {rpt['loinc_code']})</h3>
        <table class="data-table" style="margin-bottom:20px;">
            <thead>
                <tr>
                    <th>Observation / Parameter</th>
                    <th>Observed Value</th>
                    <th>Biological Reference Interval</th>
                    <th>Interpretation Flag</th>
                </tr>
            </thead>
            <tbody>
                {obs_rows}
            </tbody>
        </table>

        <div style="background:#faf5ff; border:1px solid #e9d5ff; border-radius:6px; padding:12px; margin-bottom:20px;">
            <div style="font-weight:700; color:#6b21a8; font-size:0.9rem; margin-bottom:4px;">Diagnostic Interpretation / Pathologist Remarks:</div>
            <p style="font-size:0.88rem; color:#4c1d95;">{rpt.get('interpretation', 'No significant pathology noted.')}</p>
        </div>

        <div style="border-top:1px dashed #cbd5e1; padding-top:12px; display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; color:#64748b;">
            <div>Verified and authorized by Senior Clinical Biochemist / Pathologist.</div>
            <div style="font-family:monospace;">FHIR Binary (PDF) Attachment: PRESENT</div>
        </div>
    </div>
    """

def render_patient_consents(patient: Dict[str, Any], consents: List[Dict[str, Any]], doctors: List[Dict[str, Any]], labs: List[Dict[str, Any]]) -> str:
    """Render DISHA & ABDM compliant Consent Management Interface."""
    rows = ""
    for c in consents:
        resources = json.loads(c["resources_json"])
        res_badges = " ".join([f'<span class="badge badge-info">{r}</span>' for r in resources])
        
        status_badge = '<span class="badge badge-success">GRANTED</span>' if c["status"] == "GRANTED" else '<span class="badge badge-danger">REVOKED</span>'
        action_btn = ""
        if c["status"] == "GRANTED":
            action_btn = f"""
            <form action="/patient/consents/{c['consent_id']}/revoke" method="POST" style="display:inline;">
                <button type="submit" class="btn btn-danger btn-sm" onclick="return confirm('Are you sure you want to revoke this consent immediately?')">Revoke Consent</button>
            </form>
            """
        else:
            action_btn = '<span style="color:#94a3b8; font-size:0.8rem;">Revoked</span>'

        rows += f"""
        <tr>
            <td style="font-family:monospace; font-weight:700;">{c['consent_id']}</td>
            <td><strong>{c['requester_name']}</strong> ({c['requester_type']})</td>
            <td>{c['purpose']}</td>
            <td>{res_badges}</td>
            <td>{c['valid_from'][:10]} to {c['valid_to'][:10]}</td>
            <td>{status_badge}</td>
            <td>{action_btn}</td>
        </tr>
        """
    if not rows:
        rows = '<tr><td colspan="7" style="text-align:center; color:#94a3b8;">No consent artefacts recorded.</td></tr>'

    # Build options for granting consent
    doc_options = "".join([f'<option value="DOCTOR|{d["udk"]}|{d["name"]}">{d["name"]} ({d["specialty"]})</option>' for d in doctors])
    lab_options = "".join([f'<option value="LAB|{l["lab_id"]}|{l["name"]}">{l["name"]} (NABL)</option>' for l in labs])

    return f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:12px;">
        <div>
            <h2 style="color:var(--primary); font-size:1.5rem;">Patient Consent Manager</h2>
            <p style="font-size:0.85rem; color:#64748b;">DISHA 2018 & ABDM Consent Artefact Framework — You control who accesses your health records.</p>
        </div>
        <button onclick="openModal('grantConsentModal')" class="btn btn-primary">+ Grant New Consent</button>
    </div>

    <div class="card">
        <div class="card-header">
            <div class="card-title">📜 Active & Historic Consent Artefacts</div>
            <span class="badge badge-success">Patient Controlled Access</span>
        </div>
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Consent ID</th>
                        <th>Authorized Requester</th>
                        <th>Permitted Purpose</th>
                        <th>Allowed Health Resources</th>
                        <th>Validity Period</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Grant Consent Modal -->
    <div id="grantConsentModal" class="modal-backdrop">
        <div class="modal-content">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <h3 style="color:var(--primary);">Grant Clinical Consent</h3>
                <button onclick="closeModal('grantConsentModal')" style="background:none;border:none;font-size:1.4rem;cursor:pointer;">&times;</button>
            </div>
            <form action="/patient/consents/grant" method="POST">
                <div class="form-group">
                    <label class="form-label">Select Healthcare Provider / Diagnostic Lab:</label>
                    <select name="requester_payload" class="form-control" required>
                        <optgroup label="Doctors / Specialists">
                            {doc_options}
                        </optgroup>
                        <optgroup label="NABL Diagnostic Laboratories">
                            {lab_options}
                        </optgroup>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Purpose of Sharing:</label>
                    <select name="purpose" class="form-control">
                        <option value="Treatment">Direct Medical Treatment / Consultation</option>
                        <option value="Diagnostic Order Fulfillment">Diagnostic Investigation Fulfillment</option>
                        <option value="Second Opinion">Specialist Second Opinion</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Permitted FHIR Resources:</label>
                    <div style="display:flex; gap:12px; font-size:0.85rem;">
                        <label><input type="checkbox" name="resources" value="DiagnosticReport" checked> Diagnostic Reports</label>
                        <label><input type="checkbox" name="resources" value="MedicationRequest" checked> Prescriptions</label>
                        <label><input type="checkbox" name="resources" value="Encounter" checked> Encounters</label>
                    </div>
                </div>
                <div class="grid-2">
                    <div class="form-group">
                        <label class="form-label">Valid From:</label>
                        <input type="date" name="valid_from" class="form-control" value="2026-10-01" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Valid To:</label>
                        <input type="date" name="valid_to" class="form-control" value="2027-10-01" required>
                    </div>
                </div>
                <div style="text-align:right; margin-top:16px;">
                    <button type="button" onclick="closeModal('grantConsentModal')" class="btn btn-secondary">Cancel</button>
                    <button type="submit" class="btn btn-primary">Authorize & Issue Consent</button>
                </div>
            </form>
        </div>
    </div>
    """

def render_doctor_dashboard(doctor: Dict[str, Any], hospital: Dict[str, Any], recent_encounters: List[Dict[str, Any]], pending_orders: List[Dict[str, Any]], available_reports: List[Dict[str, Any]]) -> str:
    """Render clinical consultation desk with patient quick-search, order triggers, and pending reports."""
    enc_rows = ""
    for e in recent_encounters:
        enc_rows += f"""
        <tr>
            <td style="font-family:monospace; font-weight:700; color:var(--primary);">{e['encounter_id']}</td>
            <td><strong>{e['patient_name']}</strong> <span style="font-size:0.8rem; color:#64748b; font-family:monospace;">({e['upk']})</span></td>
            <td>{e['start_time'][:10]}</td>
            <td><strong>{e['diagnosis_name']}</strong></td>
            <td>
                <a href="/doctor/search?upk={e['upk']}" class="btn btn-secondary btn-sm">Clinical Chart →</a>
            </td>
        </tr>
        """
    if not enc_rows:
        enc_rows = '<tr><td colspan="5" style="text-align:center; color:#94a3b8; padding:24px;">No recent encounters logged.</td></tr>'

    rpt_rows = ""
    for r in available_reports:
        flag = r.get("abnormal_flag", "Normal")
        flag_badge = '<span class="badge badge-danger">CRITICAL</span>' if flag == 'Critical' else f'<span class="badge badge-warning">{flag}</span>' if flag in ('High', 'Low') else '<span class="badge badge-success">Normal</span>'
        rpt_rows += f"""
        <tr>
            <td style="font-family:monospace; font-weight:700; color:var(--primary);">{r['report_id']}</td>
            <td><strong>{r['patient_name']}</strong> <span style="font-size:0.8rem; color:#64748b; font-family:monospace;">({r['upk']})</span></td>
            <td><strong>{r['test_name']}</strong></td>
            <td>{flag_badge}</td>
            <td>
                <a href="/doctor/review-report/{r['report_id']}" class="btn btn-primary btn-sm">Review & Prescribe</a>
            </td>
        </tr>
        """
    if not rpt_rows:
        rpt_rows = '<tr><td colspan="5" style="text-align:center; color:#94a3b8; padding:24px;">No diagnostic reports requiring review.</td></tr>'

    initials = "".join([part[0] for part in doctor['name'].replace("Dr.", "").split() if part])[:2].upper() or "DR"

    return f"""
    <!-- Doctor Identity Card -->
    <div class="card" style="border-left:4px solid var(--primary); padding:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
            <div style="display:flex; align-items:center; gap:18px;">
                <div style="width:58px; height:58px; border-radius:50%; background:var(--primary-subtle); color:var(--primary); display:flex; align-items:center; justify-content:center; font-size:1.35rem; font-weight:800; border:2px solid #bae6fd;">
                    {initials}
                </div>
                <div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                        <span class="badge badge-primary">NMC Verified Practitioner</span>
                        <span class="badge badge-info">{doctor['specialty']}</span>
                    </div>
                    <h2 style="font-size:1.5rem; color:var(--primary); font-weight:800; margin:0;">{doctor['name']}</h2>
                    <div style="display:flex; gap:16px; flex-wrap:wrap; font-size:0.84rem; color:#475569; margin-top:6px;">
                        <div><strong>NMC Reg No:</strong> <span style="font-family:monospace; font-weight:700;">{doctor['nmc_id']}</span></div>
                        <div><strong>UDK:</strong> <span style="font-family:monospace; color:#64748b;">{doctor['udk']}</span></div>
                        <div><strong>Facility:</strong> {hospital['name']}</div>
                    </div>
                </div>
            </div>
            <div style="display:flex; gap:10px;">
                <a href="/doctor/search" class="btn btn-primary">Search Patient Record</a>
            </div>
        </div>
    </div>

    <!-- Clinician Metrics Grid -->
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:24px;">
        <div class="card" style="padding:16px; border-left:4px solid var(--primary);">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Recent Encounters</div>
            <div style="font-size:1.4rem; font-weight:800; color:var(--primary); margin-top:4px;">{len(recent_encounters)}</div>
            <div style="font-size:0.78rem; color:#475569; margin-top:2px;">Logged Consultations</div>
        </div>
        <div class="card" style="padding:16px; border-left:4px solid var(--accent-saffron);">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Reports for Review</div>
            <div style="font-size:1.4rem; font-weight:800; color:var(--accent-saffron); margin-top:4px;">{len(available_reports)}</div>
            <div style="font-size:0.78rem; color:#475569; margin-top:2px;">Awaiting Physician Assessment</div>
        </div>
        <div class="card" style="padding:16px; border-left:4px solid var(--secondary);">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Practice Base</div>
            <div style="font-size:1.15rem; font-weight:800; color:var(--secondary); margin-top:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{hospital['name']}</div>
            <div style="font-size:0.78rem; color:#475569; margin-top:2px;">HFR ID: {hospital['hfr_id']}</div>
        </div>
    </div>

    <!-- Patient Identity Quick Search Widget -->
    <div class="card" style="background:#f8fafc; border:1px solid #e2e8f0; padding:20px; margin-bottom:24px;">
        <div style="font-weight:700; color:var(--primary); font-size:1rem; margin-bottom:6px;">Patient Identity Search</div>
        <div style="font-size:0.84rem; color:#64748b; margin-bottom:12px;">Query by Universal Patient Key (UPK) or 14-digit National ABHA ID to access longitudinal charts.</div>
        <form action="/doctor/search" method="GET" style="display:flex; gap:10px;">
            <input type="text" name="query" class="form-control" placeholder="Enter Patient UPK (e.g. UPK-IND-2026-9041) or 14-digit ABHA Number..." required>
            <button type="submit" class="btn btn-primary" style="min-width:140px;">Search Patient</button>
        </form>
    </div>

    <!-- Reports Requiring Doctor Review -->
    <div class="card" style="margin-bottom:24px;">
        <div class="card-header">
            <div>
                <div class="card-title">Diagnostic Reports Ready for Clinical Review</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">NABL lab observations and diagnostic tests awaiting doctor sign-off:</div>
            </div>
            <span class="badge badge-warning">Action Required</span>
        </div>
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Report ID</th>
                        <th>Patient</th>
                        <th>Investigation</th>
                        <th>Flag</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rpt_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Recent Clinical Consultations -->
    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">Recent Clinical Consultations</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Outpatient encounters logged across departmental specialties:</div>
            </div>
        </div>
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Encounter ID</th>
                        <th>Patient</th>
                        <th>Date</th>
                        <th>SNOMED Diagnosis</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {enc_rows}
                </tbody>
            </table>
        </div>
    </div>
    """

def render_doctor_patient_chart(patient: Dict[str, Any], consent_status: str, encounters: List[Dict[str, Any]], reports: List[Dict[str, Any]], prescriptions: List[Dict[str, Any]], is_break_glass: bool = False) -> str:
    """Render patient clinical chart for doctor with encounter recording, test ordering, and e-prescribing triggers."""
    upk = patient["upk"]

    # Warning banner if consent is required
    banner_html = ""
    if is_break_glass:
        banner_html = """
        <div class="alert-banner alert-danger" style="margin-bottom:20px;">
            <div>
                <strong>EMERGENCY BREAK-GLASS MODE ACTIVE:</strong> Accessing patient health records under DISHA Section 7 emergency provisions. This action is permanently logged to the national cryptographic audit ledger.
            </div>
        </div>
        """
    elif consent_status != "GRANTED":
        banner_html = f"""
        <div class="alert-banner alert-warning" style="margin-bottom:20px;">
            <div>
                <strong>Active Patient Consent Missing:</strong> The patient has not yet explicitly authorized access to historical multi-hospital records. You can still initiate a new clinical encounter, or request emergency break-glass.
                <div style="margin-top:8px;">
                    <a href="/doctor/break-glass-modal?upk={upk}" class="btn btn-danger btn-sm">Activate Emergency Break-Glass</a>
                </div>
            </div>
        </div>
        """

    initials = "".join([part[0] for part in patient['name'].split() if part])[:2].upper() or "PT"

    return f"""
    {banner_html}

    <div class="card" style="border-left:4px solid var(--secondary); padding:24px; margin-bottom:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
            <div style="display:flex; align-items:center; gap:18px;">
                <div style="width:58px; height:58px; border-radius:50%; background:var(--primary-subtle); color:var(--primary); display:flex; align-items:center; justify-content:center; font-size:1.35rem; font-weight:800; border:2px solid #bae6fd;">
                    {initials}
                </div>
                <div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                        <span class="badge badge-success">Patient Identified</span>
                        <span class="badge badge-info">ABHA Linked</span>
                    </div>
                    <h2 style="color:var(--primary); font-size:1.5rem; font-weight:800; margin:0;">{patient['name']}</h2>
                    <div style="font-size:0.84rem; color:#475569; margin-top:6px; display:flex; gap:16px; flex-wrap:wrap;">
                        <div><strong>UPK:</strong> <span style="font-family:monospace; font-weight:700;">{upk}</span></div>
                        <div><strong>ABHA:</strong> <span style="font-family:monospace;">{patient['abha_number']}</span></div>
                        <div><strong>DOB:</strong> {patient['dob']} ({patient['gender']})</div>
                        <div><strong>Blood Group:</strong> {patient.get('blood_group', 'B+')}</div>
                    </div>
                </div>
            </div>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <a href="/doctor/encounter/new?upk={upk}" class="btn btn-primary">+ Record Clinical Encounter</a>
                <a href="/doctor/order/new?upk={upk}" class="btn btn-secondary">Order Diagnostic Test</a>
                <a href="/doctor/prescribe/new?upk={upk}" class="btn btn-success">Issue E-Prescription</a>
            </div>
        </div>
    </div>

    <!-- Patient Longitudinal History Summary -->
    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Previous Consultations ({len(encounters)})</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Documented clinical encounters across facilities:</div>
                </div>
            </div>
            <div style="max-height:340px; overflow-y:auto;">
                {''.join([f'''
                <div style="border-bottom:1px solid #e2e8f0; padding:12px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#64748b;">
                        <span>{e['start_time'][:10]} • {e['department']}</span>
                        <span style="font-weight:600;">{e['hospital_name']}</span>
                    </div>
                    <div style="font-weight:700; color:var(--primary); font-size:0.95rem; margin-top:2px;">{e['diagnosis_name']}</div>
                    <div style="font-size:0.82rem; color:#475569; margin-top:4px;">{e['chief_complaint']}</div>
                </div>
                ''' for e in encounters]) if encounters else '<div style="color:#94a3b8; text-align:center; padding:30px;">No previous encounters.</div>'}
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Diagnostic Reports ({len(reports)})</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Standardized laboratory investigation findings:</div>
                </div>
            </div>
            <div style="max-height:340px; overflow-y:auto;">
                {''.join([f'''
                <div style="border-bottom:1px solid #e2e8f0; padding:12px 0; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:0.8rem; color:#64748b;">{r['report_time'][:10]} • LOINC: {r['loinc_code']}</div>
                        <div style="font-weight:700; color:var(--primary);">{r['test_name']}</div>
                        <div style="font-size:0.8rem; color:#475569; margin-top:2px;">Flag: <strong>{r['abnormal_flag']}</strong></div>
                    </div>
                    <a href="/doctor/review-report/{r['report_id']}" class="btn btn-secondary btn-sm">Review →</a>
                </div>
                ''' for r in reports]) if reports else '<div style="color:#94a3b8; text-align:center; padding:30px;">No diagnostic reports on record.</div>'}
            </div>
        </div>
    </div>
    """

def render_new_encounter_form(patient: Dict[str, Any], doctor: Dict[str, Any]) -> str:
    """Render clinical encounter recording form with vitals and SNOMED CT diagnoses."""
    diag_options = "".join([f'<option value="{d["code"]}|{d["display"]}">{d["display"]} (SNOMED: {d["code"]})</option>' for d in SNOMED_DIAGNOSES.values()])

    return f"""
    <div style="margin-bottom:16px;">
        <a href="/doctor/search?upk={patient['upk']}" class="btn btn-secondary">← Back to Patient Chart</a>
    </div>

    <div class="card">
        <div class="card-header">
            <div class="card-title">📋 Record Clinical Encounter</div>
            <span class="badge badge-primary">{doctor['specialty']} Department</span>
        </div>

        <div style="background:#f8fafc; padding:10px; border-radius:6px; margin-bottom:20px; font-size:0.85rem;">
            <strong>Patient:</strong> {patient['name']} | <strong>UPK:</strong> {patient['upk']} | <strong>ABHA:</strong> {patient['abha_number']}
        </div>

        <form action="/doctor/encounter/save" method="POST">
            <input type="hidden" name="upk" value="{patient['upk']}">

            <div class="form-group">
                <label class="form-label">Chief Complaint & Presenting Symptoms:</label>
                <textarea name="chief_complaint" class="form-control" rows="2" placeholder="e.g. Chest tightness on exertion, intermittent shortness of breath..." required></textarea>
            </div>

            <div class="card-title" style="font-size:1rem; margin:16px 0 10px;">🩺 Vital Signs:</div>
            <div class="grid-4">
                <div class="form-group">
                    <label class="form-label">Blood Pressure (BP):</label>
                    <input type="text" name="bp" class="form-control" placeholder="130/85 mmHg" value="130/85 mmHg">
                </div>
                <div class="form-group">
                    <label class="form-label">Pulse Rate:</label>
                    <input type="text" name="pulse" class="form-control" placeholder="78 bpm" value="78 bpm">
                </div>
                <div class="form-group">
                    <label class="form-label">Oxygen Saturation (SpO2):</label>
                    <input type="text" name="spo2" class="form-control" placeholder="98%" value="98%">
                </div>
                <div class="form-group">
                    <label class="form-label">BMI / Temp:</label>
                    <input type="text" name="bmi" class="form-control" placeholder="25.2 kg/m²" value="25.2">
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Clinical Diagnosis (SNOMED CT Coded):</label>
                <select name="diagnosis_payload" class="form-control" required>
                    {diag_options}
                </select>
            </div>

            <div class="form-group">
                <label class="form-label">Clinical Notes & Treatment Plan:</label>
                <textarea name="clinical_notes" class="form-control" rows="3" placeholder="Advised low-salt diet, lipid panel investigation, and cardio follow-up in 4 weeks."></textarea>
            </div>

            <div class="form-group">
                <label class="form-label">Documented Allergies:</label>
                <input type="text" name="allergies" class="form-control" placeholder="e.g. Penicillin, NSAIDs (or None)" value="None">
            </div>

            <div style="text-align:right; margin-top:20px;">
                <button type="submit" class="btn btn-primary">Save Encounter & Update LHR</button>
            </div>
        </form>
    </div>
    """

def render_order_test_form(patient: Dict[str, Any], doctor: Dict[str, Any], labs: List[Dict[str, Any]]) -> str:
    """Render diagnostic test order form with LOINC catalog and priority routing."""
    loinc_options = "".join([f'<option value="{item["code"]}|{item["display"]}">{item["display"]} (LOINC: {item["code"]}) - {item["department"]}</option>' for item in LOINC_CATALOG.values()])
    lab_options = "".join([f'<option value="{l["lab_id"]}">{l["name"]} (NABL: {l["nabl_id"]})</option>' for l in labs])

    return f"""
    <div style="margin-bottom:16px;">
        <a href="/doctor/search?upk={patient['upk']}" class="btn btn-secondary">← Back to Patient Chart</a>
    </div>

    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">Order Diagnostic Investigation (FHIR ServiceRequest)</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">NRCeS LOINC Catalog routing to accredited diagnostic pathology:</div>
            </div>
            <span class="badge badge-purple">NRCeS LOINC Catalog</span>
        </div>

        <form action="/doctor/order/save" method="POST">
            <input type="hidden" name="upk" value="{patient['upk']}">

            <div class="form-group">
                <label class="form-label">Select Standardized Laboratory Test (LOINC):</label>
                <select name="test_payload" class="form-control" required>
                    {loinc_options}
                </select>
            </div>

            <div class="grid-2">
                <div class="form-group">
                    <label class="form-label">Priority Level:</label>
                    <select name="priority" class="form-control">
                        <option value="Routine">Routine</option>
                        <option value="Urgent">Urgent</option>
                        <option value="STAT">STAT (Emergency)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Route to Accredited NABL Laboratory:</label>
                    <select name="lab_id" class="form-control" required>
                        {lab_options}
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Clinical Indication / Diagnostic Hypothesis:</label>
                <input type="text" name="indication" class="form-control" placeholder="e.g. Unexplained fatigue, hyperlipidemia screening, glycemic monitoring" required>
            </div>

            <div style="text-align:right; margin-top:20px;">
                <button type="submit" class="btn btn-primary">Transmit Order to Laboratory Queue →</button>
            </div>
        </form>
    </div>
    """

def render_prescribe_form(patient: Dict[str, Any], doctor: Dict[str, Any]) -> str:
    """Render e-Prescription formulation screen with SNOMED CT medications & digital signature signing."""
    med_options = "".join([f'<option value="{m["code"]}|{m["display"]}|{m["default_dosage"]}|{m["default_frequency"]}|{m["route"]}|{m["duration"]}">{m["display"]} ({m["indication"]})</option>' for m in MEDICATIONS_CATALOG.values()])

    return f"""
    <div style="margin-bottom:16px;">
        <a href="/doctor/search?upk={patient['upk']}" class="btn btn-secondary">← Back to Patient Chart</a>
    </div>

    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">Formulate & Digitally Sign E-Prescription</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">National Medical Commission PKI Digital Signature Standard:</div>
            </div>
            <span class="badge badge-success">PKCS#11 / Aadhaar eSign PKI</span>
        </div>

        <form action="/doctor/prescribe/save" method="POST">
            <input type="hidden" name="upk" value="{patient['upk']}">

            <div class="form-group">
                <label class="form-label">Select Primary Formulation (National Formulary / SNOMED CT):</label>
                <select name="med_payload_1" class="form-control" required>
                    {med_options}
                </select>
            </div>

            <div class="grid-3">
                <div class="form-group">
                    <label class="form-label">Dosage:</label>
                    <input type="text" name="dosage_1" class="form-control" value="1 tablet" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Frequency:</label>
                    <input type="text" name="frequency_1" class="form-control" value="1-0-1 (After food)" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Duration:</label>
                    <input type="text" name="duration_1" class="form-control" value="30 days" required>
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Special Dietary & Medication Instructions:</label>
                <input type="text" name="instructions_1" class="form-control" value="Take with plenty of water. Avoid skipping doses.">
            </div>

            <hr style="border:0; border-top:1px solid #e2e8f0; margin:20px 0;">

            <div class="form-group">
                <label class="form-label">Add Secondary Formulation (Optional):</label>
                <select name="med_payload_2" class="form-control">
                    <option value="">-- None / Single Drug --</option>
                    {med_options}
                </select>
            </div>

            <!-- PKI Digital Signature Authorization Box -->
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:18px; margin:20px 0;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    <div style="font-weight:700; color:#15803d; font-size:0.95rem;">Apply Clinician Digital Cryptographic Signature (PKCS#11)</div>
                </div>
                <p style="font-size:0.85rem; color:#166534; margin-bottom:12px; line-height:1.5;">
                    Under DISHA Section 7 and the IT Act 2000, clicking "Sign & Issue E-Prescription" generates an immutable SHA-256 canonical hash and attaches your verified NMC credentials (<strong>{doctor['nmc_id']}</strong>) to the tamper-evident prescription artifact.
                </p>
                <label style="font-size:0.85rem; font-weight:700; color:#15803d; display:flex; align-items:center; gap:8px;">
                    <input type="checkbox" required checked> I confirm clinical accuracy and authorize digital signature attachment.
                </label>
            </div>

            <div style="text-align:right;">
                <button type="submit" class="btn btn-success" style="font-size:0.95rem; padding:10px 24px; font-weight:700;">
                    Sign & Issue Digitally Signed E-Prescription
                </button>
            </div>
        </form>
    </div>
    """

def render_doctor_review_report(report: Dict[str, Any], patient: Dict[str, Any], history_observations: List[Dict[str, Any]]) -> str:
    """Render doctor's report review screen with abnormal flags and historical comparisons."""
    results = json.loads(report["result_values_json"])
    flag = report["abnormal_flag"]
    flag_badge = '<span class="badge badge-danger">CRITICAL</span>' if flag == 'Critical' else f'<span class="badge badge-warning">{flag}</span>' if flag in ('High', 'Low') else '<span class="badge badge-success">Normal</span>'

    # Build historical trend comparison
    hist_rows = ""
    for h in history_observations:
        hist_rows += f"""
        <tr>
            <td>{h['date'][:10]}</td>
            <td><strong>{h['value']} {h['unit']}</strong></td>
            <td>{h['ref']}</td>
            <td><span class="badge badge-{ 'danger' if h['flag'] == 'Critical' else 'warning' if h['flag'] in ('High', 'Low') else 'success'}">{h['flag']}</span></td>
        </tr>
        """

    return f"""
    <div style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
        <a href="/doctor" class="btn btn-secondary">← Back to Dashboard</a>
        <a href="/doctor/prescribe/new?upk={patient['upk']}" class="btn btn-primary">Formulate E-Prescription for Patient →</a>
    </div>

    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">Clinical Diagnostic Review: {report['test_name']}</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Standardized laboratory investigation findings:</div>
            </div>
            <div>{flag_badge}</div>
        </div>

        <div style="background:#f8fafc; padding:12px; border-radius:6px; margin-bottom:20px; font-size:0.85rem;">
            <strong>Patient:</strong> {patient['name']} | <strong>UPK:</strong> {patient['upk']} | <strong>ABHA:</strong> {patient['abha_number']} | <strong>LOINC:</strong> {report['loinc_code']}
        </div>

        <h3 style="font-size:1.05rem; color:var(--primary); margin-bottom:10px;">Current Observation Values:</h3>
        <table class="data-table" style="margin-bottom:20px;">
            <thead>
                <tr>
                    <th>Observation</th>
                    <th>Measured Result</th>
                    <th>Reference Range</th>
                    <th>Interpretation Flag</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td><strong>{r.get('parameter', report['test_name'])}</strong></td><td style='font-size:1.05rem; font-weight:700;'>{r.get('value')} {r.get('unit')}</td><td>{r.get('ref', report['reference_range'])}</td><td>{flag_badge}</td></tr>" for r in results])}
            </tbody>
        </table>

        <div style="background:#f1f5f9; padding:14px; border-radius:8px; margin-bottom:24px;">
            <strong>Lab Pathologist Impression:</strong>
            <p style="font-size:0.88rem; margin-top:4px; color:#334155;">{report.get('interpretation', 'Routine findings.')}</p>
        </div>

        <!-- Historical Trend Graph / Table -->
        <div class="card-title" style="font-size:1.05rem; margin-bottom:10px;">Longitudinal History for this Test ({report['test_name']}):</div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Value</th>
                    <th>Reference Interval</th>
                    <th>Flag</th>
                </tr>
            </thead>
            <tbody>
                {hist_rows if hist_rows else '<tr><td colspan="4" style="text-align:center; color:#94a3b8; padding:20px;">No previous test instances found.</td></tr>'}
            </tbody>
        </table>
    </div>
    """

def render_lab_worklist(lab: Dict[str, Any], pending_orders: List[Dict[str, Any]], completed_reports: List[Dict[str, Any]]) -> str:
    """Render laboratory worklist with order queue, LOINC code filters, and specimen tracking."""
    order_rows = ""
    for o in pending_orders:
        p_badge = '<span class="badge badge-danger">STAT</span>' if o['priority'] == 'STAT' else '<span class="badge badge-warning">Urgent</span>' if o['priority'] == 'Urgent' else '<span class="badge badge-info">Routine</span>'
        order_rows += f"""
        <tr>
            <td style="font-family:monospace; font-weight:700; color:var(--primary);">{o['order_id']}</td>
            <td>{o['order_time'][:10]}</td>
            <td><strong>{o['patient_name']}</strong> <span style="font-size:0.8rem; color:#64748b; font-family:monospace;">({o['upk']})</span></td>
            <td><strong>{o['test_name']}</strong> <span style="font-size:0.8rem; color:#64748b;">({o['loinc_code']})</span></td>
            <td>{o['doctor_name']}</td>
            <td>{p_badge}</td>
            <td><span class="badge badge-secondary">{o['status']}</span></td>
            <td>
                <a href="/lab/entry/{o['order_id']}" class="btn btn-primary btn-sm">Enter Results</a>
            </td>
        </tr>
        """
    if not order_rows:
        order_rows = '<tr><td colspan="8" style="text-align:center; color:#94a3b8; padding:24px;">No pending diagnostic orders in worklist.</td></tr>'

    report_rows = ""
    for r in completed_reports:
        report_rows += f"""
        <tr>
            <td style="font-family:monospace; font-weight:700; color:var(--primary);">{r['report_id']}</td>
            <td>{r['report_time'][:10]}</td>
            <td><strong>{r['patient_name']}</strong></td>
            <td><strong>{r['test_name']}</strong></td>
            <td><span class="badge badge-success">{r['status']}</span></td>
            <td>
                <div style="display:flex; gap:6px;">
                    <a href="/patient/report/{r['report_id']}" class="btn btn-secondary btn-sm">View Report</a>
                    <a href="/lab/amend/{r['report_id']}" class="btn btn-outline btn-sm" style="color:#b91c1c; border-color:#fca5a5;">Amend</a>
                </div>
            </td>
        </tr>
        """
    if not report_rows:
        report_rows = '<tr><td colspan="6" style="text-align:center; color:#94a3b8; padding:24px;">No completed reports today.</td></tr>'

    return f"""
    <!-- Lab Profile Header -->
    <div class="card" style="border-left:4px solid var(--secondary); padding:24px; margin-bottom:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
            <div>
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span class="badge badge-purple">NABL Accredited Worklist</span>
                    <span class="badge badge-success">ABDM Gateway Synchronized</span>
                </div>
                <h2 style="color:var(--primary); font-size:1.5rem; font-weight:800; margin:0;">{lab['name']}</h2>
                <div style="font-size:0.84rem; color:#64748b; margin-top:6px; display:flex; gap:16px; flex-wrap:wrap;">
                    <div><strong>NABL Accreditation:</strong> <span style="font-family:monospace; font-weight:700;">{lab['nabl_id']}</span></div>
                    <div><strong>Expiry:</strong> {lab['accreditation_expiry']}</div>
                    <div><strong>Status:</strong> <span style="color:#15803d; font-weight:700;">Active & Certified</span></div>
                </div>
            </div>
            <div>
                <span class="badge badge-info" style="font-size:0.85rem; padding:6px 14px;">Worklist Status: ONLINE</span>
            </div>
        </div>
    </div>

    <!-- Lab Metrics Grid -->
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:24px;">
        <div class="card" style="padding:16px; border-left:4px solid var(--primary);">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Pending Test Orders</div>
            <div style="font-size:1.4rem; font-weight:800; color:var(--primary); margin-top:4px;">{len(pending_orders)}</div>
            <div style="font-size:0.78rem; color:#475569; margin-top:2px;">Awaiting Specimen / Result Entry</div>
        </div>
        <div class="card" style="padding:16px; border-left:4px solid var(--accent-green);">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Released Reports</div>
            <div style="font-size:1.4rem; font-weight:800; color:var(--accent-green); margin-top:4px;">{len(completed_reports)}</div>
            <div style="font-size:0.78rem; color:#475569; margin-top:2px;">Published to National LHR</div>
        </div>
        <div class="card" style="padding:16px; border-left:4px solid var(--accent-saffron);">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Compliance Standard</div>
            <div style="font-size:1.15rem; font-weight:800; color:var(--accent-saffron); margin-top:4px;">ISO 15189:2022</div>
            <div style="font-size:0.78rem; color:#475569; margin-top:2px;">LOINC Coded Observations</div>
        </div>
    </div>

    <!-- Pending Orders Queue -->
    <div class="card" style="margin-bottom:24px;">
        <div class="card-header">
            <div>
                <div class="card-title">Pending Test Orders Queue ({len(pending_orders)})</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Diagnostic test service requests ordered by verified clinicians:</div>
            </div>
            <input type="text" id="worklistFilter" class="form-control" style="width:240px;" placeholder="Filter by patient/test..." onkeyup="filterTable('worklistFilter', 'ordersTable')">
        </div>
        <div class="table-responsive">
            <table class="data-table" id="ordersTable">
                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>Received Date</th>
                        <th>Patient</th>
                        <th>Investigation (LOINC)</th>
                        <th>Ordering Doctor</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {order_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Recently Released Reports -->
    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">Released Diagnostic Reports (LHR Synchronized)</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Published laboratory investigations available to clinician and citizen:</div>
            </div>
        </div>
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Report ID</th>
                        <th>Report Date</th>
                        <th>Patient</th>
                        <th>Investigation</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {report_rows}
                </tbody>
            </table>
        </div>
    </div>
    """

def render_result_entry_form(order: Dict[str, Any], patient: Dict[str, Any], doctor: Dict[str, Any]) -> str:
    """Render laboratory structured result entry form with dynamic reference ranges and abnormal flags."""
    loinc_meta = LOINC_CATALOG.get(order["loinc_code"], {
        "unit": "units", "low_ref": 0, "high_ref": 100, "critical_low": 0, "critical_high": 200
    })

    return f"""
    <div style="margin-bottom:16px;">
        <a href="/lab" class="btn btn-secondary">← Back to Worklist</a>
    </div>

    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">Structured Laboratory Result Entry</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">LOINC observation capture with real-time interpretation flagging:</div>
            </div>
            <span class="badge badge-purple">{order['test_name']}</span>
        </div>

        <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:14px; border-radius:6px; margin-bottom:20px; font-size:0.85rem; display:grid; grid-template-columns:repeat(3, 1fr); gap:12px;">
            <div><strong>Patient:</strong> {patient['name']} <span style="font-family:monospace; color:#64748b;">({patient['upk']})</span></div>
            <div><strong>Doctor:</strong> {doctor['name']} <span style="font-family:monospace; color:#64748b;">({doctor['udk']})</span></div>
            <div><strong>Clinical Indication:</strong> {order.get('clinical_indication', 'Routine check')}</div>
        </div>

        <form action="/lab/entry/save" method="POST">
            <input type="hidden" name="order_id" value="{order['order_id']}">
            <input type="hidden" name="upk" value="{patient['upk']}">
            <input type="hidden" name="udk" value="{doctor['udk']}">
            <input type="hidden" name="loinc_code" value="{order['loinc_code']}">
            <input type="hidden" name="test_name" value="{order['test_name']}">
            <input type="hidden" id="abnormal_flag_hidden" name="abnormal_flag" value="Normal">

            <div style="display:none;">
                <select id="loinc_code_select">
                    <option value="{order['loinc_code']}" data-low="{loinc_meta['low_ref']}" data-high="{loinc_meta['high_ref']}" data-critlow="{loinc_meta['critical_low']}" data-crithigh="{loinc_meta['critical_high']}">
                        {order['test_name']}
                    </option>
                </select>
            </div>

            <div class="grid-3" style="align-items:flex-end;">
                <div class="form-group">
                    <label class="form-label">Observed Quantitative Value ({loinc_meta['unit']}):</label>
                    <input type="number" step="0.01" id="numeric_result_val" name="result_value" class="form-control" placeholder="e.g. 142.5" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Reference Interval:</label>
                    <input type="text" name="ref_range" class="form-control" value="{loinc_meta['low_ref']} - {loinc_meta['high_ref']} {loinc_meta['unit']}" readonly>
                </div>
                <div class="form-group">
                    <label class="form-label">Real-time Flag Assessment:</label>
                    <div id="auto_flag_display" style="padding:9px 0;">
                        <span class="badge badge-info">Awaiting Input</span>
                    </div>
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Pathologist Clinical Interpretation / Remarks:</label>
                <textarea name="interpretation" class="form-control" rows="3" placeholder="Enter diagnostic observations, methodology, or recommendations..."></textarea>
            </div>

            <div style="background:#eef2ff; border:1px solid #c7d2fe; border-radius:6px; padding:14px; margin-bottom:20px; font-size:0.85rem; color:#3730a3; line-height:1.5;">
                Submitting this form generates a <strong>FHIR DiagnosticReport</strong> with child <strong>Observation</strong> resources, attaches a Base64 PDF document reference, and notifies both the patient and ordering clinician.
            </div>

            <div style="text-align:right;">
                <button type="submit" class="btn btn-primary" style="padding:10px 24px; font-weight:700;">Release & Authorize Diagnostic Report</button>
            </div>
        </form>
    </div>
    """

def render_hospital_portal(hospital: Dict[str, Any], doctors: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    """Render hospital administration dashboard with department stats and verified clinician roster."""
    departments = json.loads(hospital["departments_json"])
    doc_rows = ""
    for d in doctors:
        doc_rows += f"""
        <tr>
            <td style="font-family:monospace; font-weight:700; color:var(--primary);">{d['udk']}</td>
            <td><strong>{d['name']}</strong></td>
            <td>{d['specialty']}</td>
            <td><span style="font-family:monospace;">{d['nmc_id']}</span></td>
            <td><span class="badge badge-success">{d['status']}</span></td>
        </tr>
        """

    return f"""
    <!-- Hospital Facility Profile Header -->
    <div class="card" style="border-left:4px solid var(--accent-saffron); padding:24px; margin-bottom:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
            <div>
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span class="badge badge-warning">HFR Registered Healthcare Facility</span>
                    <span class="badge badge-info">{hospital['tier']} Facility</span>
                </div>
                <h2 style="color:var(--primary); font-size:1.5rem; font-weight:800; margin:0;">{hospital['name']}</h2>
                <div style="font-size:0.84rem; color:#64748b; margin-top:6px; display:flex; gap:16px; flex-wrap:wrap;">
                    <div><strong>HFR Registry ID:</strong> <span style="font-family:monospace; font-weight:700;">{hospital['hfr_id']}</span></div>
                    <div><strong>Location:</strong> {hospital['district']}, {hospital['state']}</div>
                    <div><strong>National Gateway:</strong> <span style="color:#15803d; font-weight:700;">Connected</span></div>
                </div>
            </div>
            <div>
                <span class="badge badge-success" style="font-size:0.85rem; padding:6px 14px;">ABDM Gateway Connected</span>
            </div>
        </div>
    </div>

    <!-- Hospital Key Metrics -->
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:24px;">
        <div class="card" style="padding:16px; border-left:4px solid var(--primary);">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Active NMC Clinicians</div>
            <div style="font-size:1.4rem; font-weight:800; color:var(--primary); margin-top:4px;">{len(doctors)}</div>
            <div style="font-size:0.78rem; color:#475569; margin-top:2px;">Licensed Medical Practitioners</div>
        </div>
        <div class="card" style="padding:16px; border-left:4px solid var(--secondary);">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Clinical Departments</div>
            <div style="font-size:1.4rem; font-weight:800; color:var(--secondary); margin-top:4px;">{len(departments)}</div>
            <div style="font-size:0.78rem; color:#475569; margin-top:2px;">Specialty OPD/IPD Units</div>
        </div>
        <div class="card" style="padding:16px; border-left:4px solid var(--accent-green);">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Outpatient Encounters</div>
            <div style="font-size:1.4rem; font-weight:800; color:var(--accent-green); margin-top:4px;">{stats.get('encounters_count', 0)}</div>
            <div style="font-size:0.78rem; color:#475569; margin-top:2px;">Synchronized to National LHR</div>
        </div>
    </div>

    <!-- Active Doctor Roster -->
    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">Verified Clinician Roster (NMC / HPR Linked)</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Credentialed healthcare professionals registered under National Medical Commission:</div>
            </div>
        </div>
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>UDK</th>
                        <th>Clinician Name</th>
                        <th>Specialty</th>
                        <th>NMC License No</th>
                        <th>HPR Status</th>
                    </tr>
                </thead>
                <tbody>
                    {doc_rows if doc_rows else '<tr><td colspan="5" style="text-align:center; color:#94a3b8; padding:24px;">No clinicians registered.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    """

def render_research_portal(analytics_data: Dict[str, Any], query_params: Dict[str, Any]) -> str:
    """Render public health & epidemiological analytics dashboard with de-identification and k-anonymity guarantee."""
    dept_stats = analytics_data.get("department_counts", {})
    age_stats = analytics_data.get("age_distribution", {})
    disease_stats = analytics_data.get("top_diseases", {})
    k_status = analytics_data.get("k_anonymity_status", "COMPLIANT (k >= 50)")

    return f"""
    <!-- Research Gateway Profile Header -->
    <div class="card" style="border-left:4px solid var(--secondary); padding:24px; margin-bottom:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
            <div>
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span class="badge badge-info">ICMR Epidemiological Research Gateway</span>
                    <span class="badge badge-success">DISHA 2018 & DPDPA 2023 Compliant</span>
                </div>
                <h2 style="color:var(--primary); font-size:1.5rem; font-weight:800; margin:0;">De-Identified Public Health Analytics Lake</h2>
                <div style="font-size:0.84rem; color:#64748b; margin-top:6px;">
                    Privacy Engine: <strong>k-Anonymity &ge; 50 + Differential Privacy</strong> • Zero personally identifiable health information exposed.
                </div>
            </div>
            <div>
                <span class="badge badge-success" style="font-size:0.85rem; padding:6px 14px;">{k_status}</span>
            </div>
        </div>
    </div>

    <!-- Query Builder -->
    <div class="card" style="margin-bottom:24px;">
        <div class="card-header">
            <div>
                <div class="card-title">Cohort Query Filter</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Filter population health aggregates by specialty and geographic territory:</div>
            </div>
        </div>
        <form action="/research" method="GET" class="grid-4" style="align-items:flex-end;">
            <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">Clinical Department:</label>
                <select name="department" class="form-control">
                    <option value="ALL">All Departments</option>
                    <option value="Cardiology">Cardiology</option>
                    <option value="Endocrinology">Endocrinology</option>
                    <option value="Pulmonology">Pulmonology</option>
                    <option value="General Medicine">General Medicine</option>
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">State / Region:</label>
                <select name="state" class="form-control">
                    <option value="ALL">All India (National)</option>
                    <option value="Delhi">Delhi NCT</option>
                    <option value="Tamil Nadu">Tamil Nadu</option>
                    <option value="Maharashtra">Maharashtra</option>
                    <option value="Gujarat">Gujarat</option>
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">Privacy Shield:</label>
                <input type="text" class="form-control" value="k-anonymity (k=50) + Laplace Noise" readonly style="background:#f1f5f9;">
            </div>
            <div>
                <button type="submit" class="btn btn-primary" style="width:100%; font-weight:700;">Run Aggregation Query</button>
            </div>
        </form>
    </div>

    <!-- Export Dataset Actions -->
    <div style="margin-bottom:24px; display:flex; justify-content:flex-end; gap:10px; flex-wrap:wrap;">
        <a href="/api/v1/research/export?format=csv" class="btn btn-secondary">Export CSV</a>
        <a href="/api/v1/research/export?format=json" class="btn btn-secondary">Export JSON</a>
        <a href="/api/v1/research/export?format=fhir" class="btn btn-primary">Export FHIR R4 Bundle</a>
    </div>

    <!-- Charts / Aggregated Stats Grid -->
    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Disease Prevalence by SNOMED CT Concept</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">De-identified clinical condition distribution:</div>
                </div>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Clinical Condition</th>
                        <th>Aggregated Cases</th>
                        <th>National Frequency</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td><strong>{k}</strong></td><td>{v['count']}</td><td><div style='background:#e2e8f0; border-radius:4px; width:100px; height:8px;'><div style='background:var(--secondary); width:{min(100, v['count']*15)}%; height:100%; border-radius:4px;'></div></div></td></tr>" for k, v in disease_stats.items()]) if disease_stats else '<tr><td colspan="3" style="text-align:center; color:#94a3b8; padding:20px;">No data in cohort.</td></tr>'}
                </tbody>
            </table>
        </div>

        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Age Bracket Cohort Distribution</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">10-year demographic age bands:</div>
                </div>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Age Bracket (10-yr Band)</th>
                        <th>Cohort Patient Count</th>
                        <th>Distribution</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td><strong>{k}</strong></td><td>{v}</td><td><div style='background:#e2e8f0; border-radius:4px; width:100px; height:8px;'><div style='background:var(--accent-green); width:{min(100, v*25)}%; height:100%; border-radius:4px;'></div></div></td></tr>" for k, v in age_stats.items()]) if age_stats else '<tr><td colspan="3" style="text-align:center; color:#94a3b8; padding:20px;">No data in cohort.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    """

def render_security_portal(audit_events: List[Dict[str, Any]], integrity_status: Dict[str, Any]) -> str:
    """Render Zero-Trust security monitor and cryptographic immutable audit ledger with hash verification."""
    is_intact = integrity_status.get("is_intact", True)
    status_badge = '<span class="badge badge-success" style="font-size:0.85rem; padding:6px 14px;">LEDGER CHAIN INTACT & VALID</span>' if is_intact else '<span class="badge badge-danger">TAMPER DETECTED</span>'

    audit_rows = ""
    for a in audit_events[:15]:
        outcome_badge = '<span class="badge badge-success">SUCCESS</span>' if a['outcome'] == 'SUCCESS' else '<span class="badge badge-danger">DENIED</span>'
        audit_rows += f"""
        <tr>
            <td style="font-family:monospace; font-size:0.75rem; color:var(--primary); font-weight:700;">{a['audit_id']}</td>
            <td style="font-size:0.8rem; color:#64748b;">{a['timestamp']}</td>
            <td><strong>{a['user_id']}</strong><br><small style="color:#64748b;">Role: {a['role']}</small></td>
            <td><span class="badge badge-primary">{a['action']}</span></td>
            <td>{a['resource_type']}<br><small style="font-family:monospace; color:#64748b;">{a['resource_id']}</small></td>
            <td>{outcome_badge}</td>
            <td style="font-family:monospace; font-size:0.75rem; color:#475569;" title="{a['curr_hash']}">
                <code>{a['curr_hash'][:14]}...</code>
            </td>
        </tr>
        """

    return f"""
    <!-- Security Center Profile Header -->
    <div class="card" style="border-left:4px solid #dc2626; padding:24px; margin-bottom:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
            <div>
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span class="badge badge-danger">NIST SP 800-207 Zero-Trust Architecture</span>
                    <span class="badge badge-info">DISHA Mandated 10-Yr Retention</span>
                </div>
                <h2 style="color:var(--primary); font-size:1.5rem; font-weight:800; margin:0;">Cryptographic Audit Ledger & Security Monitor</h2>
                <div style="font-size:0.84rem; color:#64748b; margin-top:6px;">
                    Immutable SHA-256 Block Chained Audit Trail • All record accesses, prescriptions, and consent actions logged.
                </div>
            </div>
            <div>
                {status_badge}
            </div>
        </div>
    </div>

    <!-- Security Integrity Verification Card -->
    <div class="card" style="background:#f8fafc; border:1px solid #e2e8f0; padding:20px; margin-bottom:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
            <div>
                <div style="font-weight:700; color:var(--primary); font-size:1rem;">Cryptographic Hash Chain Verification</div>
                <div style="font-size:0.84rem; color:#64748b; margin-top:4px;">
                    Total Verified Ledger Blocks: <strong>{integrity_status.get('total_records', 0)}</strong> | Genesis Root: <span style="font-family:monospace;">GENESIS_BLOCK_CIHIP_NHA_2026_MOHFW</span>
                </div>
            </div>
            <form action="/admin/security/verify" method="POST">
                <button type="submit" class="btn btn-primary btn-sm" style="font-weight:700;">Verify Hash Chain Integrity</button>
            </form>
        </div>
    </div>

    <!-- Live Audit Ledger Table -->
    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">Immutable Access & Exchange Ledger</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">10-Year DISHA Mandated Retention for all health data interactions:</div>
            </div>
            <span class="badge badge-info">Zero-Trust Active</span>
        </div>
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Audit ID</th>
                        <th>Timestamp (UTC)</th>
                        <th>Subject (User/Role)</th>
                        <th>Action</th>
                        <th>Target Resource</th>
                        <th>Outcome</th>
                        <th>Block SHA-256 Hash</th>
                    </tr>
                </thead>
                <tbody>
                    {audit_rows}
                </tbody>
            </table>
        </div>
    </div>
    """

def render_api_docs_page() -> str:
    """Render interactive RESTful and FHIR R4 API Explorer."""
    return """
    <div class="card" style="border-left:5px solid #0b3954;">
        <h2 style="color:var(--primary);">CIHIP National FHIR R4 & REST API Catalogue</h2>
        <p style="font-size:0.9rem; color:#64748b; margin-top:4px;">
            Standardized interfaces aligned with <strong>HL7 FHIR Release 4.0.1</strong> and <strong>ABDM Implementation Guide v6.5.0</strong>.
        </p>
    </div>

    <div class="grid-2">
        <!-- FHIR R4 Endpoints -->
        <div class="card">
            <div class="card-title" style="margin-bottom:12px;">🔥 HL7 FHIR R4 Resources (ABDM Profiled)</div>
            <div style="display:flex; flex-direction:column; gap:10px;">
                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/fhir/Patient/UPK-IND-2026-9041" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/fhir/Patient/{upk}</a>
                    </div>
                    <small style="color:#64748b;">Retrieves FHIR Patient resource with ABHA identifier.</small>
                </div>

                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/fhir/Practitioner/UDK-IND-2026-4412" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/fhir/Practitioner/{udk}</a>
                    </div>
                    <small style="color:#64748b;">Retrieves FHIR Practitioner resource with NMC registration.</small>
                </div>

                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/fhir/ServiceRequest/ORD-2026-101" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/fhir/ServiceRequest/{order_id}</a>
                    </div>
                    <small style="color:#64748b;">Retrieves diagnostic test order with LOINC coding.</small>
                </div>

                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/fhir/DiagnosticReport/RPT-2026-501" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/fhir/DiagnosticReport/{report_id}</a>
                    </div>
                    <small style="color:#64748b;">Retrieves structured observations and PDF document reference.</small>
                </div>

                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/fhir/MedicationRequest/RX-2026-801" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/fhir/MedicationRequest/{rx_id}</a>
                    </div>
                    <small style="color:#64748b;">Retrieves digitally signed prescription with SNOMED CT medications.</small>
                </div>

                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/fhir/Consent/CON-2026-001" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/fhir/Consent/{consent_id}</a>
                    </div>
                    <small style="color:#64748b;">Retrieves patient consent artefact per ABDM specifications.</small>
                </div>

                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/fhir/AuditEvent" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/fhir/AuditEvent</a>
                    </div>
                    <small style="color:#64748b;">Retrieves FHIR AuditEvent searchset with cryptographic hash extensions.</small>
                </div>
            </div>
        </div>

        <!-- RESTful JSON Endpoints -->
        <div class="card">
            <div class="card-title" style="margin-bottom:12px;">⚡ Core RESTful Services</div>
            <div style="display:flex; flex-direction:column; gap:10px;">
                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/patients/UPK-IND-2026-9041/timeline" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/patients/{upk}/timeline</a>
                    </div>
                    <small style="color:#64748b;">Complete multi-hospital chronological Longitudinal Health Record (LHR).</small>
                </div>

                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/research/export?format=json" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/research/export?format=json</a>
                    </div>
                    <small style="color:#64748b;">De-identified epidemiological cohort export (k &ge; 50 compliant).</small>
                </div>

                <div style="border:1px solid #e2e8f0; padding:10px; border-radius:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge badge-success">GET</span>
                        <a href="/api/v1/audit/verify" target="_blank" style="font-family:monospace; font-weight:700;">/api/v1/audit/verify</a>
                    </div>
                    <small style="color:#64748b;">Recalculates and validates SHA-256 audit ledger blockchain integrity.</small>
                </div>
            </div>
        </div>
    </div>
    """


def render_login_page(role: str = "PATIENT", error_message: Optional[str] = None, lang: str = "en") -> str:
    """Render comprehensive national login portal with tabs for Patients, Doctors, Labs, and Hospitals."""
    role = role.upper()
    if role not in ("PATIENT", "DOCTOR", "LAB_TECHNICIAN", "HOSPITAL_ADMIN", "RESEARCHER", "SYSTEM_ADMIN"):
        role = "PATIENT"

    err_html = ""
    if error_message:
        err_html = f"""
        <div class="alert-banner alert-danger" style="margin-bottom:20px;">
            <span>⚠️ {html.escape(error_message)}</span>
        </div>
        """

    # Role meta info for active form
    meta = {
        "PATIENT": {
            "title": "Patient & Citizen Login",
            "badge": '<span class="badge badge-success">ABHA / UPK Unified Access</span>',
            "id_label": "ABHA Number (14-digit) or Username / UPK:",
            "id_placeholder": "e.g. 91-4567-8901-2345 or patient_rajesh",
            "redirect_note": "Access your Longitudinal Health Record, e-prescriptions with QR codes, and consent dashboard."
        },
        "DOCTOR": {
            "title": "Clinical Practitioner Login",
            "badge": '<span class="badge badge-primary">NMC / HPR Verified Clinicians</span>',
            "id_label": "NMC Registration Number or Username / UDK:",
            "id_placeholder": "e.g. NMC-MCI-2015-88492 or doctor_priya",
            "redirect_note": "Conduct consultations, record encounters with SNOMED CT, order tests, and issue PKI-signed prescriptions."
        },
        "LAB_TECHNICIAN": {
            "title": "Diagnostic Laboratory Portal",
            "badge": '<span class="badge badge-purple">NABL Accredited Diagnostics</span>',
            "id_label": "NABL Certificate Number or Username / Lab ID:",
            "id_placeholder": "e.g. NABL-MED-2024-9912 or lab_ramesh",
            "redirect_note": "Manage prioritized test queues, input structured LOINC observations, and authorize diagnostic reports."
        },
        "HOSPITAL_ADMIN": {
            "title": "Hospital Facility Administration",
            "badge": '<span class="badge badge-warning">HFR Registered Institutions</span>',
            "id_label": "HFR Facility Registry ID or Username:",
            "id_placeholder": "e.g. HFR-DEL-000101 or admin_aiims",
            "redirect_note": "Supervise clinical departments, verify doctor credentials, and audit facility data exchange metrics."
        },
        "RESEARCHER": {
            "title": "ICMR Epidemiological Research Gateway",
            "badge": '<span class="badge badge-info">De-Identified Public Health Analytics</span>',
            "id_label": "Researcher Registry ID or Username:",
            "id_placeholder": "e.g. ICMR-RES-2026 or researcher_sunita",
            "redirect_note": "Query privacy-preserved cohorts with k-anonymity (k >= 50) and export de-identified FHIR bundles."
        },
        "SYSTEM_ADMIN": {
            "title": "Zero-Trust SecOps Administration",
            "badge": '<span class="badge badge-danger">National Governance & Ledger Audit</span>',
            "id_label": "Security Admin Username / ID:",
            "id_placeholder": "e.g. admin_cihip or CIHIP-HQ-DELHI",
            "redirect_note": "Monitor real-time zero-trust access evaluations and verify SHA-256 blockchain audit ledger integrity."
        }
    }.get(role, {})

    # Tab navigation bar
    tabs = [
        ("PATIENT", "👤 Patient", "/login?role=PATIENT"),
        ("DOCTOR", "🩺 Doctor", "/login?role=DOCTOR"),
        ("LAB_TECHNICIAN", "🔬 Diagnostic Lab", "/login?role=LAB_TECHNICIAN"),
        ("HOSPITAL_ADMIN", "🏥 Hospital Admin", "/login?role=HOSPITAL_ADMIN"),
        ("RESEARCHER", "📊 Researcher", "/login?role=RESEARCHER"),
        ("SYSTEM_ADMIN", "🛡️ SecOps Admin", "/login?role=SYSTEM_ADMIN")
    ]

    tab_links = ""
    for r_code, r_title, r_href in tabs:
        is_active = (r_code == role)
        active_style = "background:var(--primary); color:#ffffff; border-color:var(--primary); font-weight:700;" if is_active else "background:#ffffff; color:#475569; border-color:#cbd5e1;"
        tab_links += f"""
        <a href="{r_href}" class="btn btn-sm" style="{active_style} border-radius:6px; text-decoration:none; padding:8px 14px;">
            {r_title}
        </a>
        """

    return f"""
    <div style="max-width:680px; margin:20px auto;">
        <!-- Role Selector Tabs -->
        <div style="display:flex; gap:6px; flex-wrap:wrap; justify-content:center; margin-bottom:16px;">
            {tab_links}
        </div>

        <div class="card" style="box-shadow:var(--shadow-md); border-top:4px solid var(--primary);">
            <div style="text-align:center; margin-bottom:20px; padding-bottom:16px; border-bottom:1px solid #e2e8f0;">
                <div style="margin-bottom:8px;">{meta['badge']}</div>
                <h2 style="color:var(--primary); font-size:1.6rem; font-weight:800;">{meta['title']}</h2>
                <p style="font-size:0.85rem; color:#64748b; margin-top:4px;">{meta['redirect_note']}</p>
            </div>

            {err_html}

            <form action="/login" method="POST">
                <input type="hidden" name="role" value="{role}">

                <div class="form-group">
                    <label class="form-label">{meta['id_label']}</label>
                    <input type="text" id="login_identifier" name="identifier" class="form-control" placeholder="{meta['id_placeholder']}" required autofocus>
                </div>

                <div class="form-group">
                    <label class="form-label">Password / Secret Key:</label>
                    <input type="password" id="login_password" name="password" class="form-control" placeholder="••••••••" required>
                </div>

                <div style="margin-top:20px;">
                    <button type="submit" class="btn btn-primary" style="width:100%; padding:11px; font-size:0.95rem; font-weight:700;">
                        Secure Sign In →
                    </button>
                </div>
            </form>

            <div style="text-align:center; margin-top:18px; padding-top:14px; border-top:1px dashed #cbd5e1; font-size:0.88rem;">
                New to CIHIP? <a href="/signup?role={role}" style="color:var(--primary); font-weight:700; text-decoration:none;">Register / Sign Up as {role.replace('_', ' ').title()} →</a>
            </div>

            <div style="border-top:1px solid #e2e8f0; margin-top:16px; padding-top:14px; display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:#64748b;">
                <span>🔒 Zero-Trust NIST SP 800-207</span>
                <span>🇮🇳 DISHA 2018 & DPDPA 2023 Compliant</span>
            </div>
        </div>
    </div>
    """


def render_signup_page(role: str = "PATIENT", error_message: Optional[str] = None, lang: str = "en", hospitals: Optional[List[Dict[str, Any]]] = None) -> str:
    """Render comprehensive national onboarding / sign-up portal for Patients, Doctors, Labs, and Hospitals."""
    role = role.upper()
    if role not in ("PATIENT", "DOCTOR", "LAB_TECHNICIAN", "HOSPITAL_ADMIN"):
        role = "PATIENT"

    err_html = ""
    if error_message:
        err_html = f"""
        <div class="alert-banner alert-danger" style="margin-bottom:20px;">
            <span>⚠️ {html.escape(error_message)}</span>
        </div>
        """

    # Role tabs
    tabs = [
        ("PATIENT", "👤 Patient Sign-Up", "/signup?role=PATIENT"),
        ("DOCTOR", "🩺 Doctor Onboarding", "/signup?role=DOCTOR"),
        ("LAB_TECHNICIAN", "🔬 Diagnostic Lab Register", "/signup?role=LAB_TECHNICIAN"),
        ("HOSPITAL_ADMIN", "🏥 Hospital Facility Register", "/signup?role=HOSPITAL_ADMIN")
    ]

    tab_links = ""
    for r_code, r_title, r_href in tabs:
        is_active = (r_code == role)
        active_style = "background:var(--primary); color:#ffffff; border-color:var(--primary); font-weight:700;" if is_active else "background:#ffffff; color:#475569; border-color:#cbd5e1;"
        tab_links += f"""
        <a href="{r_href}" class="btn btn-sm" style="{active_style} border-radius:6px; text-decoration:none; padding:8px 14px;">
            {r_title}
        </a>
        """

    hosp_options = ""
    if hospitals:
        for h in hospitals:
            hosp_options += f'<option value="{h["hospital_id"]}">{h["name"]} ({h["district"]}, {h["state"]})</option>'
    else:
        hosp_options = '<option value="HOSP-AIIMS-DEL">AIIMS New Delhi</option><option value="HOSP-CMC-VEL">CMC Vellore</option>'

    form_fields = ""
    if role == "PATIENT":
        form_fields = f"""
        <div class="form-group">
            <label class="form-label">Citizen / Patient Full Name:</label>
            <input type="text" name="name" class="form-control" placeholder="e.g. Vikram Patel" required>
        </div>
        <div class="form-group">
            <label class="form-label">14-Digit ABHA ID (Ayushman Bharat Health Account):</label>
            <input type="text" id="reg_abha" name="abha_number" class="form-control" placeholder="e.g. 91-9988-7766-5544" required>
        </div>
        <div class="grid-3">
            <div class="form-group">
                <label class="form-label">Date of Birth:</label>
                <input type="date" name="dob" class="form-control" value="1992-05-15" required>
            </div>
            <div class="form-group">
                <label class="form-label">Gender:</label>
                <select name="gender" class="form-control">
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Blood Group:</label>
                <select name="blood_group" class="form-control">
                    <option value="B+">B+</option>
                    <option value="O+">O+</option>
                    <option value="A+">A+</option>
                    <option value="AB+">AB+</option>
                    <option value="B-">B-</option>
                    <option value="O-">O-</option>
                </select>
            </div>
        </div>
        <div class="grid-3">
            <div class="form-group">
                <label class="form-label">State:</label>
                <input type="text" name="state" class="form-control" placeholder="e.g. Maharashtra" value="Delhi" required>
            </div>
            <div class="form-group">
                <label class="form-label">District:</label>
                <input type="text" name="district" class="form-control" placeholder="e.g. Mumbai City" value="South Delhi" required>
            </div>
            <div class="form-group">
                <label class="form-label">Pincode:</label>
                <input type="text" name="pincode" class="form-control" placeholder="110029" value="110029">
            </div>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">Mobile Number:</label>
                <input type="text" name="phone" class="form-control" placeholder="+91 98765 43210" value="+91 98765 00112" required>
            </div>
            <div class="form-group">
                <label class="form-label">Email Address (Optional):</label>
                <input type="email" name="email" class="form-control" placeholder="patient@example.com">
            </div>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">Create Username:</label>
                <input type="text" name="username" class="form-control" placeholder="e.g. vikram_patel" required>
            </div>
            <div class="form-group">
                <label class="form-label">Password:</label>
                <input type="password" name="password" class="form-control" placeholder="Create strong password" required>
            </div>
        </div>
        """
    elif role == "DOCTOR":
        form_fields = f"""
        <div class="form-group">
            <label class="form-label">Doctor's Full Name (with Title):</label>
            <input type="text" name="name" class="form-control" placeholder="e.g. Dr. Meera Nambiar, MD" required>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">National Medical Commission (NMC) License No:</label>
                <input type="text" name="nmc_id" class="form-control" placeholder="e.g. NMC-MCI-2022-77112" required>
            </div>
            <div class="form-group">
                <label class="form-label">Clinical Specialty:</label>
                <select name="specialty" class="form-control">
                    <option value="Cardiology">Cardiology</option>
                    <option value="Pulmonology">Pulmonology</option>
                    <option value="Endocrinology">Endocrinology</option>
                    <option value="Nephrology">Nephrology</option>
                    <option value="General Medicine">General Medicine</option>
                    <option value="Oncology">Oncology</option>
                    <option value="Neurology">Neurology</option>
                    <option value="Gastroenterology">Gastroenterology</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">Primary Hospital / Healthcare Facility Affiliation:</label>
            <select name="hospital_id" class="form-control" required>
                {hosp_options}
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Medical Qualifications:</label>
            <input type="text" name="qualification" class="form-control" placeholder="e.g. MBBS, MD (Medicine), DM (Cardiology)" value="MBBS, MD" required>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">Professional Email:</label>
                <input type="email" name="email" class="form-control" placeholder="doctor@hospital.edu.in" required>
            </div>
            <div class="form-group">
                <label class="form-label">Phone Number:</label>
                <input type="text" name="phone" class="form-control" placeholder="+91 98111 22334" required>
            </div>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">Create Username:</label>
                <input type="text" name="username" class="form-control" placeholder="e.g. dr_meera" required>
            </div>
            <div class="form-group">
                <label class="form-label">Password:</label>
                <input type="password" name="password" class="form-control" placeholder="Create strong password" required>
            </div>
        </div>
        """
    elif role == "LAB_TECHNICIAN":
        form_fields = f"""
        <div class="form-group">
            <label class="form-label">Diagnostic Laboratory Legal Entity Name:</label>
            <input type="text" name="name" class="form-control" placeholder="e.g. Metropolis Clinical Pathology & Genomics" required>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">NABL Accreditation Certificate Number:</label>
                <input type="text" name="nabl_id" class="form-control" placeholder="e.g. NABL-MED-2025-9988" required>
            </div>
            <div class="form-group">
                <label class="form-label">Accreditation Expiry Date:</label>
                <input type="date" name="accreditation_expiry" class="form-control" value="2028-12-31" required>
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">Associated Hospital (Optional / Select Standalone if independent):</label>
            <select name="hospital_id" class="form-control">
                <option value="">-- Independent Standalone Diagnostic Lab --</option>
                {hosp_options}
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Physical Laboratory Address & City:</label>
            <input type="text" name="address" class="form-control" placeholder="e.g. Sector 18, Institutional Area, Noida - 201301" required>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">Lab Contact Phone:</label>
                <input type="text" name="phone" class="form-control" placeholder="+91 98188 00112" required>
            </div>
            <div class="form-group">
                <label class="form-label">Official Lab Email:</label>
                <input type="email" name="email" class="form-control" placeholder="contact@labname.in" required>
            </div>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">Create Username:</label>
                <input type="text" name="username" class="form-control" placeholder="e.g. lab_metropolis" required>
            </div>
            <div class="form-group">
                <label class="form-label">Password:</label>
                <input type="password" name="password" class="form-control" placeholder="Create strong password" required>
            </div>
        </div>
        """
    elif role == "HOSPITAL_ADMIN":
        form_fields = f"""
        <div class="form-group">
            <label class="form-label">Hospital / Healthcare Facility Name:</label>
            <input type="text" name="name" class="form-control" placeholder="e.g. Fortis Memorial Research Institute" required>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">National Health Facility Registry (HFR) ID:</label>
                <input type="text" name="hfr_id" class="form-control" placeholder="e.g. HFR-DEL-000918" required>
            </div>
            <div class="form-group">
                <label class="form-label">Facility Tier:</label>
                <select name="tier" class="form-control">
                    <option value="Tertiary Apex">Tertiary Apex Multi-Specialty</option>
                    <option value="Super Specialty">Super Specialty Care</option>
                    <option value="Secondary Hospital">Secondary Hospital</option>
                    <option value="Primary Health Centre">Primary Health Centre</option>
                </select>
            </div>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">State:</label>
                <input type="text" name="state" class="form-control" placeholder="e.g. Haryana" value="Delhi" required>
            </div>
            <div class="form-group">
                <label class="form-label">District:</label>
                <input type="text" name="district" class="form-control" placeholder="e.g. Gurugram" value="New Delhi" required>
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">Clinical Departments Registered (Hold Ctrl/Cmd to select multiple):</label>
            <select name="departments" class="form-control" multiple style="height:100px;">
                <option value="Cardiology" selected>Cardiology</option>
                <option value="Pulmonology" selected>Pulmonology</option>
                <option value="Endocrinology" selected>Endocrinology</option>
                <option value="General Medicine" selected>General Medicine</option>
                <option value="Nephrology">Nephrology</option>
                <option value="Oncology">Oncology</option>
                <option value="Neurology">Neurology</option>
                <option value="Biochemistry">Biochemistry</option>
            </select>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">Administrator Full Name:</label>
                <input type="text" name="admin_name" class="form-control" placeholder="e.g. Dr. Rajesh Goel (Superintendent)" required>
            </div>
            <div class="form-group">
                <label class="form-label">Admin Email:</label>
                <input type="email" name="email" class="form-control" placeholder="admin@hospital.com" required>
            </div>
        </div>
        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">Create Username:</label>
                <input type="text" name="username" class="form-control" placeholder="e.g. admin_fortis" required>
            </div>
            <div class="form-group">
                <label class="form-label">Password:</label>
                <input type="password" name="password" class="form-control" placeholder="Create strong password" required>
            </div>
        </div>
        """

    btn_label = {
        "PATIENT": "Register Patient & Issue Unique Patient Key (UPK) →",
        "DOCTOR": "Verify Credentials & Issue Unique Doctor Key (UDK) →",
        "LAB_TECHNICIAN": "Register NABL Diagnostic Laboratory →",
        "HOSPITAL_ADMIN": "Register Hospital on National HFR Registry →"
    }.get(role, "Register Entity →")

    return f"""
    <div style="max-width:760px; margin:20px auto;">
        <!-- Role Tabs -->
        <div style="display:flex; gap:6px; flex-wrap:wrap; justify-content:center; margin-bottom:16px;">
            {tab_links}
        </div>

        <div class="card" style="box-shadow:var(--shadow-md); border-top:4px solid var(--accent-green);">
            <div style="text-align:center; margin-bottom:20px; padding-bottom:16px; border-bottom:1px solid #e2e8f0;">
                <span class="badge badge-success" style="margin-bottom:8px;">ABDM National Ecosystem Onboarding</span>
                <h2 style="color:var(--primary); font-size:1.6rem; font-weight:800;">Register as {role.replace('_', ' ').title()}</h2>
                <p style="font-size:0.85rem; color:#64748b; margin-top:4px;">
                    Compliant with Ayushman Bharat Digital Mission (ABDM) and National Health Authority standards.
                </p>
            </div>

            {err_html}

            <form action="/signup" method="POST">
                <input type="hidden" name="role" value="{role}">
                {form_fields}

                <div style="margin-top:24px;">
                    <button type="submit" class="btn btn-success" style="width:100%; padding:12px; font-size:1rem; font-weight:700;">
                        {btn_label}
                    </button>
                </div>
            </form>

            <div style="text-align:center; margin-top:18px; padding-top:14px; border-top:1px dashed #cbd5e1; font-size:0.88rem;">
                Already registered? <a href="/signin?role={role}" style="color:var(--primary); font-weight:700; text-decoration:none;">Sign In here →</a>
            </div>

            <div style="border-top:1px solid #e2e8f0; margin-top:16px; padding-top:14px; display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:#64748b;">
                <span>🇮🇳 National Medical Commission & NABL Verified</span>
                <span>🔒 DISHA 2018 & DPDPA 2023 Compliant</span>
            </div>
        </div>
    </div>
    """

def render_database_explorer(
    db_stats: Dict[str, Any],
    active_table: str,
    table_data: Dict[str, Any],
    query_result: Optional[Dict[str, Any]] = None,
    query_input: str = "",
    lang: str = "en"
) -> str:
    """Render comprehensive Visual Database Explorer & Management Dashboard."""
    engine = db_stats.get("engine", {})
    table_counts = db_stats.get("table_counts", {})
    total_records = db_stats.get("total_records", 0)
    tables = db_stats.get("tables", {})

    # Engine badge styling
    is_pg = engine.get("engine") == "postgresql"
    engine_badge = f"""
    <span class="badge {'badge-primary' if is_pg else 'badge-success'}" style="font-size:0.85rem; padding:6px 12px;">
        {'🐘 Cloud PostgreSQL 16' if is_pg else '🗄️ Embedded SQLite 3 (WAL)'}
    </span>
    """

    # Table chips
    table_icons = {
        "users": "👤",
        "patients": "🏥",
        "doctors": "👨‍⚕️",
        "hospitals": "🏢",
        "labs": "🔬",
        "encounters": "🩺",
        "service_requests": "📋",
        "diagnostic_reports": "🧪",
        "prescriptions": "💊",
        "consents": "📜",
        "audit_events": "🔒",
        "research_queries": "📊"
    }

    chips_html = ""
    for tbl_name, tbl_info in tables.items():
        is_active = tbl_name == active_table
        count = table_counts.get(tbl_name, 0)
        icon = table_icons.get(tbl_name, "📁")
        bg_style = "background:var(--primary); color:#ffffff; border-color:var(--primary);" if is_active else "background:#ffffff; color:var(--text-main); border:1px solid #cbd5e1;"
        badge_bg = "background:rgba(255,255,255,0.25); color:#ffffff;" if is_active else "background:#e2e8f0; color:#475569;"
        chips_html += f"""
        <a href="/admin/database?table={tbl_name}" class="demo-pill" style="{bg_style} padding:6px 14px; text-decoration:none; display:inline-flex; align-items:center; gap:8px;">
            <span>{icon} {tbl_name}</span>
            <span style="font-size:0.75rem; padding:2px 7px; border-radius:10px; {badge_bg} font-weight:700;">{count}</span>
        </a>
        """

    # Active Table Columns & Rows
    cols = table_data.get("columns", [])
    rows = table_data.get("rows", [])
    total_rows = table_data.get("total_rows", 0)
    current_page = table_data.get("current_page", 1)
    total_pages = table_data.get("total_pages", 1)
    pk = table_data.get("primary_key", "")
    desc = table_data.get("description", "")

    # Headers
    th_cells = ""
    for c in cols:
        is_pk = c == pk
        pk_indicator = ' 🔑' if is_pk else ''
        th_cells += f'<th style="white-space:nowrap; {"color:var(--primary); font-weight:700;" if is_pk else ""}">{html.escape(c)}{pk_indicator}</th>'

    # Rows
    tr_cells = ""
    if not rows:
        tr_cells = f'<tr><td colspan="{len(cols)}" style="text-align:center; padding:30px; color:#94a3b8;">No records in table <code>{html.escape(active_table)}</code></td></tr>'
    else:
        for r in rows:
            td_cells = ""
            for c in cols:
                val = r.get(c)
                if val is None:
                    formatted_val = '<span style="color:#94a3b8; font-style:italic;">NULL</span>'
                elif isinstance(val, (dict, list)):
                    s = json.dumps(val)
                    preview = s[:60] + ('...' if len(s) > 60 else '')
                    formatted_val = f'<code style="font-size:0.75rem; background:#f1f5f9; padding:2px 6px; border-radius:4px; color:#0f172a;" title="{html.escape(s)}">{html.escape(preview)}</code>'
                elif str(val) in ("ACTIVE", "VERIFIED", "ACCREDITED", "GRANTED", "FINAL", "COMPLETED", "SUCCESS"):
                    formatted_val = f'<span class="badge badge-success" style="font-size:0.75rem;">{html.escape(str(val))}</span>'
                elif str(val) in ("REVOKED", "SUPERSEDED", "FAILED", "SUSPENDED"):
                    formatted_val = f'<span class="badge badge-danger" style="font-size:0.75rem;">{html.escape(str(val))}</span>'
                elif str(val) in ("SUBMITTED", "PENDING", "AMENDED"):
                    formatted_val = f'<span class="badge badge-warning" style="font-size:0.75rem;">{html.escape(str(val))}</span>'
                elif c in ("upk", "udk", "hospital_id", "lab_id", "order_id", "report_id", "rx_id", "consent_id", "audit_id"):
                    formatted_val = f'<span style="font-family:monospace; font-weight:600; color:var(--primary);">{html.escape(str(val))}</span>'
                elif "hash" in c:
                    short_h = str(val)[:16] + "..." if len(str(val)) > 16 else str(val)
                    formatted_val = f'<code style="font-size:0.72rem; color:#64748b;" title="{html.escape(str(val))}">{html.escape(short_h)}</code>'
                else:
                    s_val = str(val)
                    if len(s_val) > 70:
                        s_val = s_val[:70] + "..."
                    formatted_val = html.escape(s_val)
                td_cells += f'<td style="font-size:0.83rem;">{formatted_val}</td>'
            tr_cells += f'<tr>{td_cells}</tr>'

    # Pagination buttons
    prev_link = f'<a href="/admin/database?table={active_table}&page={current_page - 1}" class="btn btn-secondary btn-sm">← Previous</a>' if current_page > 1 else '<span class="btn btn-secondary btn-sm" style="opacity:0.5; pointer-events:none;">← Previous</span>'
    next_link = f'<a href="/admin/database?table={active_table}&page={current_page + 1}" class="btn btn-secondary btn-sm">Next →</a>' if current_page < total_pages else '<span class="btn btn-secondary btn-sm" style="opacity:0.5; pointer-events:none;">Next →</span>'

    # Query Results Output
    query_box_html = ""
    if query_result:
        if query_result.get("success"):
            q_cols = query_result.get("columns", [])
            q_rows = query_result.get("rows", [])
            q_count = query_result.get("row_count", 0)
            q_time = query_result.get("execution_ms", 0)

            q_th = "".join(f'<th style="white-space:nowrap;">{html.escape(qc)}</th>' for qc in q_cols)
            q_tr = ""
            for qr in q_rows:
                tds = ""
                for qc in q_cols:
                    qv = qr.get(qc)
                    if qv is None:
                        tds += '<td><span style="color:#94a3b8; font-style:italic;">NULL</span></td>'
                    else:
                        tds += f'<td style="font-size:0.83rem;">{html.escape(str(qv)[:80])}</td>'
                q_tr += f'<tr>{tds}</tr>'

            query_box_html = f"""
            <div style="margin-top:20px; border-top:2px solid #e2e8f0; padding-top:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div style="font-weight:700; color:#166534; display:flex; align-items:center; gap:8px;">
                        <span>✅ Query Successful</span>
                        <span class="badge badge-success">{q_count} records</span>
                        <span style="font-size:0.8rem; color:#64748b; font-family:monospace;">Execution time: {q_time} ms</span>
                    </div>
                </div>
                <div style="overflow-x:auto; max-height:400px; border:1px solid #cbd5e1; border-radius:6px;">
                    <table class="data-table" style="margin:0; font-size:0.83rem;">
                        <thead>
                            <tr>{q_th}</tr>
                        </thead>
                        <tbody>
                            {q_tr if q_tr else '<tr><td colspan="' + str(len(q_cols)) + '" style="text-align:center; padding:20px;">Zero records matched query.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
            """
        else:
            query_box_html = f"""
            <div style="margin-top:20px; border-top:2px solid #e2e8f0; padding-top:16px;">
                <div class="alert-banner alert-danger" style="margin:0;">
                    <div>
                        <div style="font-weight:700; margin-bottom:4px;">❌ SQL Execution Error</div>
                        <div style="font-family:monospace; font-size:0.85rem;">{html.escape(str(query_result.get('error', 'Unknown query execution failure')))}</div>
                    </div>
                </div>
            </div>
            """

    default_query = query_input or f"SELECT * FROM {active_table} LIMIT 25;"

    return f"""
    <div style="max-width:1300px; margin:0 auto;">
        <!-- Header -->
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px; margin-bottom:24px;">
            <div>
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:2rem;">🗄️</span>
                    <div>
                        <h2 style="color:var(--primary); font-size:1.6rem; font-weight:800;">CIHIP Database Explorer & Schema Hub</h2>
                        <p style="color:#64748b; font-size:0.88rem;">National Relational Database • Cloud PostgreSQL & Embedded SQLite Dual Engine</p>
                    </div>
                </div>
            </div>
            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                {engine_badge}
                <span class="badge badge-info" style="font-size:0.85rem; padding:6px 12px;">🟢 {engine.get('status', 'Online')}</span>
            </div>
        </div>

        <!-- Metrics Overview Grid -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:24px;">
            <div class="card" style="padding:16px; border-left:4px solid var(--primary);">
                <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Active Engine</div>
                <div style="font-size:1.15rem; font-weight:800; color:var(--primary); margin-top:4px;">{engine.get('display_name', 'SQLite')}</div>
                <div style="font-size:0.78rem; color:#475569; margin-top:2px;">{engine.get('driver', '')}</div>
            </div>

            <div class="card" style="padding:16px; border-left:4px solid var(--secondary);">
                <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Storage & Host</div>
                <div style="font-size:1.15rem; font-weight:800; color:var(--secondary); margin-top:4px;">
                    {engine.get('database', 'cihip')}
                </div>
                <div style="font-size:0.78rem; color:#475569; margin-top:2px; font-family:monospace;">
                    {engine.get('host', 'Local')} {'(' + str(engine.get('size_kb', '0')) + ' KB)' if not is_pg else ''}
                </div>
            </div>

            <div class="card" style="padding:16px; border-left:4px solid var(--accent-green);">
                <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Relational Tables</div>
                <div style="font-size:1.15rem; font-weight:800; color:var(--accent-green); margin-top:4px;">12 Core Schemas</div>
                <div style="font-size:0.78rem; color:#475569; margin-top:2px;">FHIR R4 & ABDM Compliant</div>
            </div>

            <div class="card" style="padding:16px; border-left:4px solid var(--accent-saffron);">
                <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Total Portal Records</div>
                <div style="font-size:1.15rem; font-weight:800; color:var(--accent-saffron); margin-top:4px;">{total_records:,} Records</div>
                <div style="font-size:0.78rem; color:#475569; margin-top:2px;">ACID Transactions Guaranteed</div>
            </div>
        </div>

        <!-- Cloud Deployment Architecture Callout -->
        <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:14px 20px; margin-bottom:24px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="font-size:1.5rem;">☁️</span>
                <div>
                    <div style="font-weight:700; color:#166534; font-size:0.92rem;">Seamless Cloud PostgreSQL & Embedded SQLite Dual Support</div>
                    <div style="font-size:0.82rem; color:#15803d;">
                        CIHIP is configured to automatically bind to Render Managed PostgreSQL, Supabase, or Neon via <code>DATABASE_URL</code> in cloud environments, while providing 100% standard library SQLite local execution without external dependencies.
                    </div>
                </div>
            </div>
            <a href="/api/docs" class="btn btn-outline btn-sm" style="background:#ffffff;">View FHIR Schema</a>
        </div>

        <!-- Table Selector Bar -->
        <div class="card" style="padding:18px; margin-bottom:24px;">
            <div style="font-size:0.85rem; font-weight:700; color:var(--primary); margin-bottom:12px; text-transform:uppercase; letter-spacing:0.5px;">
                Select Relational Table to Inspect:
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                {chips_html}
            </div>
        </div>

        <!-- Active Table Viewer -->
        <div class="card" style="padding:22px; margin-bottom:28px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px;">
                <div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <h3 style="color:var(--primary); font-size:1.3rem; font-weight:800; margin:0;">
                            {table_icons.get(active_table, '📁')} {active_table}
                        </h3>
                        <span class="badge badge-primary">{total_rows} records</span>
                        <span style="font-size:0.75rem; color:#64748b; font-family:monospace;">Primary Key: {pk}</span>
                    </div>
                    <p style="font-size:0.84rem; color:#64748b; margin-top:4px;">{desc}</p>
                </div>

                <div style="display:flex; gap:8px; align-items:center;">
                    <a href="/admin/database/export?table={active_table}&format=json" class="btn btn-secondary btn-sm" download>
                        Export JSON
                    </a>
                    <a href="/admin/database/export?table={active_table}&format=csv" class="btn btn-secondary btn-sm" download>
                        Export CSV
                    </a>
                </div>
            </div>

            <!-- Table Data Grid -->
            <div style="overflow-x:auto; border:1px solid #cbd5e1; border-radius:8px; margin-bottom:16px;">
                <table class="data-table" style="margin:0; width:100%;">
                    <thead>
                        <tr>{th_cells}</tr>
                    </thead>
                    <tbody>
                        {tr_cells}
                    </tbody>
                </table>
            </div>

            <!-- Pagination Bar -->
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; font-size:0.85rem; color:#64748b;">
                <div>
                    Page <strong>{current_page}</strong> of <strong>{total_pages}</strong> (Total {total_rows} records)
                </div>
                <div style="display:flex; gap:8px;">
                    {prev_link}
                    {next_link}
                </div>
            </div>
        </div>

        <!-- Interactive SQL Query Console -->
        <div class="card" style="padding:22px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <h3 style="color:var(--primary); font-size:1.25rem; font-weight:800; margin:0;">
                    Interactive SQL Console & Data Query Runner
                </h3>
            </div>
            <p style="font-size:0.84rem; color:#64748b; margin-bottom:16px;">
                Execute safe read-only SQL queries (<code>SELECT</code>, <code>EXPLAIN</code>, <code>WITH</code>) across the national database.
            </p>

            <!-- Quick Template Chips -->
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px;">
                <button type="button" class="btn btn-secondary btn-sm" onclick="setQuery('SELECT * FROM patients WHERE state = \\'Delhi\\';')">
                    Delhi Patients
                </button>
                <button type="button" class="btn btn-secondary btn-sm" onclick="setQuery('SELECT udk, name, specialty, qualification, phone FROM doctors;')">
                    Doctors Catalog
                </button>
                <button type="button" class="btn btn-secondary btn-sm" onclick="setQuery('SELECT encounter_id, upk, udk, hospital_id, diagnosis_name, diagnosis_snomed, start_time FROM encounters;')">
                    Clinical Encounters
                </button>
                <button type="button" class="btn btn-secondary btn-sm" onclick="setQuery('SELECT report_id, upk, test_name, loinc_code, abnormal_flag, reference_range FROM diagnostic_reports;')">
                    Lab Reports (LOINC)
                </button>
                <button type="button" class="btn btn-secondary btn-sm" onclick="setQuery('SELECT rx_id, upk, udk, canonical_hash, status, issue_time FROM prescriptions;')">
                    Signed Prescriptions
                </button>
                <button type="button" class="btn btn-secondary btn-sm" onclick="setQuery('SELECT audit_id, timestamp, user_id, action, resource_type, outcome, curr_hash FROM audit_events ORDER BY timestamp DESC LIMIT 20;')">
                    Audit Trail Ledger
                </button>
            </div>

            <!-- Query Form -->
            <form action="/admin/database/query" method="POST">
                <input type="hidden" name="table" value="{active_table}">
                <div style="margin-bottom:12px;">
                    <textarea 
                        name="sql" 
                        id="sqlEditor" 
                        rows="4" 
                        style="width:100%; font-family:Consolas, Monaco, monospace; font-size:0.88rem; padding:12px; border-radius:6px; border:1px solid #cbd5e1; background:#0f172a; color:#f8fafc; line-height:1.4;"
                        placeholder="Enter SQL SELECT statement here..."
                    >{html.escape(default_query)}</textarea>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:0.78rem; color:#64748b;">
                        State mutations (DROP/DELETE/UPDATE) are protected. Read-only execution enforced.
                    </div>
                    <button type="submit" class="btn btn-primary" style="padding:8px 20px; font-weight:700;">
                        Run SQL Query
                    </button>
                </div>
            </form>

            <!-- Query Results -->
            {query_box_html}
        </div>
    </div>

    <script>
    function setQuery(sql) {{
        const editor = document.getElementById('sqlEditor');
        if (editor) {{
            editor.value = sql;
            editor.focus();
        }}
    }}
    </script>
    """
