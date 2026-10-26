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

    def test_12_signup_missing_email_rejected(self):
        post_data = urllib.parse.urlencode({
            "role": "PATIENT",
            "name": "Arun Verma",
            "abha_number": "91-9988-5544-3322",
            "username": "arun_verma_99",
            "password": "SecurePassword@123",
            "email": ""  # Missing mandatory email
        }).encode("utf-8")
        code, _, body = execute_mock_request("POST", "/signup", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 400)
        self.assertIn(b"Email Address is mandatory", body)

    def test_13_signup_with_invalid_otp_rejected(self):
        post_data = urllib.parse.urlencode({
            "role": "PATIENT",
            "name": "Kavita Rao",
            "abha_number": "91-9988-7711-2233",
            "username": "kavita_rao_26",
            "password": "SecurePassword@123",
            "email": "kavita.rao@example.com",
            "otp_code": "000000"  # Invalid OTP
        }).encode("utf-8")
        code, _, body = execute_mock_request("POST", "/signup", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 400)
        self.assertIn(b"OTP Verification Failed", body)

    def test_14_signup_with_valid_otp_success(self):
        # 1. Request OTP via API
        send_data = urllib.parse.urlencode({"email": "alok.singh@example.com"}).encode("utf-8")
        code, _, body = execute_mock_request("POST", "/api/v1/auth/send-otp", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=send_data)
        self.assertEqual(code, 200)
        otp_json = json.loads(body.decode("utf-8"))
        self.assertTrue(otp_json.get("success"))
        dispatched_otp = otp_json.get("otp")
        self.assertEqual(len(dispatched_otp), 6)

        # 2. Complete registration with generated OTP
        signup_data = urllib.parse.urlencode({
            "role": "PATIENT",
            "name": "Alok Singh",
            "abha_number": "91-8877-6655-4433",
            "dob": "1988-03-21",
            "gender": "Male",
            "blood_group": "O+",
            "state": "Haryana",
            "district": "Gurugram",
            "pincode": "122001",
            "phone": "+91 98119 88776",
            "email": "alok.singh@example.com",
            "username": "alok_singh_88",
            "password": "SecurePassword@123",
            "otp_code": dispatched_otp
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signup", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=signup_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/patient")

    def test_16_login_with_registered_email_success(self):
        # Login Patient with Email
        post_pat = urllib.parse.urlencode({
            "role": "PATIENT",
            "identifier": "rajesh.sharma@example.com",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signin", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_pat)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/patient")

        # Login Doctor with Email
        post_doc = urllib.parse.urlencode({
            "role": "DOCTOR",
            "identifier": "dr.priya.nair@aiims.edu.in",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signin", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_doc)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/doctor")

        # Login Hospital Admin with Email
        post_hosp = urllib.parse.urlencode({
            "role": "HOSPITAL_ADMIN",
            "identifier": "admin@aiims.edu.in",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/signin", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_hosp)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/hospital")

    def test_17_otp_api_endpoints(self):
        # Send OTP
        send_data = urllib.parse.urlencode({"email": "dr.verma@apex.in"}).encode("utf-8")
        code, _, body = execute_mock_request("POST", "/api/v1/auth/send-otp", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=send_data)
        self.assertEqual(code, 200)
        resp = json.loads(body.decode("utf-8"))
        otp = resp["otp"]

        # Verify correct OTP
        verify_data = urllib.parse.urlencode({"email": "dr.verma@apex.in", "otp_code": otp}).encode("utf-8")
        code, _, body = execute_mock_request("POST", "/api/v1/auth/verify-otp", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=verify_data)
        self.assertEqual(code, 200)
        resp2 = json.loads(body.decode("utf-8"))
        self.assertTrue(resp2["verified"])

        # Verify incorrect OTP
        wrong_data = urllib.parse.urlencode({"email": "dr.verma@apex.in", "otp_code": "000000"}).encode("utf-8")
        code, _, body = execute_mock_request("POST", "/api/v1/auth/verify-otp", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=wrong_data)
        self.assertEqual(code, 400)

        # Universal demo OTP bypass 123456
        demo_data = urllib.parse.urlencode({"email": "anyuser@health.gov.in", "otp_code": "123456"}).encode("utf-8")
        code, _, body = execute_mock_request("POST", "/api/v1/auth/verify-otp", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=demo_data)
        self.assertEqual(code, 200)

    def test_18_verify_otp_view_workflow(self):
        # GET /verify-otp
        code, _, body = execute_mock_request("GET", "/verify-otp?email=patient@test.com&role=PATIENT")
        self.assertEqual(code, 200)
        self.assertIn(b"Email Verification Required", body)

        # POST /verify-otp with valid demo OTP
        post_data = urllib.parse.urlencode({
            "email": "patient@test.com",
            "role": "PATIENT",
            "otp_code": "123456"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/verify-otp", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertIn("/signin?role=PATIENT", headers.get("location"))

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
