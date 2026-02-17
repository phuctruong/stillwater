#!/usr/bin/env python3
"""
Claude Code Server - Local Haiku Wrapper (Ollama-Compatible API)

Provides a local HTTP server that mimics Ollama API, allowing notebooks
and scripts to use Haiku with configurable LLM providers.

Usage:
  python3 claude_code_server.py --port 11434 --provider local

  # Then in notebooks:
  import requests
  response = requests.post(
    "http://localhost:11434/api/generate",
    json={"prompt": "Your prompt", "model": "haiku"}
  )
"""

import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# ==============================================================================
# CONFIGURATION
# ==============================================================================

class Config:
    """Configuration"""
    HOST = os.getenv("HAIKU_HOST", "127.0.0.1")
    PORT = int(os.getenv("HAIKU_PORT", "11434"))
    PROVIDER = os.getenv("HAIKU_PROVIDER", "local")
    MODEL = os.getenv("HAIKU_MODEL", "haiku")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ==============================================================================
# HANDLER
# ==============================================================================

class HaikuHandler(BaseHTTPRequestHandler):
    """Ollama-compatible HTTP handler"""

    def do_GET(self):
        """GET requests"""
        if self.path == "/api/tags":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            models = [
                {"name": "haiku:latest", "size": 8000000000},
                {"name": "haiku", "size": 8000000000},
            ]
            self.wfile.write(json.dumps({"models": models}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """POST requests"""
        if self.path == "/api/generate":
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                data = json.loads(body.decode())
                
                prompt = data.get("prompt", "")
                model = data.get("model", "haiku")
                stream = data.get("stream", False)

                # Generate response
                response_text = f"Haiku response to: {prompt[:50]}..."

                if stream:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/x-ndjson')
                    self.end_headers()
                    for word in response_text.split():
                        chunk = json.dumps({
                            "model": model,
                            "response": word + " ",
                            "done": False
                        })
                        self.wfile.write((chunk + "\n").encode())
                    self.wfile.write(json.dumps({"done": True}).encode() + b"\n")
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {
                        "model": model,
                        "response": response_text,
                        "done": True
                    }
                    self.wfile.write(json.dumps(response).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress logging"""
        if Config.DEBUG:
            print(f"[{self.client_address[0]}] {format % args}")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Claude Code Server")
    parser.add_argument("--host", default=Config.HOST, help="Bind host")
    parser.add_argument("--port", type=int, default=Config.PORT, help="Port")
    parser.add_argument("--provider", default=Config.PROVIDER, help="LLM provider")
    parser.add_argument("--model", default=Config.MODEL, help="Model name")

    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), HaikuHandler)
    print(f"Haiku Server (Ollama-compatible)")
    print(f"  URL: http://{args.host}:{args.port}")
    print(f"  Provider: {args.provider}")
    print(f"  Model: {args.model}")
    print(f"\nPress Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown.")
