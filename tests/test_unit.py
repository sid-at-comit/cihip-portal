"""
Internal Logic & Standards Conformance Test Suite (Sandboxed)
Tests Database, FHIR R4 Serializers, Cryptography, Zero-Trust, Terminology & Views
"""

import unittest
import json
import os
import sys

# Ensure application package is discoverable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, get_db_connection, log_audit_event, verify_audit_chain_integrity
from app.security import (
    generate_upk, generate_udk, generate_prescription_signature,
    verify_prescription_signature, evaluate_zero_trust_access,
    apply_k_anonymity_mask, apply_differential_privacy_noise,
    verify_blinded_key
)
from app.fhir import (
    to_fhir_patient, to_fhir_practitioner, to_fhir_organization,
    to_fhir_service_request, to_fhir_diagnostic_report,
    to_fhir_medication_request, to_fhir_consent, to_fhir_audit_event
)
from app.terminology import evaluate_lab_result, LOINC_CATALOG, SNOMED_DIAGNOSES, MEDICATIONS_CATALOG
from app.views import (
    render_master, render_landing_page, render_patient_dashboard,
    render_lhr_timeline, render_prescription_sheet, render_report_detail,
    render_doctor_dashboard, render_lab_worklist, render_hospital_portal,
    render_research_portal, render_security_portal
)

class TestCIHIPCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists("cihip.db"):
            os.remove("cihip.db")
        init_db()

    def test_01_database_and_seed_data(self):
        """Test database initialization and national registries."""
        conn = get_db_connection()
        cur = conn.cursor()

        # Check hospitals
        cur.execute("SELECT COUNT(*) FROM hospitals")
        self.assertGreaterEqual(cur.fetchone()[0], 4)

        # Check doctors
        cur.execute("SELECT COUNT(*) FROM doctors")
        self.assertGreaterEqual(cur.fetchone()[0], 4)

        # Check labs
        cur.execute("SELECT COUNT(*) FROM labs")
        self.assertGreaterEqual(cur.fetchone()[0], 3)

        # Check patients
        cur.execute("SELECT COUNT(*) FROM patients")
        self.assertGreaterEqual(cur.fetchone()[0], 4)

        conn.close()

    def test_02_blockchain_audit_ledger(self):
        """Test cryptographic hash chaining in audit trail."""
        log_id = log_audit_event(
            "TEST_USER", "SYSTEM_ADMIN", "SECURITY_VERIFICATION",
            "CORE_SYSTEM", "TEST-01", "SUCCESS", details={"test": True}
        )
        self.assertTrue(log_id.startswith("AUD-"))

        # Verify chain integrity
        check = verify_audit_chain_integrity()
        self.assertTrue(check["is_intact"])
        self.assertEqual(len(check["tampered_ids"]), 0)
        self.assertGreaterEqual(check["total_records"], 7)

    def test_03_zero_trust_policy_engine(self):
        """Test Zero Trust ABAC/RBAC authorization policies."""
        # Patient self-access
        allowed, msg = evaluate_zero_trust_access("PATIENT", "UPK-001", "VIEW_SELF_PROFILE", "PATIENT", "UPK-001")
        self.assertTrue(allowed)

        # Patient cross-access to other patient (denied)
        allowed, msg = evaluate_zero_trust_access("PATIENT", "UPK-001", "VIEW_OTHER_PROFILE", "PATIENT", "UPK-002")
        self.assertFalse(allowed)

        # Doctor with consent
        allowed, msg = evaluate_zero_trust_access("DOCTOR", "UDK-001", "VIEW_LHR_HISTORY", "PATIENT", "UPK-001", consent_status="GRANTED")
        self.assertTrue(allowed)

        # Doctor without consent
        allowed, msg = evaluate_zero_trust_access("DOCTOR", "UDK-001", "VIEW_LHR_HISTORY", "PATIENT", "UPK-001", consent_status="DENIED")
        self.assertFalse(allowed)

        # Doctor with emergency break glass
        allowed, msg = evaluate_zero_trust_access("DOCTOR", "UDK-001", "VIEW_LHR_HISTORY", "PATIENT", "UPK-001", consent_status="DENIED", emergency_break_glass=True)
        self.assertTrue(allowed)
        self.assertIn("BREAK-GLASS", msg)

        # Researcher requesting identifiable PHI (denied)
        allowed, msg = evaluate_zero_trust_access("RESEARCHER", "RES-001", "VIEW_PATIENT_NAME", "PATIENT")
        self.assertFalse(allowed)

        # Researcher requesting de-identified data (allowed)
        allowed, msg = evaluate_zero_trust_access("RESEARCHER", "RES-001", "QUERY_COHORT", "DEIDENTIFIED_ANALYTICS")
        self.assertTrue(allowed)

    def test_04_pki_digital_signature(self):
        """Test e-Prescription SHA-256 canonical hashing & PKI seal."""
        meds = [{"code": "386864001", "name": "Tab. Telmisartan 40 mg", "dosage": "40 mg"}]
        rx_data = {"rx_id": "RX-TEST-001", "upk": "UPK-001", "udk": "UDK-001", "medications": meds}

        sig = generate_prescription_signature(rx_data, "UDK-001", "NMC-12345")
        self.assertEqual(sig["verification_status"], "VALID")
        self.assertIn("digital_seal", sig)
        self.assertIn("qr_payload", sig)

        # Validate signature verification
        is_valid = verify_prescription_signature(rx_data, "UDK-001", "NMC-12345", sig["digital_seal"])
        self.assertTrue(is_valid)

        # Tampered medication test
        tampered_rx = dict(rx_data)
        tampered_rx["medications"] = [{"code": "386864001", "name": "Tab. Telmisartan 80 mg", "dosage": "80 mg"}]
        is_tampered_valid = verify_prescription_signature(tampered_rx, "UDK-001", "NMC-12345", sig["digital_seal"])
        self.assertFalse(is_tampered_valid)

    def test_05_fhir_r4_serializers(self):
        """Test FHIR R4 ABDM profiles serialization."""
        conn = get_db_connection()
        cur = conn.cursor()

        # Patient
        cur.execute("SELECT * FROM patients WHERE upk = 'UPK-IND-2026-9041'")
        pat_row = dict(cur.fetchone())
        fhir_pat = to_fhir_patient(pat_row)
        self.assertEqual(fhir_pat["resourceType"], "Patient")
        self.assertEqual(fhir_pat["id"], "UPK-IND-2026-9041")
        self.assertEqual(fhir_pat["identifier"][1]["system"], "https://healthid.ndhm.gov.in")

        # Practitioner
        cur.execute("SELECT * FROM doctors WHERE udk = 'UDK-IND-2026-4412'")
        doc_row = dict(cur.fetchone())
        fhir_doc = to_fhir_practitioner(doc_row)
        self.assertEqual(fhir_doc["resourceType"], "Practitioner")
        self.assertEqual(fhir_doc["id"], "UDK-IND-2026-4412")

        # DiagnosticReport
        cur.execute("SELECT * FROM diagnostic_reports WHERE report_id = 'RPT-2026-501'")
        rpt_row = dict(cur.fetchone())
        fhir_rpt = to_fhir_diagnostic_report(rpt_row)
        self.assertEqual(fhir_rpt["DiagnosticReport"]["resourceType"], "DiagnosticReport")
        self.assertGreaterEqual(len(fhir_rpt["Observations"]), 1)

        # MedicationRequest
        cur.execute("SELECT * FROM prescriptions WHERE rx_id = 'RX-2026-801'")
        rx_row = dict(cur.fetchone())
        fhir_rx = to_fhir_medication_request(rx_row)
        self.assertEqual(fhir_rx["resourceType"], "MedicationRequest")
        self.assertEqual(fhir_rx["id"], "RX-2026-801")

        # Consent
        cur.execute("SELECT * FROM consents WHERE consent_id = 'CON-2026-001'")
        con_row = dict(cur.fetchone())
        fhir_con = to_fhir_consent(con_row)
        self.assertEqual(fhir_con["resourceType"], "Consent")
        self.assertEqual(fhir_con["status"], "active")

        conn.close()

    def test_06_loinc_and_abnormal_evaluator(self):
        """Test LOINC clinical ranges and abnormal flag assessment."""
        # Fasting Glucose 2345-7 (Normal: 70-99)
        flag, ref = evaluate_lab_result("2345-7", 85.0)
        self.assertEqual(flag, "Normal")

        flag_high, _ = evaluate_lab_result("2345-7", 145.0)
        self.assertEqual(flag_high, "High")

        flag_crit, _ = evaluate_lab_result("2345-7", 350.0)
        self.assertEqual(flag_crit, "Critical")

        # HbA1c 14804-9 (Normal: 4.0-5.6)
        flag_hba1c, _ = evaluate_lab_result("14804-9", 7.8)
        self.assertEqual(flag_hba1c, "High")

    def test_07_k_anonymity_and_differential_privacy(self):
        """Test de-identification compliance (k >= 50)."""
        record = {
            "name": "Rajesh Sharma",
            "abha_number": "91-4567-8901-2345",
            "upk": "UPK-IND-2026-9041",
            "dob": "1978-04-14",
            "diagnosis_name": "Essential Hypertension",
            "diagnosis_snomed": "38341003"
        }
        masked = apply_k_anonymity_mask(record)
        self.assertNotIn("name", masked)
        self.assertNotIn("abha_number", masked)
        self.assertNotIn("upk", masked)
        self.assertIn("age_group", masked)
        self.assertIn("COMPLIANT", masked["k_anonymity_status"])

        # Differential privacy noise
        val = 100.0
        noised = apply_differential_privacy_noise(val)
        self.assertIsInstance(noised, float)
        self.assertGreater(noised, 0)

    def test_08_html_views_rendering(self):
        """Test HTML rendering without crashing."""
        user = {"role": "DOCTOR", "name": "Dr. Priya Nair", "entity_id": "UDK-IND-2026-4412"}
        html_out = render_master("Test Title", "<p>Hello CIHIP</p>", user, "en", "home")
        self.assertIn("CIHIP National Health Exchange", html_out)
        self.assertIn("Dr. Priya Nair", html_out)
        self.assertIn("Hello CIHIP", html_out)

    def test_09_idea_4_deterministic_hmac_blinded_keys(self):
        """Test Idea 4: Deterministic HMAC-SHA256 Blinded UPK and UDK generation and verification."""
        # 1. Determinism: Same ABHA ID yields identical UPK
        abha_1 = "91-9988-7766-5544"
        upk_a = generate_upk(abha_1)
        upk_b = generate_upk(abha_1)
        self.assertEqual(upk_a, upk_b)
        self.assertTrue(upk_a.startswith("UPK-IND-2026-"))

        # 2. Irreversibility: Raw ABHA digits are not exposed
        self.assertNotIn("9988", upk_a)
        self.assertNotIn("7766", upk_a)

        # 3. Distinctness: Different ABHA IDs yield distinct UPKs
        abha_2 = "91-1122-3344-5566"
        upk_c = generate_upk(abha_2)
        self.assertNotEqual(upk_a, upk_c)

        # 4. Cryptographic Verification
        self.assertTrue(verify_blinded_key(abha_1, upk_a, "PATIENT"))
        self.assertFalse(verify_blinded_key(abha_2, upk_a, "PATIENT"))

        # 5. Doctor UDK Determinism & Verification
        nmc_1 = "NMC-MCI-2025-78192"
        udk_a = generate_udk(nmc_1)
        udk_b = generate_udk(nmc_1)
        self.assertEqual(udk_a, udk_b)
        self.assertTrue(udk_a.startswith("UDK-IND-2026-"))
        self.assertTrue(verify_blinded_key(nmc_1, udk_a, "DOCTOR"))

        # 6. Backward compatibility with seeded national demo records
        self.assertEqual(generate_upk("91-4567-8901-2345"), "UPK-IND-2026-9041")
        self.assertEqual(generate_udk("NMC-MCI-2015-88492"), "UDK-IND-2026-4412")

if __name__ == "__main__":
    unittest.main()
