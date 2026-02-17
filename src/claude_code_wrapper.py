#!/usr/bin/env python3
"""
Claude Code Wrapper - Ollama-Compatible HTTP Server

Runs as HTTP server (like Ollama) but uses local Claude Code CLI with -p flag.
This allows notebooks and scripts to use consistent API regardless of LLM provider.

Usage:
  python3 src/claude_code_wrapper.py --port 8080

  # In curl:
  curl -X POST http://localhost:8080/api/generate \\
    -H "Content-Type: application/json" \\
    -d '{"prompt": "What is 2+2?", "stream": false}'

  # In Python:
  import requests
  response = requests.post(
    "http://localhost:8080/api/generate",
    json={"prompt": "What is 2+2?"}
  )
  print(response.json()['response'])

Auth: 65537 | Status: Production Ready
"""

import os
import sys
import json
import subprocess
import argparse
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional, Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration for Claude Code Server"""
    HOST = os.getenv("CLAUDE_CODE_HOST", "127.0.0.1")
    PORT = int(os.getenv("CLAUDE_CODE_PORT", "8080"))
    MODEL = os.getenv("CLAUDE_CODE_MODEL", "claude-haiku-4-5-20251001")
    TEMPERATURE = float(os.getenv("CLAUDE_CODE_TEMPERATURE", "0.0"))
    MAX_TOKENS = int(os.getenv("CLAUDE_CODE_MAX_TOKENS", "4096"))
    TIMEOUT = int(os.getenv("CLAUDE_CODE_TIMEOUT", "120"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"


class ClaudeCodeCLI:
    """Wrapper for Claude Code CLI (local command with -p flag)"""

    def __init__(self):
        """Initialize CLI wrapper"""
        self.cli_path = self._find_cli()
        self.available = self._check_available()

    def _find_cli(self) -> str:
        """Find claude-code CLI in PATH"""
        result = subprocess.run(
            ["which", "claude-code"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "claude-code"  # Hope it's in PATH

    def _check_available(self) -> bool:
        """Check if CLI is available"""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Claude Code CLI check failed: {e}")
            return False

    def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        timeout: int = 120
    ) -> Optional[str]:
        """
        Query Claude Code CLI using -p flag

        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Temperature (0.0 = deterministic)
            max_tokens: Max tokens in response
            timeout: Command timeout in seconds

        Returns:
            Response text or None if error
        """
        if not self.available:
            return None

        try:
            # Combine system and user prompt
            full_prompt = prompt
            if system:
                full_prompt = f"{system}\n\n{prompt}"

            # Build command: claude-code -p "prompt"
            cmd = [self.cli_path, "-p", full_prompt]

            # Add optional parameters
            if temperature != 0.7:  # 0.7 is default
                cmd.extend(["--temperature", str(temperature)])

            if max_tokens != 4096:  # 4096 is default
                cmd.extend(["--max-tokens", str(max_tokens)])

            if Config.DEBUG:
                logger.debug(f"Running: {' '.join(cmd[:2])} ...")

            # Execute CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"CLI error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"CLI timed out after {timeout}s")
            return None
        except FileNotFoundError:
            logger.error(f"Claude Code CLI not found: {self.cli_path}")
            return None
        except Exception as e:
            logger.error(f"Error calling CLI: {e}")
            return None


# Global CLI instance
cli = ClaudeCodeCLI()


class OllamaCompatibleHandler(BaseHTTPRequestHandler):
    """HTTP request handler (Ollama-compatible API)"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/api/tags":
            # Ollama-compatible /api/tags endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            response = {
                "models": [
                    {"name": "claude-haiku", "size": 7000000000},
                    {"name": "claude-haiku-4-5-20251001", "size": 7000000000},
                ]
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == "/":
            # Health check
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            response = {
                "status": "ok",
                "message": "Claude Code Server (Ollama-compatible)",
                "cli_available": cli.available,
                "cli_path": cli.cli_path
            }
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not found"}).encode())

    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/api/generate":
            self._handle_generate()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not found"}).encode())

    def _handle_generate(self):
        """Handle /api/generate requests"""
        try:
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())

            prompt = data.get("prompt", "")
            model = data.get("model", Config.MODEL)
            system = data.get("system", None)
            stream = data.get("stream", False)
            temperature = float(data.get("temperature", Config.TEMPERATURE))
            max_tokens = int(data.get("max_tokens", Config.MAX_TOKENS))

            if not prompt:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "prompt required"}).encode())
                return

            # Check CLI availability
            if not cli.available:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error = {
                    "error": "Claude Code CLI not available",
                    "details": f"CLI path: {cli.cli_path}",
                    "solution": "Install with: pip install claude-code"
                }
                self.wfile.write(json.dumps(error).encode())
                return

            # Query CLI
            response_text = cli.query(
                prompt=prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=Config.TIMEOUT
            )

            if response_text is None:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "failed to generate response"}).encode())
                return

            # Send response
            self.send_response(200)

            if stream:
                # Streaming mode (NDJSON)
                self.send_header('Content-Type', 'application/x-ndjson')
                self.end_headers()

                # Stream word by word
                for word in response_text.split():
                    chunk = {
                        "model": model,
                        "response": word + " ",
                        "done": False
                    }
                    self.wfile.write((json.dumps(chunk) + "\n").encode())

                # Final chunk
                final = {
                    "model": model,
                    "response": "",
                    "done": True
                }
                self.wfile.write((json.dumps(final) + "\n").encode())

            else:
                # Non-streaming mode (JSON)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

                response = {
                    "model": model,
                    "response": response_text,
                    "done": True
                }
                self.wfile.write(json.dumps(response).encode())

        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "invalid json"}).encode())

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        """Custom logging"""
        if Config.DEBUG:
            logger.info(format % args)


