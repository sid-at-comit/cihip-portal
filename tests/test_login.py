"""
Authentication & Login Page Test Suite
Tests dedicated login views and credentials authentication for:
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
        code, headers, body = execute_mock_request("GET", "/login")
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
            code, _, body = execute_mock_request("GET", f"/login?role={role}")
            self.assertEqual(code, 200)
            self.assertIn(title_bytes, body)
            self.assertIn(label_bytes, body)

    def test_03_post_login_patient_success(self):
        # Login with username
        post_data = urllib.parse.urlencode({
            "role": "PATIENT",
            "identifier": "patient_rajesh",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/login", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
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

    def test_04_post_login_doctor_success(self):
        # Login with NMC Registration
        post_data = urllib.parse.urlencode({
            "role": "DOCTOR",
            "identifier": "NMC-MCI-2015-88492",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/login", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/doctor")
        self.assertIn("cihip_session", headers.get("set-cookie", ""))

    def test_05_post_login_lab_success(self):
        # Login with NABL Certificate
        post_data = urllib.parse.urlencode({
            "role": "LAB_TECHNICIAN",
            "identifier": "NABL-MED-2024-9912",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/login", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/lab")
        self.assertIn("cihip_session", headers.get("set-cookie", ""))

    def test_06_post_login_hospital_success(self):
        # Login with HFR ID
        post_data = urllib.parse.urlencode({
            "role": "HOSPITAL_ADMIN",
            "identifier": "HFR-DEL-000101",
            "password": "Admin@123"
        }).encode("utf-8")
        code, headers, _ = execute_mock_request("POST", "/login", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 302)
        self.assertEqual(headers.get("location"), "/hospital")
        self.assertIn("cihip_session", headers.get("set-cookie", ""))

    def test_07_post_login_invalid_credentials(self):
        post_data = urllib.parse.urlencode({
            "role": "PATIENT",
            "identifier": "wrong_patient",
            "password": "IncorrectPassword"
        }).encode("utf-8")
        code, _, body = execute_mock_request("POST", "/login", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=post_data)
        self.assertEqual(code, 401)
        self.assertIn(b"Invalid identifier or password", body)

if __name__ == "__main__":
    unittest.main()
