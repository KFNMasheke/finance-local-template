"""Exercise simultaneous loopback saves and verify that SQLite connections close."""
import concurrent.futures
import http.client
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

import server

STATE = {"version": 1, "transactions": [], "income": [], "budgets": [],
         "debts": [], "audits": [], "settings": {}}


class ConcurrentPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db, self.previous_port = server.DB, server.PORT
        server.DB = Path(self.tmp.name) / "data" / "finance.sqlite3"
        self.http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        server.PORT = self.http.server_address[1]
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(timeout=5)
        server.DB, server.PORT = self.previous_db, self.previous_port
        self.tmp.cleanup()

    def request(self, method, data=None):
        connection = http.client.HTTPConnection("127.0.0.1", server.PORT, timeout=20)
        try:
            headers = {"X-Finance-Local": "1",
                       "Origin": f"http://127.0.0.1:{server.PORT}",
                       "Content-Type": "application/json"}
            connection.request(method, "/api/state", body=data, headers=headers)
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def test_concurrent_writers_are_committed_without_lost_inserts(self):
        workers = 12
        gate = threading.Barrier(workers)
        payload = json.dumps(STATE)

        def save(_):
            gate.wait(timeout=10)
            return self.request("POST", payload)

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(save, range(workers)))
        self.assertTrue(all(status == 200 for status, _ in results), results)
        with server.connection() as db:
            count = db.execute("SELECT COUNT(*) FROM states").fetchone()[0]
        self.assertEqual(count, workers)
        status, raw = self.request("GET")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw), STATE)

    def test_context_manager_closes_connection_after_success_and_failure(self):
        with server.connection() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM states").fetchone()[0], 0)
        with self.assertRaises(sqlite3.ProgrammingError):
            db.execute("SELECT 1")

        with self.assertRaisesRegex(ValueError, "rollback"):
            with server.connection() as failed:
                failed.execute("INSERT INTO states(body) VALUES (?)", (json.dumps(STATE),))
                raise ValueError("rollback")
        with self.assertRaises(sqlite3.ProgrammingError):
            failed.execute("SELECT 1")
        with server.connection() as fresh:
            self.assertEqual(fresh.execute("SELECT COUNT(*) FROM states").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
