# /// script
# requires-python = ">=3.11"
# ///
"""Dev server for poster development with live-reload and inline editing."""

import json
import os
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

EDITS_FILE = Path("edits.json")
PORT = 8787


class PosterHandler(SimpleHTTPRequestHandler):
    def do_HEAD(self):
        """Serve HEAD requests (for auto-reload polling) without logging."""
        self._send_file_headers()

    def do_GET(self):
        if self.path == "/edits":
            self._serve_edits()
        elif self.path == "/poster.html":
            self._serve_poster()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/edits":
            self._save_edit()
        elif self.path == "/edits/clear":
            self._clear_edits()
        else:
            self.send_error(404)

    def _serve_poster(self):
        path = Path("poster.html")
        if not path.exists():
            self.send_error(404)
            return
        content = path.read_bytes()
        mtime = os.path.getmtime(path)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Last-Modified", self.date_time_string(mtime))
        self.end_headers()
        self.wfile.write(content)

    def _send_file_headers(self):
        path = Path("poster.html")
        if not path.exists():
            self.send_error(404)
            return
        mtime = os.path.getmtime(path)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Last-Modified", self.date_time_string(mtime))
        self.end_headers()

    def _serve_edits(self):
        edits = self._read_edits()
        body = json.dumps(edits).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _save_edit(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length))
        edits = self._read_edits()
        edits[data["key"]] = data["value"]
        EDITS_FILE.write_text(json.dumps(edits, indent=2))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def _clear_edits(self):
        EDITS_FILE.write_text("{}")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def _read_edits(self) -> dict:
        if EDITS_FILE.exists():
            return json.loads(EDITS_FILE.read_text())
        return {}

    def log_message(self, format, *args):
        # Suppress HEAD request logging to reduce noise
        if len(args) >= 1 and isinstance(args[0], str) and args[0].startswith("HEAD"):
            return
        super().log_message(format, *args)


if __name__ == "__main__":
    server = HTTPServer(("", PORT), PosterHandler)
    print(f"Serving on http://localhost:{PORT}")
    print(f"Open http://localhost:{PORT}/poster.html in your browser")
    server.serve_forever()
