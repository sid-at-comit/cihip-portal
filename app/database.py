"""
Database Schema & Data Access Layer
SQLite with Full Relational Schema, ACID Transactions & Seed Data
"""

import sqlite3
import json
import time
import os
from typing import Dict, Any, List, Optional
from app.config import DB_PATH
from app.security import (
    hash_password, generate_prescription_signature, compute_audit_hash,
    generate_upk, generate_udk
)

def get_db_connection():
    """Establish connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Create all relational tables and indexes if they do not exist."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.executescript("""
    -- User accounts & credentials
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT DEFAULT 'ACTIVE',
        created_at TEXT NOT NULL
    );

    -- Patients (ABHA / UPK)
    CREATE TABLE IF NOT EXISTS patients (
        upk TEXT PRIMARY KEY,
        abha_number TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        dob TEXT NOT NULL,
        gender TEXT NOT NULL,
        blood_group TEXT,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        pincode TEXT,
        phone TEXT NOT NULL,
        email TEXT,
        emergency_contact TEXT,
        status TEXT DEFAULT 'ACTIVE',
        created_at TEXT NOT NULL
    );

    -- Hospitals (HFR Registered)
    CREATE TABLE IF NOT EXISTS hospitals (
        hospital_id TEXT PRIMARY KEY,
        hfr_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        tier TEXT NOT NULL,
        departments_json TEXT NOT NULL,
        status TEXT DEFAULT 'ACTIVE',
        created_at TEXT NOT NULL
    );

    -- Doctors (HPR & NMC Registered / UDK)
    CREATE TABLE IF NOT EXISTS doctors (
        udk TEXT PRIMARY KEY,
        nmc_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        hospital_id TEXT NOT NULL,
        qualification TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        status TEXT DEFAULT 'VERIFIED',
        created_at TEXT NOT NULL,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
    );

    -- Diagnostic Laboratories (NABL Accredited)
    CREATE TABLE IF NOT EXISTS labs (
        lab_id TEXT PRIMARY KEY,
        nabl_id TEXT UNIQUE NOT NULL,
        hfr_id TEXT NOT NULL,
        name TEXT NOT NULL,
        hospital_id TEXT,
        address TEXT NOT NULL,
        accreditation_expiry TEXT NOT NULL,
        status TEXT DEFAULT 'ACCREDITED',
        created_at TEXT NOT NULL
    );

    -- Clinical Encounters
    CREATE TABLE IF NOT EXISTS encounters (
        encounter_id TEXT PRIMARY KEY,
        upk TEXT NOT NULL,
        udk TEXT NOT NULL,
        hospital_id TEXT NOT NULL,
        department TEXT NOT NULL,
        start_time TEXT NOT NULL,
        chief_complaint TEXT NOT NULL,
        vitals_json TEXT NOT NULL,
        diagnosis_snomed TEXT NOT NULL,
        diagnosis_name TEXT NOT NULL,
        clinical_notes TEXT,
        allergies TEXT,
        status TEXT DEFAULT 'COMPLETED',
        FOREIGN KEY (upk) REFERENCES patients(upk),
        FOREIGN KEY (udk) REFERENCES doctors(udk),
        FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
    );

    -- Diagnostic Test Orders (FHIR ServiceRequest)
    CREATE TABLE IF NOT EXISTS service_requests (
        order_id TEXT PRIMARY KEY,
        upk TEXT NOT NULL,
        udk TEXT NOT NULL,
        hospital_id TEXT NOT NULL,
        lab_id TEXT NOT NULL,
        loinc_code TEXT NOT NULL,
        test_name TEXT NOT NULL,
        priority TEXT NOT NULL,
        specimen_type TEXT NOT NULL,
        clinical_indication TEXT,
        order_time TEXT NOT NULL,
        status TEXT DEFAULT 'SUBMITTED',
        FOREIGN KEY (upk) REFERENCES patients(upk),
        FOREIGN KEY (udk) REFERENCES doctors(udk),
        FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id),
        FOREIGN KEY (lab_id) REFERENCES labs(lab_id)
    );

    -- Diagnostic Reports (FHIR DiagnosticReport + Observation + PDF Base64)
    CREATE TABLE IF NOT EXISTS diagnostic_reports (
        report_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        upk TEXT NOT NULL,
        udk TEXT NOT NULL,
        lab_id TEXT NOT NULL,
        loinc_code TEXT NOT NULL,
        test_name TEXT NOT NULL,
        result_values_json TEXT NOT NULL,
        reference_range TEXT NOT NULL,
        abnormal_flag TEXT NOT NULL,
        interpretation TEXT,
        pdf_attachment_base64 TEXT,
        report_time TEXT NOT NULL,
        status TEXT DEFAULT 'FINAL',
        amended_from_id TEXT,
        FOREIGN KEY (order_id) REFERENCES service_requests(order_id),
        FOREIGN KEY (upk) REFERENCES patients(upk),
        FOREIGN KEY (udk) REFERENCES doctors(udk),
        FOREIGN KEY (lab_id) REFERENCES labs(lab_id)
    );

    -- E-Prescriptions (FHIR MedicationRequest with PKI Digital Signature)
    CREATE TABLE IF NOT EXISTS prescriptions (
        rx_id TEXT PRIMARY KEY,
        upk TEXT NOT NULL,
        udk TEXT NOT NULL,
        encounter_id TEXT,
        medications_json TEXT NOT NULL,
        canonical_hash TEXT NOT NULL,
        digital_signature TEXT NOT NULL,
        qr_payload TEXT NOT NULL,
        issue_time TEXT NOT NULL,
        status TEXT DEFAULT 'ACTIVE',
        FOREIGN KEY (upk) REFERENCES patients(upk),
        FOREIGN KEY (udk) REFERENCES doctors(udk)
    );

    -- Consent Manager (ABDM Consent Artefacts)
    CREATE TABLE IF NOT EXISTS consents (
        consent_id TEXT PRIMARY KEY,
        upk TEXT NOT NULL,
        requester_type TEXT NOT NULL,
        requester_id TEXT NOT NULL,
        requester_name TEXT NOT NULL,
        purpose TEXT NOT NULL,
        resources_json TEXT NOT NULL,
        valid_from TEXT NOT NULL,
        valid_to TEXT NOT NULL,
        status TEXT DEFAULT 'GRANTED',
        granted_time TEXT NOT NULL,
        revoked_time TEXT,
        FOREIGN KEY (upk) REFERENCES patients(upk)
    );

    -- Immutable Audit Ledger with Cryptographic Hash Chaining
    CREATE TABLE IF NOT EXISTS audit_events (
        audit_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL,
        action TEXT NOT NULL,
        resource_type TEXT NOT NULL,
        resource_id TEXT NOT NULL,
        outcome TEXT NOT NULL,
        ip_address TEXT NOT NULL,
        details_json TEXT NOT NULL,
        prev_hash TEXT NOT NULL,
        curr_hash TEXT NOT NULL
    );

    -- Research Query Logs
    CREATE TABLE IF NOT EXISTS research_queries (
        query_id TEXT PRIMARY KEY,
        researcher_id TEXT NOT NULL,
        department TEXT NOT NULL,
        filters_json TEXT NOT NULL,
        cohort_count INTEGER NOT NULL,
        export_time TEXT NOT NULL
    );

    -- Create indexes for sub-second search
    CREATE INDEX IF NOT EXISTS idx_patients_abha ON patients(abha_number);
    CREATE INDEX IF NOT EXISTS idx_doctors_nmc ON doctors(nmc_id);
    CREATE INDEX IF NOT EXISTS idx_encounters_upk ON encounters(upk);
    CREATE INDEX IF NOT EXISTS idx_service_requests_upk ON service_requests(upk);
    CREATE INDEX IF NOT EXISTS idx_service_requests_lab ON service_requests(lab_id);
    CREATE INDEX IF NOT EXISTS idx_diagnostic_reports_upk ON diagnostic_reports(upk);
    CREATE INDEX IF NOT EXISTS idx_prescriptions_upk ON prescriptions(upk);
    CREATE INDEX IF NOT EXISTS idx_consents_upk ON consents(upk);
    CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp);
    """)

    conn.commit()
    seed_initial_data(conn)
    conn.close()

def log_audit_event(
    user_id: str,
    role: str,
    action: str,
    resource_type: str,
    resource_id: str,
    outcome: str = "SUCCESS",
    ip_address: str = "127.0.0.1",
    details: Optional[Dict[str, Any]] = None
) -> str:
    """Append a tamper-evident audit record with SHA-256 hash chaining."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Retrieve current last hash in the chain
    cur.execute("SELECT curr_hash FROM audit_events ORDER BY rowid DESC LIMIT 1")
    last_row = cur.fetchone()
    prev_hash = last_row["curr_hash"] if last_row else "GENESIS_BLOCK_CIHIP_NHA_2026_MOHFW"

    audit_id = f"AUD-{int(time.time() * 1000)}-{os.urandom(3).hex()}"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    details_str = json.dumps(details or {})

    entry = {
        "timestamp": timestamp,
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "outcome": outcome,
    }
    curr_hash = compute_audit_hash(prev_hash, entry)

    cur.execute("""
        INSERT INTO audit_events 
        (audit_id, timestamp, user_id, role, action, resource_type, resource_id, outcome, ip_address, details_json, prev_hash, curr_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (audit_id, timestamp, user_id, role, action, resource_type, resource_id, outcome, ip_address, details_str, prev_hash, curr_hash))

    conn.commit()
    conn.close()
    return audit_id

def verify_audit_chain_integrity() -> Dict[str, Any]:
    """Verify cryptographic integrity of all audit entries."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_events ORDER BY rowid ASC")
    rows = cur.fetchall()
    conn.close()

    expected_prev = "GENESIS_BLOCK_CIHIP_NHA_2026_MOHFW"
    valid_count = 0
    tampered = []

    for row in rows:
        if row["prev_hash"] != expected_prev:
            tampered.append(row["audit_id"])
        
        entry = {
            "timestamp": row["timestamp"],
            "user_id": row["user_id"],
            "action": row["action"],
            "resource_type": row["resource_type"],
            "resource_id": row["resource_id"],
            "outcome": row["outcome"],
        }
        recalculated = compute_audit_hash(row["prev_hash"], entry)
        if recalculated != row["curr_hash"]:
            tampered.append(row["audit_id"])
        else:
            valid_count += 1
        expected_prev = row["curr_hash"]

    return {
        "total_records": len(rows),
        "valid_records": valid_count,
        "is_intact": len(tampered) == 0,
        "tampered_ids": tampered,
        "latest_block_hash": expected_prev
    }

