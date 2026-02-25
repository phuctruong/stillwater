#!/usr/bin/env python3
"""
Local Haiku 4.5 Server - Mimics Ollama API for Claude Haiku
Auth: 65537
Purpose: Run Haiku locally for SWE-bench solving via notebook

This server:
1. Accepts requests compatible with Ollama API
2. Translates them to Anthropic Claude API
3. Returns Ollama-compatible responses
4. Can be used by any notebook expecting Ollama

Usage:
  export STILLWATER_ENABLE_LEGACY_SOLVERS=1
  python3 src/swe/src/haiku_local_server.py &
  # Server runs on http://127.0.0.1:11434 by default (override with STILLWATER_HAIKU_SERVER_HOST/PORT)
  # Use in notebooks via requests to http://localhost:11434/api/generate
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import anthropic

# Configuration
HAIKU_MODEL = "claude-haiku-4-5-20251001"
# Fail-closed: bind localhost by default (do not expose to LAN).
SERVER_HOST = os.environ.get("STILLWATER_HAIKU_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.environ.get("STILLWATER_HAIKU_SERVER_PORT", "11434"))
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=API_KEY) if API_KEY else None


class HaikuLocalHandler(BaseHTTPRequestHandler):
    """HTTP request handler that proxies to Anthropic API."""

    def do_POST(self):
        """Handle POST requests (Ollama API style)."""
        path = urlparse(self.path).path

        if path == "/api/generate":
            self.handle_generate()
        elif path == "/api/tags":
            self.handle_tags()
        else:
            self.send_error(404, f"Unknown endpoint: {path}")

    def handle_generate(self):
        """Handle /api/generate endpoint (Ollama API compatible)."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body)

            # Extract Ollama request format
            prompt = request_data.get("prompt", "")
            stream = request_data.get("stream", False)
            temperature = request_data.get("temperature", 0.7)
            _ = request_data.get("model", HAIKU_MODEL)  # model field accepted but server uses HAIKU_MODEL

            if not client:
                self.send_json_error(401, "ANTHROPIC_API_KEY not set")
                return

            if not prompt:
                self.send_json_error(400, "Missing prompt")
                return

            # Call Anthropic API
            message = client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=4096,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract response text
            response_text = message.content[0].text if message.content else ""

            # Return Ollama-compatible format
            if stream:
                # Stream response (line by line)
                self.send_response(200)
                self.send_header("Content-Type", "application/x-ndjson")
                self.end_headers()

                # Send response in chunks (Ollama streaming format)
                for line in response_text.split("\n"):
                    chunk = {
                        "model": HAIKU_MODEL,
                        "created_at": "",
                        "response": line + "\n",
                        "done": False,
                    }
                    self.wfile.write(json.dumps(chunk).encode() + b"\n")

                # Send final chunk
                final = {
                    "model": HAIKU_MODEL,
                    "created_at": "",
                    "response": "",
                    "done": True,
                    "total_duration": 0,
                    "load_duration": 0,
                    "prompt_eval_count": len(prompt.split()),
                    "prompt_eval_duration": 0,
                    "eval_count": len(response_text.split()),
                    "eval_duration": 0,
                }
                self.wfile.write(json.dumps(final).encode() + b"\n")
            else:
                # Non-streaming response
                response = {
                    "model": HAIKU_MODEL,
                    "created_at": "",
                    "response": response_text,
                    "done": True,
                    "context": [],
                    "total_duration": 0,
                    "load_duration": 0,
                    "prompt_eval_count": len(prompt.split()),
                    "prompt_eval_duration": 0,
                    "eval_count": len(response_text.split()),
                    "eval_duration": 0,
                }
                self.send_json_response(response)

        except json.JSONDecodeError:
            self.send_json_error(400, "Invalid JSON in request body")
        except anthropic.APIError as e:
            self.send_json_error(500, f"Anthropic API error: {str(e)}")
        except Exception as e:
            self.send_json_error(500, f"Internal error: {str(e)}")

    def handle_tags(self):
        """Handle /api/tags endpoint (list available models)."""
        response = {
            "models": [
                {
                    "name": HAIKU_MODEL,
                    "modified_at": "2025-02-16T00:00:00Z",
                    "size": 0,
                    "digest": "stillwater-haiku-4.5",
                }
            ]
        }
        self.send_json_response(response)

    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_json_error(self, code, message):
        """Send JSON error response."""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        error = {"error": message}
        self.wfile.write(json.dumps(error).encode())

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def start_server():
    """Start the Haiku local server."""
    if os.environ.get("STILLWATER_ENABLE_LEGACY_SOLVERS") != "1":
        print("❌ Legacy/experimental tool is disabled by default.")
        print("Enable explicitly with: export STILLWATER_ENABLE_LEGACY_SOLVERS=1")
        sys.exit(2)

    if not API_KEY:
        print("❌ ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY=sk-...")
        sys.exit(1)

    server = HTTPServer((SERVER_HOST, SERVER_PORT), HaikuLocalHandler)
    print(f"✅ Haiku Local Server started on http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"   Model: {HAIKU_MODEL}")
    print(f"   Use endpoint: http://localhost:{SERVER_PORT}/api/generate")
    print(f"   List models: http://localhost:{SERVER_PORT}/api/tags")
    print("\n   To stop: Press Ctrl+C")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
        sys.exit(0)


if __name__ == "__main__":
    start_server()