def run_server(host: str = Config.HOST, port: int = Config.PORT):
    """Start the Claude Code server"""
    server = HTTPServer((host, port), OllamaCompatibleHandler)

    print("\n" + "=" * 80)
    print("CLAUDE CODE SERVER (Ollama-Compatible)")
    print("=" * 80)
    print(f"\n✅ Server running at: http://{host}:{port}")
    print(f"   CLI available: {'Yes' if cli.available else 'No'}")
    if cli.available:
        print(f"   CLI path: {cli.cli_path}")
    else:
        print(f"   CLI path: {cli.cli_path} (NOT FOUND)")
        print(f"   Install with: pip install claude-code")
    print(f"\n📝 Test with curl:")
    print(f'   curl http://{host}:{port}/')
    print(f'   curl -X POST http://{host}:{port}/api/generate \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"prompt": "Hello", "stream": false}}\'')
    print(f"\n🔗 In Python/notebooks:")
    print(f'   import requests')
    print(f'   r = requests.post("http://{host}:{port}/api/generate",')
    print(f'     json={{"prompt": "What is 2+2?"}})')
    print(f'   print(r.json()["response"])')
    print(f"\n⌨️  Press Ctrl+C to stop\n")
    print("=" * 80 + "\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server shut down cleanly")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Claude Code Server (Ollama-compatible API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start on default port (8080)
  python3 src/claude_code_wrapper.py

  # Start on custom port
  python3 src/claude_code_wrapper.py --port 11434

  # With debug logging
  DEBUG=true python3 src/claude_code_wrapper.py

  # Test with curl
  curl http://localhost:8080/
  curl -X POST http://localhost:8080/api/generate \\
    -H "Content-Type: application/json" \\
    -d '{"prompt": "2+2?", "stream": false}'
        """
    )
    parser.add_argument(
        "--host",
        default=Config.HOST,
        help=f"Bind address (default: {Config.HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=Config.PORT,
        help=f"Port to listen on (default: {Config.PORT})"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    if args.debug:
        Config.DEBUG = True
        logger.setLevel(logging.DEBUG)

    run_server(host=args.host, port=args.port)
