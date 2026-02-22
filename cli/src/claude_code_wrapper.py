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

Auth: 65537 | Status: Experimental (local wrapper)
"""

import os
import sys
import json
import subprocess
import argparse
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

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
    """Wrapper for Claude CLI (local command with -p flag)"""

    def __init__(self):
        """Initialize CLI wrapper"""
        self.cli_path = self._find_cli()
        self.available = self._check_available()

    def _find_cli(self) -> str:
        """Find claude CLI in PATH"""
        # Try 'claude' first (Claude Code v2+)
        try:
            result = subprocess.run(
                ["which", "claude"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Fallback to 'claude-code' (older versions)
        try:
            result = subprocess.run(
                ["which", "claude-code"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Try direct execution to verify which works
        for cmd in ["claude", "claude-code"]:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return cmd
            except Exception:
                pass

        return "claude"  # Default to 'claude'

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

            # Build command: claude -p "prompt"
            # Note: Claude CLI has limited parameter support
            # We only pass the prompt; temperature/max_tokens would need to be
            # configured via environment or config file (if supported)
            cmd = [self.cli_path, "-p", full_prompt]

            # Claude CLI doesn't support --temperature or --max-tokens flags via CLI
            # These would need to be set via config files or environment variables
            # For now, we only pass the prompt
            if Config.DEBUG:
                logger.debug(f"Note: temperature={temperature}, max_tokens={max_tokens} requested but Claude CLI doesn't support these flags")

            if Config.DEBUG:
                logger.debug(f"Running: {' '.join(cmd[:2])} ...")

            # Execute CLI with clean environment (remove CLAUDECODE)
            env = os.environ.copy()
            env.pop('CLAUDECODE', None)  # Remove nested session blocker

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env  # Use cleaned environment
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                stderr = result.stderr
                if "cannot be launched inside another Claude Code session" in stderr:
                    logger.error("Nested Claude Code session detected.")
                    logger.error("Solution: Unset CLAUDECODE variable or run outside Claude Code")
                    logger.error(f"Command: unset CLAUDECODE && {self.cli_path} -p '{prompt[:30]}...'")
                else:
                    logger.error(f"CLI error: {stderr}")
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


class ClaudeCodeWrapper:
    """HTTP client for Claude Code Server (localhost wrapper)"""

    def __init__(self, model: str = "claude-haiku-4-5-20251001", host: str = "127.0.0.1", port: int = 8080):
        """Initialize HTTP client wrapper"""
        self.model = model
        self.host = host
        self.port = port
        self.localhost_url = f"http://{host}:{port}"
        self.server_running = self._check_server()

    def _check_server(self) -> bool:
        """Check if HTTP server is running on localhost"""
        try:
            import requests
            response = requests.get(f"{self.localhost_url}/", timeout=2)
            return response.status_code in [200, 404, 405]
        except Exception:
            return False

    def query(self, prompt: str, system: Optional[str] = None, temperature: float = 0.0, max_tokens: int = 4096) -> Optional[str]:
        """Send query to Claude Code server via HTTP"""
        try:
            import requests

            payload = {
                "prompt": prompt,
                "model": self.model,
                "stream": False,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            if system:
                payload["system"] = system

            response = requests.post(
                f"{self.localhost_url}/api/generate",
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                logger.error(f"Server error: {response.status_code}")
                return None

        except ImportError:
            logger.error("requests library not found. Install with: pip install requests")
            return None
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None

    def solve_counting(self, prompt: str) -> Optional[str]:
        """Solve counting problem via Claude Code (Counter Bypass pattern)"""
        return self.query(prompt, temperature=0.0)

    def solve_math(self, prompt: str, system: Optional[str] = None) -> Optional[str]:
        """Solve math problem via Claude Code (IMO/math pattern)"""
        return self.query(prompt, system=system, temperature=0.0)


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
        print("   Install with: pip install claude-code")
    print("\n📝 Test with curl:")
    print(f'   curl http://{host}:{port}/')
    print(f'   curl -X POST http://{host}:{port}/api/generate \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"prompt": "Hello", "stream": false}\'')
    print("\n🔗 In Python/notebooks:")
    print('   import requests')
    print(f'   r = requests.post("http://{host}:{port}/api/generate",')
    print('     json={"prompt": "What is 2+2?"})')
    print('   print(r.json()["response"])')
    print("\n⌨️  Press Ctrl+C to stop\n")
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
