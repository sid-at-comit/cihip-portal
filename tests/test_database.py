"""
Unit and Integration Tests for CIHIP Database Layer & Visual Database Explorer
Centralized Indian Healthcare Information Portal (CIHIP) - Phase 1
"""

import unittest
import json
import io
import csv
from app.database import (
    init_db, get_db_connection, get_db_engine_info, get_database_stats,
    get_table_data, execute_explorer_query, export_table_data,
    translate_sql_for_pg, TABLE_SCHEMAS
)
from server import CIHIPRequestHandler, SESSIONS

class DummySocket:
    def __init__(self, request_bytes: bytes):
        self.rfile = io.BytesIO(request_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if 'b' in mode:
            if 'r' in mode:
                return self.rfile
            elif 'w' in mode:
                return self.wfile
        raise ValueError("Unknown mode")

    def sendall(self, data):
        self.wfile.write(data)

def simulate_http_request(method: str, path: str, body: str = "", headers: dict = None) -> tuple[int, dict, str]:
    """Execute request directly through CIHIPRequestHandler without opening network sockets."""
    hdrs = headers or {}
    body_bytes = body.encode("utf-8")
    req_lines = [f"{method} {path} HTTP/1.1", "Host: localhost:8080"]
    for k, v in hdrs.items():
        req_lines.append(f"{k}: {v}")
    if body and "Content-Length" not in hdrs:
        req_lines.append(f"Content-Length: {len(body_bytes)}")
    if body and "Content-Type" not in hdrs:
        req_lines.append("Content-Type: application/x-www-form-urlencoded")
    req_lines.append("")
    raw_header = "\r\n".join(req_lines).encode("utf-8") + b"\r\n"
    raw_req = raw_header + body_bytes

    sock = DummySocket(raw_req)
    CIHIPRequestHandler(sock, ("127.0.0.1", 54321), None)

    response_bytes = sock.wfile.getvalue()
    parts = response_bytes.split(b"\r\n\r\n", 1)
    status_header = parts[0].decode("utf-8", errors="replace")
    resp_body = parts[1].decode("utf-8", errors="replace") if len(parts) > 1 else ""

    lines = status_header.split("\r\n")
    status_code = int(lines[0].split()[1]) if lines and len(lines[0].split()) > 1 else 500
    resp_headers = {}
    for line in lines[1:]:
        if ":" in line:
            hk, hv = line.split(":", 1)
            resp_headers[hk.strip().lower()] = hv.strip()

    return status_code, resp_headers, resp_body

class TestDatabaseLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_db_engine_info(self):
        info = get_db_engine_info()
        self.assertIn("engine", info)
        self.assertIn("display_name", info)
        self.assertIn("status", info)
        self.assertIn("driver", info)
        self.assertIn(info["engine"], ("sqlite", "postgresql"))

    def test_02_database_stats(self):
        stats = get_database_stats()
        self.assertIn("engine", stats)
        self.assertIn("table_counts", stats)
        self.assertIn("total_records", stats)

        counts = stats["table_counts"]
        # Verify core tables are present and seeded
        for tbl in ("users", "patients", "doctors", "hospitals", "labs", "encounters", "prescriptions"):
            self.assertIn(tbl, counts)
            self.assertGreater(counts[tbl], 0, f"Table {tbl} should have seeded rows")

        self.assertGreater(stats["total_records"], 20)

    def test_03_get_table_data_pagination(self):
        # Page 1
        p1 = get_table_data("patients", limit=2, offset=0)
        self.assertEqual(p1["table_name"], "patients")
        self.assertEqual(len(p1["rows"]), 2)
        self.assertEqual(p1["current_page"], 1)
        self.assertIn("columns", p1)
        self.assertIn("primary_key", p1)
        self.assertEqual(p1["primary_key"], "upk")

        # Page 2
        p2 = get_table_data("patients", limit=2, offset=2)
        self.assertEqual(p2["current_page"], 2)
        self.assertGreaterEqual(len(p2["rows"]), 1)
        # Ensure rows are distinct
        self.assertNotEqual(p1["rows"][0]["upk"], p2["rows"][0]["upk"])

    def test_04_translate_sql_for_pg(self):
        # Simple parameter placeholders
        sql = "SELECT * FROM users WHERE username = ? AND role = ?"
        translated = translate_sql_for_pg(sql)
        self.assertEqual(translated, "SELECT * FROM users WHERE username = %s AND role = %s")

        # Question mark within quotes should be preserved
        quoted = "SELECT * FROM notes WHERE text = 'Is this working?' AND author = ?"
        tr_quoted = translate_sql_for_pg(quoted)
        self.assertEqual(tr_quoted, "SELECT * FROM notes WHERE text = 'Is this working?' AND author = %s")

        # rowid ordering replacement
        rowid_sql = "SELECT * FROM audit_events ORDER BY rowid DESC LIMIT 10"
        tr_rowid = translate_sql_for_pg(rowid_sql)
        self.assertIn("ORDER BY timestamp DESC, audit_id DESC", tr_rowid)

    def test_05_execute_explorer_query_select(self):
        res = execute_explorer_query("SELECT upk, name, state, gender FROM patients WHERE gender = 'Male';")
        self.assertTrue(res["success"])
        self.assertGreaterEqual(res["row_count"], 1)
        self.assertIn("upk", res["columns"])
        self.assertIn("name", res["columns"])
        self.assertGreater(res["execution_ms"], 0)

    def test_06_execute_explorer_query_safety_guardrails(self):
        # Mutations must be blocked
        drop_res = execute_explorer_query("DROP TABLE users;")
        self.assertFalse(drop_res["success"])
        self.assertIn("blocked", drop_res["error"].lower())

        delete_res = execute_explorer_query("DELETE FROM encounters;")
        self.assertFalse(delete_res["success"])
        self.assertIn("blocked", delete_res["error"].lower())

        insert_res = execute_explorer_query("INSERT INTO users VALUES ('x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x');")
        self.assertFalse(insert_res["success"])

        # Non-select statements
        update_res = execute_explorer_query("UPDATE patients SET name = 'Hacked';")
        self.assertFalse(update_res["success"])

    def test_07_export_table_data_json_and_csv(self):
        # JSON export
        content_json, ctype_json, fname_json = export_table_data("patients", "json")
        self.assertEqual(ctype_json, "application/json; charset=utf-8")
        self.assertTrue(fname_json.endswith(".json"))
        parsed = json.loads(content_json)
        self.assertIsInstance(parsed, list)
        self.assertGreaterEqual(len(parsed), 4)

        # CSV export
        content_csv, ctype_csv, fname_csv = export_table_data("hospitals", "csv")
        self.assertEqual(ctype_csv, "text/csv; charset=utf-8")
        self.assertTrue(fname_csv.endswith(".csv"))
        reader = list(csv.reader(io.StringIO(content_csv)))
        self.assertGreaterEqual(len(reader), 5)  # header + 4 rows
        self.assertEqual(reader[0][0], "hospital_id")

class TestDatabaseExplorerEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_10_get_database_explorer_page(self):
        code, hdrs, body = simulate_http_request("GET", "/admin/database")
        self.assertEqual(code, 200)
        self.assertIn("CIHIP Database Explorer & Schema Hub", body)
        self.assertIn("Relational Tables", body)
        self.assertIn("patients", body)
        self.assertIn("hospitals", body)
        self.assertIn("Interactive SQL Console", body)

    def test_11_get_database_explorer_specific_table(self):
        code, hdrs, body = simulate_http_request("GET", "/admin/database?table=doctors")
        self.assertEqual(code, 200)
        self.assertIn("doctors", body)
        self.assertIn("Dr. Priya Nair", body)
        self.assertIn("Cardiology", body)

    def test_12_export_endpoint_json(self):
        code, hdrs, body = simulate_http_request("GET", "/admin/database/export?table=patients&format=json")
        self.assertEqual(code, 200)
        self.assertIn("application/json", hdrs.get("content-type", ""))
        self.assertIn("attachment", hdrs.get("content-disposition", ""))
        parsed = json.loads(body)
        self.assertIsInstance(parsed, list)

    def test_13_export_endpoint_csv(self):
        code, hdrs, body = simulate_http_request("GET", "/admin/database/export?table=hospitals&format=csv")
        self.assertEqual(code, 200)
        self.assertIn("text/csv", hdrs.get("content-type", ""))
        self.assertIn("attachment", hdrs.get("content-disposition", ""))
        self.assertIn("hospital_id", body)
        self.assertIn("AIIMS", body)

    def test_14_post_database_query_runner(self):
        post_data = "sql=SELECT+hospital_id%2C+name%2C+state+FROM+hospitals&table=hospitals"
        code, hdrs, body = simulate_http_request("POST", "/admin/database/query", body=post_data)
        self.assertEqual(code, 200)
        self.assertIn("Query Successful", body)
        self.assertIn("AIIMS", body)
        self.assertIn("Apollo Hospitals", body)

if __name__ == "__main__":
    unittest.main()