def seed_initial_data(conn: sqlite3.Connection):
    """Populate database with comprehensive national demo data if empty."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM hospitals")
    if cur.fetchone()[0] > 0:
        return  # Already seeded

    # 1. Seed Hospitals
    hospitals = [
        ("HOSP-AIIMS-DEL", "HFR-DEL-000101", "All India Institute of Medical Sciences (AIIMS)", "Delhi", "New Delhi", "Tertiary Apex", json.dumps(["Cardiology", "Pulmonology", "Endocrinology", "Nephrology", "General Medicine"])),
        ("HOSP-CMC-VEL", "HFR-TN-000204", "Christian Medical College & Hospital (CMC)", "Tamil Nadu", "Vellore", "Tertiary Research", json.dumps(["Cardiology", "Gastroenterology", "Hematology", "General Medicine"])),
        ("HOSP-APOLLO-CHE", "HFR-TN-000305", "Apollo Hospitals Greams Road", "Tamil Nadu", "Chennai", "Super Specialty", json.dumps(["Cardiology", "Oncology", "Neurology", "Biochemistry"])),
        ("HOSP-TMH-MUM", "HFR-MH-000408", "Tata Memorial Centre & Hospital", "Maharashtra", "Mumbai", "National Cancer Apex", json.dumps(["Oncology", "Radiology", "Pathology", "General Medicine"]))
    ]
    cur.executemany("INSERT INTO hospitals VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', '2026-01-10T09:00:00Z')", hospitals)

    # 2. Seed Diagnostic Labs
    labs = [
        ("LAB-APEX-NABL", "NABL-MED-2024-9912", "HFR-DEL-000101", "Apex NABL Clinical Diagnostics Lab", "HOSP-AIIMS-DEL", "Ansari Nagar East, New Delhi - 110029", "2028-12-31", "ACCREDITED", "2026-01-10T09:00:00Z"),
        ("LAB-NATREF-NABL", "NABL-MED-2023-4418", "HFR-TN-000204", "National Reference Pathology Services", "HOSP-CMC-VEL", "Ida Scudder Road, Vellore - 632004", "2027-10-15", "ACCREDITED", "2026-01-10T09:00:00Z"),
        ("LAB-SRL-CHE", "NABL-MED-2025-1102", "HFR-TN-000305", "Apollo Diagnostic Services & Genomics", "HOSP-APOLLO-CHE", "Greams Lane, Chennai - 600006", "2029-05-20", "ACCREDITED", "2026-01-10T09:00:00Z")
    ]
    cur.executemany("INSERT INTO labs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", labs)

    # 3. Seed Doctors
    doctors = [
        ("UDK-IND-2026-4412", "NMC-MCI-2015-88492", "Dr. Priya Nair, MD, DM", "Cardiology", "HOSP-AIIMS-DEL", "MBBS, MD (Medicine), DM (Cardiology)", "+91 98110 22331", "dr.priya.nair@aiims.edu.in", "VERIFIED", "2026-01-12T10:00:00Z"),
        ("UDK-IND-2026-8891", "NMC-MCI-2012-47201", "Dr. Rajesh Khanna, MD", "Pulmonology", "HOSP-AIIMS-DEL", "MBBS, MD (Pulmonary Medicine)", "+91 98101 55442", "dr.rajesh.khanna@aiims.edu.in", "VERIFIED", "2026-01-12T10:00:00Z"),
        ("UDK-IND-2026-3105", "NMC-MCI-2018-91244", "Dr. Sneha Roy, MD, DNB", "Endocrinology", "HOSP-CMC-VEL", "MBBS, MD (General Medicine), DNB (Endocrinology)", "+91 94432 11982", "dr.sneha.roy@cmcvellore.ac.in", "VERIFIED", "2026-01-15T11:00:00Z"),
        ("UDK-IND-2026-6219", "NMC-MCI-2016-33910", "Dr. Amitabh Sen, MD", "General Medicine", "HOSP-APOLLO-CHE", "MBBS, MD (Internal Medicine)", "+91 98400 88291", "dr.amitabh.sen@apollohospitals.com", "VERIFIED", "2026-01-18T09:30:00Z")
    ]
    cur.executemany("INSERT INTO doctors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", doctors)

    # 4. Seed Patients
    patients = [
        ("UPK-IND-2026-9041", "91-4567-8901-2345", "Rajesh Sharma", "1978-04-14", "Male", "B+", "Delhi", "South Delhi", "110017", "+91 98712 34567", "rajesh.sharma@example.com", "Sunita Sharma (+91 98712 34568) - Wife"),
        ("UPK-IND-2026-7721", "91-8890-1234-5678", "Ananya Patel", "1990-11-23", "Female", "O+", "Gujarat", "Ahmedabad", "380015", "+91 98250 88991", "ananya.patel@example.com", "Viren Patel (+91 98250 88992) - Husband"),
        ("UPK-IND-2026-3392", "91-3344-5566-7788", "Mohammed Farooq", "1965-08-05", "Male", "A+", "Tamil Nadu", "Chennai", "600004", "+91 94440 22334", "m.farooq@example.com", "Nasreen Farooq (+91 94440 22335) - Daughter"),
        ("UPK-IND-2026-5518", "91-7711-2233-4455", "Sunita Devi", "1984-02-19", "Female", "AB+", "Maharashtra", "Mumbai", "400012", "+91 98200 44119", "sunita.devi@example.com", "Ramesh Devi (+91 98200 44120) - Brother")
    ]
    for p in patients:
        cur.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', '2026-01-20T10:00:00Z')", p)

    # 5. Seed System Users (Default password for demo: 'Admin@123')
    pwd_hash = hash_password("Admin@123")
    users = [
        ("USR-PAT-01", "patient_rajesh", pwd_hash, "PATIENT", "UPK-IND-2026-9041", "Rajesh Sharma", "rajesh.sharma@example.com", "+91 98712 34567"),
        ("USR-DOC-01", "doctor_priya", pwd_hash, "DOCTOR", "UDK-IND-2026-4412", "Dr. Priya Nair", "dr.priya.nair@aiims.edu.in", "+91 98110 22331"),
        ("USR-DOC-02", "doctor_sneha", pwd_hash, "DOCTOR", "UDK-IND-2026-3105", "Dr. Sneha Roy", "dr.sneha.roy@cmcvellore.ac.in", "+91 94432 11982"),
        ("USR-LAB-01", "lab_ramesh", pwd_hash, "LAB_TECHNICIAN", "LAB-APEX-NABL", "Ramesh Verma (Chief Tech)", "ramesh.verma@apexdiagnostics.in", "+91 98188 44112"),
        ("USR-HOSP-01", "admin_aiims", pwd_hash, "HOSPITAL_ADMIN", "HOSP-AIIMS-DEL", "Dr. Arvind Swaminathan (Superintendent)", "admin@aiims.edu.in", "+91 98100 99001"),
        ("USR-RES-01", "researcher_sunita", pwd_hash, "RESEARCHER", "ICMR-RES-2026", "Dr. Sunita Kulkarni (ICMR Epidemiologist)", "dr.sunita.k@icmr.gov.in", "+91 98230 77112"),
        ("USR-SYS-01", "admin_cihip", pwd_hash, "SYSTEM_ADMIN", "CIHIP-HQ-DELHI", "Vikramaditya Sen (Zero Trust SecOps)", "secops@cihip.gov.in", "+91 98111 00001")
    ]
    for u in users:
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', '2026-01-20T10:00:00Z')", u)

    # 6. Seed Consents
    cur.execute("""
        INSERT INTO consents VALUES 
        ('CON-2026-001', 'UPK-IND-2026-9041', 'DOCTOR', 'UDK-IND-2026-4412', 'Dr. Priya Nair (Cardiologist, AIIMS)', 'Treatment', 
         '["DiagnosticReport", "MedicationRequest", "Encounter"]', '2026-01-20T00:00:00Z', '2027-01-20T23:59:59Z', 'GRANTED', '2026-01-20T10:30:00Z', NULL),
        ('CON-2026-002', 'UPK-IND-2026-9041', 'LAB', 'LAB-APEX-NABL', 'Apex NABL Clinical Diagnostics Lab', 'Diagnostic Order Fulfillment', 
         '["ServiceRequest", "DiagnosticReport"]', '2026-01-20T00:00:00Z', '2027-01-20T23:59:59Z', 'GRANTED', '2026-01-20T10:35:00Z', NULL),
        ('CON-2026-003', 'UPK-IND-2026-7721', 'DOCTOR', 'UDK-IND-2026-3105', 'Dr. Sneha Roy (Endocrinologist, CMC)', 'Treatment', 
         '["DiagnosticReport", "MedicationRequest", "Encounter"]', '2026-02-01T00:00:00Z', '2027-02-01T23:59:59Z', 'GRANTED', '2026-02-01T11:00:00Z', NULL)
    """)

    # 7. Seed Encounters across hospitals (multi-hospital LHR demo)
    encounters = [
        ("ENC-2026-001", "UPK-IND-2026-9041", "UDK-IND-2026-4412", "HOSP-AIIMS-DEL", "Cardiology", "2026-02-15T10:30:00Z",
         "Chest discomfort on exertion, fatigue, high morning blood pressure.",
         json.dumps({"bp": "146/92 mmHg", "pulse": "82 bpm", "spo2": "98%", "temp": "98.4 F", "bmi": "26.4"}),
         "38341003", "Essential Hypertension", "Patient advised low sodium diet, ordered ECG & Lipid Profile.", "Penicillin", "COMPLETED"),
        
        ("ENC-2026-002", "UPK-IND-2026-9041", "UDK-IND-2026-4412", "HOSP-AIIMS-DEL", "Cardiology", "2026-03-10T11:00:00Z",
         "Follow-up consultation. Reports reviewed.",
         json.dumps({"bp": "134/86 mmHg", "pulse": "76 bpm", "spo2": "99%", "temp": "98.2 F", "bmi": "26.1"}),
         "53741008", "Coronary Artery Disease (CAD)", "Initiated Statin and Telmisartan therapy.", "Penicillin", "COMPLETED"),
        
        ("ENC-2026-003", "UPK-IND-2026-9041", "UDK-IND-2026-3105", "HOSP-CMC-VEL", "Endocrinology", "2026-06-05T14:15:00Z",
         "Frequent urination, excessive thirst, periodic blurring of vision.",
         json.dumps({"bp": "130/84 mmHg", "pulse": "78 bpm", "spo2": "98%", "temp": "98.6 F", "bmi": "26.8"}),
         "44054006", "Type 2 Diabetes Mellitus", "Advised HbA1c test and dietary counseling.", "Penicillin", "COMPLETED"),

        ("ENC-2026-004", "UPK-IND-2026-7721", "UDK-IND-2026-3105", "HOSP-CMC-VEL", "Endocrinology", "2026-04-18T09:45:00Z",
         "Routine diabetic checkup, persistent mild numbness in toes.",
         json.dumps({"bp": "124/80 mmHg", "pulse": "72 bpm", "spo2": "99%", "temp": "98.5 F", "bmi": "24.2"}),
         "44054006", "Type 2 Diabetes Mellitus", "Glycemic control stable. Continue Metformin.", "None", "COMPLETED")
    ]
    cur.executemany("INSERT INTO encounters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", encounters)

    # 8. Seed Diagnostic Orders (ServiceRequests)
    orders = [
        ("ORD-2026-101", "UPK-IND-2026-9041", "UDK-IND-2026-4412", "HOSP-AIIMS-DEL", "LAB-APEX-NABL", "2093-3", "Total Cholesterol", "Routine", "Serum", "Hyperlipidemia screening in hypertensive patient", "2026-02-15T11:00:00Z", "COMPLETED"),
        ("ORD-2026-102", "UPK-IND-2026-9041", "UDK-IND-2026-3105", "HOSP-CMC-VEL", "LAB-APEX-NABL", "14804-9", "Glycated Hemoglobin (HbA1c)", "Urgent", "Whole Blood (EDTA)", "Type 2 diabetes glycemic evaluation", "2026-06-05T14:45:00Z", "COMPLETED"),
        ("ORD-2026-103", "UPK-IND-2026-9041", "UDK-IND-2026-4412", "HOSP-AIIMS-DEL", "LAB-APEX-NABL", "2345-7", "Fasting Blood Glucose (FBS)", "Routine", "Fluoride Plasma", "Fasting blood sugar follow-up", "2026-09-20T10:00:00Z", "SUBMITTED"),
        ("ORD-2026-104", "UPK-IND-2026-7721", "UDK-IND-2026-3105", "HOSP-CMC-VEL", "LAB-NATREF-NABL", "14804-9", "Glycated Hemoglobin (HbA1c)", "Routine", "Whole Blood (EDTA)", "Annual diabetic monitoring", "2026-04-18T10:15:00Z", "COMPLETED")
    ]
    cur.executemany("INSERT INTO service_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", orders)

    # 9. Seed Diagnostic Reports with LOINC results and PDF Base64
    reports = [
        ("RPT-2026-501", "ORD-2026-101", "UPK-IND-2026-9041", "UDK-IND-2026-4412", "LAB-APEX-NABL", "2093-3", "Total Cholesterol",
         json.dumps([{"parameter": "Total Cholesterol", "value": 242.0, "unit": "mg/dL", "ref": "125 - 200 mg/dL", "flag": "High"}]),
         "125.0 - 200.0 mg/dL", "High", "Mild hypercholesterolemia. Dietary modification and statin recommended.",
         "JVBERi0xLjQKJVRlc3QgUERGIENJSElQIERpYWdub3N0aWMgUmVwb3J0IEFJSU1TIERlbGhp", "2026-02-16T15:00:00Z", "FINAL", None),

        ("RPT-2026-502", "ORD-2026-102", "UPK-IND-2026-9041", "UDK-IND-2026-3105", "LAB-APEX-NABL", "14804-9", "Glycated Hemoglobin (HbA1c)",
         json.dumps([{"parameter": "Glycated Hemoglobin (HbA1c)", "value": 7.8, "unit": "%", "ref": "4.0 - 5.6 %", "flag": "High"}]),
         "4.0 - 5.6 %", "High", "Uncontrolled glycemic state indicative of early diabetes mellitus.",
         "JVBERi0xLjQKJVRlc3QgUERGIENJSElQIERpYWdub3N0aWMgUmVwb3J0IENMQyBWZWxsb3Jl", "2026-06-06T12:30:00Z", "FINAL", None),

        ("RPT-2026-503", "ORD-2026-104", "UPK-IND-2026-7721", "UDK-IND-2026-3105", "LAB-NATREF-NABL", "14804-9", "Glycated Hemoglobin (HbA1c)",
         json.dumps([{"parameter": "Glycated Hemoglobin (HbA1c)", "value": 6.4, "unit": "%", "ref": "4.0 - 5.6 %", "flag": "High"}]),
         "4.0 - 5.6 %", "High", "Fair glycemic control maintained on current oral hypoglycemic agent.",
         "JVBERi0xLjQKJVRlc3QgUERGIENJSElQIERpYWdub3N0aWMgUmVwb3J0", "2026-04-19T11:00:00Z", "FINAL", None)
    ]
    cur.executemany("INSERT INTO diagnostic_reports VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", reports)

    # 10. Seed Prescriptions with verified PKI signatures
    rx1_meds = [
        {"code": "386864001", "name": "Tab. Telmisartan 40 mg", "dosage": "40 mg", "frequency": "1-0-0 (Morning after food)", "route": "Oral", "duration": "30 days", "instructions": "Monitor BP weekly"},
        {"code": "387584000", "name": "Tab. Atorvastatin 20 mg", "dosage": "20 mg", "frequency": "0-0-1 (Bedtime)", "route": "Oral", "duration": "30 days", "instructions": "Take after dinner"}
    ]
    rx1_dict = {"rx_id": "RX-2026-801", "upk": "UPK-IND-2026-9041", "udk": "UDK-IND-2026-4412", "medications": rx1_meds}
    rx1_sig = generate_prescription_signature(rx1_dict, "UDK-IND-2026-4412", "NMC-MCI-2015-88492")

    rx2_meds = [
        {"code": "372567009", "name": "Tab. Metformin HCl 500 mg", "dosage": "500 mg", "frequency": "1-0-1 (Twice daily after meals)", "route": "Oral", "duration": "60 days", "instructions": "Strict low sugar diet"}
    ]
    rx2_dict = {"rx_id": "RX-2026-802", "upk": "UPK-IND-2026-9041", "udk": "UDK-IND-2026-3105", "medications": rx2_meds}
    rx2_sig = generate_prescription_signature(rx2_dict, "UDK-IND-2026-3105", "NMC-MCI-2018-91244")

    cur.execute("""
        INSERT INTO prescriptions VALUES 
        ('RX-2026-801', 'UPK-IND-2026-9041', 'UDK-IND-2026-4412', 'ENC-2026-002', ?, ?, ?, ?, '2026-03-10T11:45:00Z', 'ACTIVE'),
        ('RX-2026-802', 'UPK-IND-2026-9041', 'UDK-IND-2026-3105', 'ENC-2026-003', ?, ?, ?, ?, '2026-06-05T15:00:00Z', 'ACTIVE')
    """, (
        json.dumps(rx1_meds), rx1_sig["canonical_hash"], rx1_sig["digital_seal"], rx1_sig["qr_payload"],
        json.dumps(rx2_meds), rx2_sig["canonical_hash"], rx2_sig["digital_seal"], rx2_sig["qr_payload"]
    ))

    # 11. Seed Audit Events (building initial cryptographic chain)
    audit_chain = [
        ("SYSTEM", "SYSTEM_ADMIN", "PORTAL_INIT", "CORE_INFRASTRUCTURE", "CIHIP-SERVER-01", "SUCCESS", "127.0.0.1", {"note": "CIHIP National Node online."}),
        ("UPK-IND-2026-9041", "PATIENT", "PATIENT_LOGIN", "PATIENT_PROFILE", "UPK-IND-2026-9041", "SUCCESS", "103.21.144.12", {"auth_method": "ABHA-OTP"}),
        ("UDK-IND-2026-4412", "DOCTOR", "PATIENT_SEARCH", "PATIENT", "UPK-IND-2026-9041", "SUCCESS", "14.139.60.2", {"purpose": "Clinical Consultation"}),
        ("UDK-IND-2026-4412", "DOCTOR", "CREATE_ORDER", "SERVICE_REQUEST", "ORD-2026-101", "SUCCESS", "14.139.60.2", {"test": "Total Cholesterol"}),
        ("LAB-APEX-NABL", "LAB_TECHNICIAN", "UPLOAD_REPORT", "DIAGNOSTIC_REPORT", "RPT-2026-501", "SUCCESS", "14.139.60.10", {"status": "FINAL"}),
        ("UDK-IND-2026-4412", "DOCTOR", "SIGN_PRESCRIPTION", "PRESCRIPTION", "RX-2026-801", "SUCCESS", "14.139.60.2", {"pki_token": "Valid Class 3 DSC"})
    ]

    prev_h = "GENESIS_BLOCK_CIHIP_NHA_2026_MOHFW"
    for i, a in enumerate(audit_chain):
        audit_id = f"AUD-SEED-{i+1:04d}"
        t_stamp = f"2026-02-15T{10+i:02d}:00:00Z"
        entry_meta = {
            "timestamp": t_stamp,
            "user_id": a[0],
            "action": a[2],
            "resource_type": a[3],
            "resource_id": a[4],
            "outcome": a[5],
        }
        curr_h = compute_audit_hash(prev_h, entry_meta)
        cur.execute("""
            INSERT INTO audit_events 
            (audit_id, timestamp, user_id, role, action, resource_type, resource_id, outcome, ip_address, details_json, prev_hash, curr_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (audit_id, t_stamp, a[0], a[1], a[2], a[3], a[4], a[5], a[6], json.dumps(a[7]), prev_h, curr_h))
        prev_h = curr_h

    conn.commit()
    print("Database successfully initialized and seeded with National Health Registry records.")
