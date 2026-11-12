import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import speedtest

PAYLOAD = b"x" * 200_000


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.end_headers()
        self.wfile.write(PAYLOAD)

    def log_message(self, *args):
        pass


class DownloadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/file"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_download_returns_full_size(self):
        size, elapsed = speedtest.download(self.url)
        self.assertEqual(size, len(PAYLOAD))
        self.assertGreater(elapsed, 0)

    def test_validate_url_rejects_bad_scheme(self):
        with self.assertRaises(ValueError):
            speedtest.validate_url("ftp://example.com/file")

    def test_validate_url_rejects_empty_host(self):
        with self.assertRaises(ValueError):
            speedtest.validate_url("http://")


if __name__ == "__main__":
    unittest.main()
