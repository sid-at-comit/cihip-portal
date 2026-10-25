"""
Authentication, Sign-In & Sign-Up Test Suite
Tests dedicated login/signin views, registration workflows, and credential validations for:
Patients, Doctors, Diagnostic Labs, Hospital Administrators, Researchers & System Admins.
"""

import unittest
import json
import urllib.parse
from server import CIHIPRequestHandler, SESSIONS
from tests.test_server_handlers import execute_mock_request
from app.database import init_db, get_db_connection

class TestLoginWorkflows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_get_login_page_default(self):
        code, headers, body = execute_mock_request("GET", "/signin")
        self.assertEqual(code, 200)
        self.assertIn(b"Patient & Citizen Login", body)
        self.assertIn(b"ABHA Number", body)
        self.assertIn(b"Doctor", body)
        self.assertIn(b"Diagnostic Lab", body)
        self.assertIn(b"Hospital Admin", body)

    def test_02_get_login_page_roles(self):
        roles_to_check = [
            ("DOCTOR", b"Clinical Practitioner Login", b"NMC Registration Number"),
            ("LAB_TECHNICIAN", b"Diagnostic Laboratory Portal", b"NABL Certificate Number"),
            ("HOSPITAL_ADMIN", b"Hospital Facility Administration", b"HFR Facility Registry ID"),
            ("RESEARCHER", b"ICMR Epidemiological Research Gateway", b"Researcher Registry ID"),
            ("SYSTEM_ADMIN", b"Zero-Trust SecOps Administration", b"Security Admin Username")
        ]
        for role, title_bytes, label_bytes in roles_to_check:
            code, _, body = execute_mock_request("GET", f"/signin?role={role}")
            self.assertEqual(code, 200)
            self.assertIn(title_bytes, body)
            self.assertIn(label_bytes, body)

    def test_03_get_service_specific_signin_urls(self):
        urls = [
            ("/signin/patient", b"Patient & Citizen Login"),
            ("/signin/doctor", b"Clinical Practitioner Login"),
            ("/signin/lab", b"Diagnostic Laboratory Portal"),
            ("/signin/hospital", b"Hospital Facility Administration")
        ]
        for u, expected_text in urls:
            code, _, body = execute_mock_request("GET", u)
            self.assertEqual(code, 200)
            self.assertIn(expected_text, body)

    def test_04_get_signup_pages(self):
        urls = [
            ("/signup", b"Register as Patient"),
            ("/signup/patient", b"Register as Patient"),
            ("/signup/doctor", b"Register as Doctor"),
            ("/signup/lab", b"Register as Lab Technician"),
            ("/signup/hospital", b"Register as Hospital Admin")
        ]
        for u, expected_text in urls:
            code, _, body = execute_mock_request("GET", u)
            self.assertEqual(code, 200)
            self.assertIn(expected_text, body)

    def test_05_post_login_patient_success(self):
        # Login with username
        post_data = urllib.parse.urlencode({
            "role": "PATIENT",
            "identifier": "patient_rajesh",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signin", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/patient")
        self.assertIn("cihip_session", headers.get("set-cookie", ""))

        # Login with ABHA number
        post_data_abha = urllib.parse.urlencode({
            "role": "PATIENT",
            "identifier": "91-4567-8901-2345",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/login", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data_abha)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/patient")

    def test_06_post_login_doctor_success(self):
        # Login with NMC Registration
        post_data = urllib.parse.urlencode({
            "role": "DOCTOR",
            "identifier": "NMC-MCI-2015-88492",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signin", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/doctor")
        self.assertIn("cihip_session", headers.get("set-cookie", ""))

    def test_07_post_login_lab_success(self):
        # Login with NABL Certificate
        post_data = urllib.parse.urlencode({
            "role": "LAB_TECHNICIAN",
            "identifier": "NABL-MED-2024-9912",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signin", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/lab")
        self.assertIn("cihip_session", headers.get("set-cookie", ""))

    def test_08_post_login_hospital_success(self):
        # Login with HFR ID
        post_data = urllib.parse.urlencode({
            "role": "HOSPITAL_ADMIN",
            "identifier": "HFR-DEL-000101",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signin", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/hospital")
        self.assertIn("cihip_session", headers.get("set-cookie", ""))

    def test_09_post_login_invalid_credentials(self):
        post_data = urllib.parse.urlencode({
            "role": "PATIENT",
            "identifier": "wrong_patient",
            "password": "IncorrectPassword"
        }).encode("utf-8")
        code, _, body = execute_mock_request("POST", "/signin", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 401)
        self.assertIn(b"Invalid identifier or password", body)

    def test_10_post_signup_patient_success(self):
        post_data = urllib.parse.urlencode({
            "role": "PATIENT",
            "name": "Manish Gupta",
            "abha_number": "91-9988-1122-3344",
            "dob": "1994-08-12",
            "gender": "Male",
            "blood_group": "A+",
            "state": "Uttar Pradesh",
            "district": "Noida",
            "pincode": "201301",
            "phone": "+91 98990 12345",
            "email": "manish.gupta@example.com",
            "username": "manish_gupta_94",
            "password": "SecurePassword@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signup", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/patient")
        self.assertIn("cihip_session", headers.get("set-cookie", ""))

        # Verify patient exists in DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients WHERE abha_number = '91-9988-1122-3344'")
        pat = cur.fetchone()
        self.assertIsNotNone(pat)
        self.assertEqual(pat["name"], "Manish Gupta")
        self.assertTrue(pat["upk"].startswith("UPK-IND-"))
        conn.close()

    def test_11_post_signup_doctor_success(self):
        post_data = urllib.parse.urlencode({
            "role": "DOCTOR",
            "name": "Dr. Rohit Saxena, MS",
            "nmc_id": "NMC-MCI-2023-99182",
            "specialty": "Cardiology",
            "hospital_id": "HOSP-AIIMS-DEL",
            "qualification": "MBBS, MS, MCh (Cardio)",
            "phone": "+91 98112 33445",
            "email": "dr.rohit@aiims.edu.in",
            "username": "dr_rohit_saxena",
            "password": "SecureDoctor@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signup", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/doctor")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM doctors WHERE nmc_id = 'NMC-MCI-2023-99182'")
        doc = cur.fetchone()
        self.assertIsNotNone(doc)
        self.assertEqual(doc["specialty"], "Cardiology")
        self.assertTrue(doc["udk"].startswith("UDK-IND-"))
        conn.close()

    def test_15_unauthenticated_role_redirects(self):
        # Protected endpoints must redirect unauthenticated visitors to clean sign-in pages
        protected_routes = [
            ("/patient", "/signin/patient"),
            ("/doctor", "/signin/doctor"),
            ("/lab", "/signin/lab"),
            ("/hospital", "/signin/hospital"),
            ("/research", "/signin/researcher"),
            ("/admin/security", "/signin/admin")
        ]
        for route, expected_redirect in protected_routes:
            code, hdrs, _ = execute_mock_request("GET", route)
            self.assertEqual(code, 302)
            self.assertEqual(hdrs.get("location"), expected_redirect)

if __name__ == "__main__":
    unittest.main()
