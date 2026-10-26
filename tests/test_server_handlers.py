"""
Comprehensive Mock Handler Pipeline Integration Tests
Validates complete clinical and regulatory workflows end-to-end.
"""

import unittest
import io
import json
import urllib.parse
from server import CIHIPRequestHandler, SESSIONS
from app.database import init_db, verify_audit_chain_integrity, get_db_connection

class MockSocket:
    def __init__(self, request_bytes):
        self.rfile = io.BytesIO(request_bytes)
        self.wfile = io.BytesIO()

    def sendall(self, data):
        self.wfile.write(data)

    def send(self, data):
        self.wfile.write(data)
        return len(data)

    def makefile(self, mode, *args, **kwargs):
        if "b" in mode:
            if "r" in mode:
                return self.rfile
            elif "w" in mode:
                return self.wfile
        return self.rfile

class DummyServer:
    def __init__(self):
        self.server_name = "127.0.0.1"
        self.server_port = 8080

def execute_mock_request(method: str, path: str, headers: dict = None, body: bytes = b""):
    headers = headers or {}
    if body and "Content-Length" not in headers:
        headers["Content-Length"] = str(len(body))

    header_lines = [f"{method} {path} HTTP/1.1", "Host: 127.0.0.1"]
    for k, v in headers.items():
        header_lines.append(f"{k}: {v}")
    header_raw = "\r\n".join(header_lines) + "\r\n\r\n"
    raw_req = header_raw.encode("utf-8") + body

    mock_sock = MockSocket(raw_req)
    dummy_server = DummyServer()

    handler = CIHIPRequestHandler(mock_sock, ("127.0.0.1", 12345), dummy_server)

    resp_raw = mock_sock.wfile.getvalue()
    parts = resp_raw.split(b"\r\n\r\n", 1)
    header_block = parts[0].decode("utf-8", errors="replace")
    body_block = parts[1] if len(parts) > 1 else b""

    lines = header_block.split("\r\n")
    status_line = lines[0]
    status_code = int(status_line.split()[1])

    resp_headers = {}
    for line in lines[1:]:
        if ": " in line:
            hk, hv = line.split(": ", 1)
            resp_headers[hk.lower()] = hv

    return status_code, resp_headers, body_block

class TestFullClinicalPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_landing_and_stats(self):
        code, headers, body = execute_mock_request("GET", "/")
        self.assertEqual(code, 200)
        self.assertIn(b"CIHIP National Health Exchange", body)
        self.assertIn(b"text/html", headers.get("content-type", b"").encode())

    def test_02_multilingual_switch(self):
        code, headers, body = execute_mock_request("GET", "/set-lang?lang=hi&redirect=/")
        self.assertEqual(code, 302)
        self.assertIn("cihip_lang=hi", headers.get("set-cookie", ""))

    def test_03_patient_portal_views(self):
        token = "pat_sess_rajesh"
        SESSIONS[token] = {
            "id": "USR-PAT-01",
            "role": "PATIENT",
            "entity_id": "UPK-IND-2026-9041",
            "name": "Rajesh Sharma",
            "expires_at": 9999999999
        }
        headers = {"Cookie": f"cihip_session={token}"}

        # Dashboard
        code, _, body = execute_mock_request("GET", "/patient", headers=headers)
        self.assertEqual(code, 200)
        self.assertIn(b"Rajesh Sharma", body)

        # LHR Timeline
        code, _, body = execute_mock_request("GET", "/patient/lhr", headers=headers)
        self.assertEqual(code, 200)
        self.assertIn(b"Longitudinal Health Record", body)

        # Prescription View
        code, _, body = execute_mock_request("GET", "/patient/prescription/RX-2026-801", headers=headers)
        self.assertEqual(code, 200)
        self.assertIn(b"DIGITALLY SIGNED PRESCRIPTION", body)
        self.assertIn(b"Tab. Telmisartan", body)

        # Lab Report View
        code, _, body = execute_mock_request("GET", "/patient/report/RPT-2026-501", headers=headers)
        self.assertEqual(code, 200)
        self.assertIn(b"Total Cholesterol", body)

    def test_04_patient_consent_flow(self):
        token = "pat_sess_rajesh_consent"
        SESSIONS[token] = {
            "id": "USR-PAT-01",
            "role": "PATIENT",
            "entity_id": "UPK-IND-2026-9041",
            "name": "Rajesh Sharma",
            "expires_at": 9999999999
        }
        headers = {"Cookie": f"cihip_session={token}", "Content-Type": "application/x-www-form-urlencoded"}

        # Grant Consent
        post_data = urllib.parse.urlencode({
            "requester_payload": "DOCTOR|UDK-IND-2026-6219|Dr. Amitabh Sen",
            "purpose": "Treatment",
            "resources": ["DiagnosticReport", "MedicationRequest"],
            "valid_from": "2026-10-01",
            "valid_to": "2027-10-01"
        }).encode("utf-8")
        code, _, _ = execute_mock_request("POST", "/patient/consents/grant", headers=headers, body=post_data)
        self.assertEqual(code, 302)

        # Verify in DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM consents WHERE requester_id = 'UDK-IND-2026-6219' AND status = 'GRANTED'")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        consent_id = row["consent_id"]
        conn.close()

        # Revoke Consent
        code, _, _ = execute_mock_request("POST", f"/patient/consents/{consent_id}/revoke", headers=headers)
        self.assertEqual(code, 302)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT status FROM consents WHERE consent_id = ?", (consent_id,))
        self.assertEqual(cur.fetchone()["status"], "REVOKED")
        conn.close()

    def test_05_doctor_encounter_and_pki_prescription(self):
        token = "doc_sess_priya"
        SESSIONS[token] = {
            "id": "USR-DOC-01",
            "role": "DOCTOR",
            "entity_id": "UDK-IND-2026-4412",
            "name": "Dr. Priya Nair",
            "expires_at": 9999999999
        }
        headers = {"Cookie": f"cihip_session={token}", "Content-Type": "application/x-www-form-urlencoded"}

        # Search patient
        code, _, body = execute_mock_request("GET", "/doctor/search?upk=UPK-IND-2026-9041", headers=headers)
        self.assertEqual(code, 200)
        self.assertIn(b"Rajesh Sharma", body)

        # Save Encounter
        enc_body = urllib.parse.urlencode({
            "upk": "UPK-IND-2026-9041",
            "chief_complaint": "Follow-up cardiovascular evaluation",
            "bp": "125/80 mmHg",
            "pulse": "72 bpm",
            "spo2": "99%",
            "bmi": "25.0",
            "diagnosis_payload": "53741008|Coronary Artery Disease (CAD)",
            "clinical_notes": "Statins tolerated well. Exercise routine maintained."
        }).encode("utf-8")
        code, _, _ = execute_mock_request("POST", "/doctor/encounter/save", headers=headers, body=enc_body)
        self.assertEqual(code, 302)

        # Place Diagnostic Order
        order_body = urllib.parse.urlencode({
            "upk": "UPK-IND-2026-9041",
            "test_payload": "718-7|Hemoglobin (Hb)",
            "priority": "Routine",
            "lab_id": "LAB-APEX-NABL",
            "indication": "Routine CBC panel"
        }).encode("utf-8")
        code, _, _ = execute_mock_request("POST", "/doctor/order/save", headers=headers, body=order_body)
        self.assertEqual(code, 302)

        # Issue and PKI Sign Prescription
        rx_body = urllib.parse.urlencode({
            "upk": "UPK-IND-2026-9041",
            "med_payload_1": "387584000|Tab. Atorvastatin 20 mg|20 mg|0-0-1|Oral|30 days",
            "dosage_1": "20 mg",
            "frequency_1": "0-0-1 (Bedtime)",
            "duration_1": "30 days",
            "instructions_1": "Take after dinner"
        }).encode("utf-8")
        code, _, _ = execute_mock_request("POST", "/doctor/prescribe/save", headers=headers, body=rx_body)
        self.assertEqual(code, 302)

    def test_06_lab_technician_workflow(self):
        token = "lab_sess_ramesh"
        SESSIONS[token] = {
            "id": "USR-LAB-01",
            "role": "LAB_TECHNICIAN",
            "entity_id": "LAB-APEX-NABL",
            "name": "Ramesh Verma",
            "expires_at": 9999999999
        }
        headers = {"Cookie": f"cihip_session={token}", "Content-Type": "application/x-www-form-urlencoded"}

        # View worklist
        code, _, body = execute_mock_request("GET", "/lab", headers=headers)
        self.assertEqual(code, 200)
        self.assertIn(b"Pending Test Orders Queue", body)

        # Find a pending order
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT order_id, loinc_code, test_name, upk, udk FROM service_requests WHERE status = 'SUBMITTED' LIMIT 1")
        ord_row = cur.fetchone()
        conn.close()

        if ord_row:
            result_body = urllib.parse.urlencode({
                "order_id": ord_row["order_id"],
                "upk": ord_row["upk"],
                "udk": ord_row["udk"],
                "loinc_code": ord_row["loinc_code"],
                "test_name": ord_row["test_name"],
                "result_value": "14.2",
                "ref_range": "12.0 - 16.5 g/dL",
                "interpretation": "Values within normal biological reference interval."
            }).encode("utf-8")
            code, _, _ = execute_mock_request("POST", "/lab/entry/save", headers=headers, body=result_body)
            self.assertEqual(code, 302)

    def test_07_researcher_analytics_and_export(self):
        token = "res_sess_sunita"
        SESSIONS[token] = {
            "id": "USR-RES-01",
            "role": "RESEARCHER",
            "entity_id": "ICMR-RES-2026",
            "name": "Dr. Sunita Kulkarni",
            "expires_at": 9999999999
        }
        headers = {"Cookie": f"cihip_session={token}"}

        code, _, body = execute_mock_request("GET", "/research", headers=headers)
        self.assertEqual(code, 200)
        self.assertIn(b"ICMR Epidemiological Research Gateway", body)
        self.assertIn(b"k-Anonymity", body)

        # JSON Export
        code, _, body = execute_mock_request("GET", "/api/v1/research/export?format=json")
        self.assertEqual(code, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("cohort_size", data)

        # FHIR Bundle Export
        code, _, body = execute_mock_request("GET", "/api/v1/research/export?format=fhir")
        self.assertEqual(code, 200)
        bundle = json.loads(body.decode("utf-8"))
        self.assertEqual(bundle["resourceType"], "Bundle")

    def test_08_audit_chain_blockchain_verification(self):
        token = "sec_sess_vikram"
        SESSIONS[token] = {
            "id": "USR-SYS-01",
            "role": "SYSTEM_ADMIN",
            "entity_id": "CIHIP-HQ-DELHI",
            "name": "Vikramaditya Sen",
            "expires_at": 9999999999
        }
        headers = {"Cookie": f"cihip_session={token}"}

        code, _, body = execute_mock_request("GET", "/admin/security", headers=headers)
        self.assertEqual(code, 200)
        self.assertIn(b"Cryptographic Audit Ledger", body)
        self.assertIn(b"LEDGER CHAIN INTACT & VALID", body)

        # Verify API
        code, _, body = execute_mock_request("GET", "/api/v1/audit/verify")
        self.assertEqual(code, 200)
        integrity = json.loads(body.decode("utf-8"))
        self.assertTrue(integrity["is_intact"])
        self.assertEqual(len(integrity["tampered_ids"]), 0)

    def test_09_idea_4_blinded_key_endpoint(self):
        """Test API endpoint for Idea 4 Deterministic Blinded Key Generation."""
        code, _, body = execute_mock_request("GET", "/api/v1/identity/blinded-key?type=patient&id=91-9988-7766-5544")
        self.assertEqual(code, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertTrue(data["deterministic"])
        self.assertTrue(data["verification_valid"])
        self.assertTrue(data["blinded_key"].startswith("UPK-IND-2026-"))
        self.assertEqual(data["encoding"], "Crockford Base32 (no I, L, O, U)")

        # Doctor UDK test
        code_doc, _, body_doc = execute_mock_request("GET", "/api/v1/identity/blinded-key?type=doctor&id=NMC-MCI-2024-55123")
        self.assertEqual(code_doc, 200)
        doc_data = json.loads(body_doc.decode("utf-8"))
        self.assertTrue(doc_data["blinded_key"].startswith("UDK-IND-2026-"))
        self.assertTrue(doc_data["verification_valid"])

    def test_10_not_found_404_handler(self):
        """Test 404 handler properly renders with escaped URL path."""
        code, _, body = execute_mock_request("GET", "/some/non/existent/path?query=1")
        self.assertEqual(code, 404)
        self.assertIn(b"404 - Resource Not Found", body)
        self.assertIn(b"/some/non/existent/path", body)

if __name__ == "__main__":
    unittest.main()
