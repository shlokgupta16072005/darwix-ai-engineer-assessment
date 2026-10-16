"""Minimal local dashboard server for Q4 live insights."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_FILE = BASE_DIR / "app" / "dashboard.html"

STATE = {
    "transcript": "",
    "events": [],
    "updated_at": None,
}
STATE_LOCK = threading.Lock()


class DashboardHandler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            body = HTML_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/state":
            with STATE_LOCK:
                snapshot = json.loads(json.dumps(STATE))
            self.send_json(snapshot)
            return

        self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if urlparse(self.path).path != "/api/events":
            self.send_json({"error": "Not found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1_000_000:
                self.send_json({"error": "Invalid request size"}, 400)
                return

            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object")

            transcript = payload.get("transcript", "")
            events = payload.get("events", [])

            if not isinstance(transcript, str) or not isinstance(events, list):
                raise ValueError("Invalid transcript or events")

            from datetime import datetime, timezone
            with STATE_LOCK:
                STATE["transcript"] = transcript
                STATE["events"] = events[-100:]
                STATE["updated_at"] = datetime.now(timezone.utc).isoformat()

            self.send_json({"ok": True})
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, 400)

    def log_message(self, format_string, *args):
        print("[dashboard]", format_string % args)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8765), DashboardHandler)
    print("Q4 dashboard server: http://127.0.0.1:8765")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
    finally:
        server.server_close()
