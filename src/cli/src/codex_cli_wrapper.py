#!/usr/bin/env python3
"""
Codex CLI Wrapper - Ollama-Compatible HTTP Server

Runs as an HTTP server but uses the local Codex CLI via `codex exec`.
This gives notebooks and scripts a stable localhost API while keeping the
actual model backend configurable through the Codex CLI itself.

Usage:
  python3 src/codex_cli_wrapper.py --port 8081

Auth: 65537 | Status: Experimental (local wrapper)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class Config:
    """Configuration for the Codex CLI wrapper server."""

    HOST = os.getenv("CODEX_WRAPPER_HOST", "127.0.0.1")
    PORT = int(os.getenv("CODEX_WRAPPER_PORT", "8081"))
    MODEL = os.getenv("CODEX_WRAPPER_MODEL", "")
    TEMPERATURE = float(os.getenv("CODEX_WRAPPER_TEMPERATURE", "0.0"))
    MAX_TOKENS = int(os.getenv("CODEX_WRAPPER_MAX_TOKENS", "4096"))
    TIMEOUT = int(os.getenv("CODEX_WRAPPER_TIMEOUT", "180"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def _scratch_dir() -> Path:
    """Return a dedicated scratch directory for wrapper artifacts."""
    repo_root = Path(__file__).resolve().parents[3]
    scratch = repo_root / "scratch" / "codex-wrapper"
    scratch.mkdir(parents=True, exist_ok=True)
    return scratch


def _playground_html(host: str, port: int) -> str:
    """Render a small browser playground for manual wrapper testing."""
    endpoint = f"http://{host}:{port}/api/generate"
    claude_url = os.getenv("CLAUDE_CODE_URL", "http://127.0.0.1:8080")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Codex Wrapper Playground</title>
  <style>
    :root {{
      --bg: #f3efe4;
      --panel: #fffaf0;
      --ink: #1d2a31;
      --line: #b7a98b;
      --accent: #0e6b5c;
      --accent-2: #d97a27;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(217,122,39,0.14), transparent 24rem),
        radial-gradient(circle at bottom right, rgba(14,107,92,0.18), transparent 26rem),
        linear-gradient(180deg, #f8f4ea 0%, var(--bg) 100%);
    }}
    main {{
      max-width: 960px;
      margin: 0 auto;
      padding: 2rem 1.25rem 3rem;
    }}
    .hero {{
      margin-bottom: 1.5rem;
      padding: 1.5rem;
      border: 1px solid rgba(29,42,49,0.08);
      border-radius: 1.25rem;
      background: rgba(255,250,240,0.84);
      backdrop-filter: blur(8px);
      box-shadow: 0 18px 44px rgba(29,42,49,0.08);
    }}
    .hero h1 {{
      margin: 0 0 0.5rem;
      font-size: clamp(2rem, 4vw, 3.5rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
    }}
    .hero p {{
      margin: 0.2rem 0;
      max-width: 48rem;
      line-height: 1.5;
    }}
    .grid {{
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }}
    .card {{
      padding: 1rem;
      border: 1px solid var(--line);
      border-radius: 1rem;
      background: var(--panel);
      box-shadow: 0 12px 28px rgba(29,42,49,0.06);
    }}
    label {{
      display: block;
      margin-bottom: 0.75rem;
      font-size: 0.9rem;
      font-weight: 600;
      letter-spacing: 0.01em;
    }}
    input, textarea {{
      width: 100%;
      margin-top: 0.35rem;
      padding: 0.8rem 0.9rem;
      border: 1px solid rgba(29,42,49,0.18);
      border-radius: 0.85rem;
      background: #fff;
      color: var(--ink);
      font: inherit;
    }}
    textarea {{
      min-height: 10rem;
      resize: vertical;
    }}
    button {{
      cursor: pointer;
      border: 0;
      border-radius: 999px;
      padding: 0.85rem 1.2rem;
      font: inherit;
      font-weight: 700;
      color: #fff;
      background: linear-gradient(135deg, var(--accent), #10433c);
    }}
    button.secondary {{
      color: var(--ink);
      background: linear-gradient(135deg, #f1ddbf, #ead0aa);
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-top: 1rem;
    }}
    .meta {{
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      font-size: 0.82rem;
      color: #516169;
    }}
    pre {{
      margin: 0;
      min-height: 16rem;
      overflow: auto;
      white-space: pre-wrap;
      border-radius: 0.9rem;
      padding: 1rem;
      background: #152126;
      color: #e8f2ef;
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      line-height: 1.45;
    }}
    .status {{
      margin-top: 0.75rem;
      min-height: 1.5rem;
      font-weight: 600;
      color: var(--accent-2);
    }}
    @media (max-width: 640px) {{
      main {{ padding: 1rem 0.9rem 2rem; }}
      .hero, .card {{ border-radius: 0.9rem; }}
      .actions {{ flex-direction: column; }}
      button {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="meta">Stillwater local webservice / Codex CLI bridge</div>
      <h1>Codex Wrapper Playground</h1>
      <p>Use this page to hit the Ollama-compatible wrapper directly from a browser.</p>
      <p class="meta">POST endpoint: {endpoint}</p>
      <p class="meta"><a href="/">Health JSON</a> · <a href="{claude_url}/playground">Open Claude Playground</a></p>
    </section>
    <section class="grid">
      <form id="prompt-form" class="card">
        <label>
          Model
          <input id="model" name="model" placeholder="Use CLI default if blank" />
        </label>
        <label>
          System prompt
          <textarea id="system" name="system" placeholder="Optional system instruction"></textarea>
        </label>
        <label>
          User prompt
          <textarea id="prompt" name="prompt" required>Reply in one sentence: what does this wrapper do?</textarea>
        </label>
        <div class="actions">
          <button type="submit">Send Request</button>
          <button type="button" class="secondary" id="health-btn">Check Health</button>
        </div>
        <div class="status" id="status"></div>
      </form>
      <section class="card">
        <div class="meta">Response</div>
        <pre id="output">Waiting for request...</pre>
      </section>
    </section>
  </main>
  <script>
    const form = document.getElementById("prompt-form");
    const output = document.getElementById("output");
    const status = document.getElementById("status");
    const healthBtn = document.getElementById("health-btn");

    async function checkHealth() {{
      status.textContent = "Checking health...";
      const res = await fetch("/");
      const data = await res.json();
      output.textContent = JSON.stringify(data, null, 2);
      status.textContent = res.ok ? "Wrapper reachable." : "Wrapper returned an error.";
    }}

    form.addEventListener("submit", async (event) => {{
      event.preventDefault();
      const payload = {{
        prompt: document.getElementById("prompt").value,
        system: document.getElementById("system").value || undefined,
        model: document.getElementById("model").value || undefined,
        stream: false
      }};

      status.textContent = "Sending request...";
      output.textContent = "";

      try {{
        const res = await fetch("/api/generate", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify(payload)
        }});
        const data = await res.json();
        output.textContent = JSON.stringify(data, null, 2);
        status.textContent = res.ok ? "Request finished." : "Request failed.";
      }} catch (error) {{
        output.textContent = String(error);
        status.textContent = "Network error.";
      }}
    }});

    healthBtn.addEventListener("click", () => {{
      checkHealth().catch((error) => {{
        output.textContent = String(error);
        status.textContent = "Health check failed.";
      }});
    }});
  </script>
</body>
</html>
"""


class CodexCLI:
    """Thin wrapper around the local Codex CLI."""

    def __init__(self):
        self.cli_path = self._find_cli()
        self.available = self._check_available()

    def _find_cli(self) -> str:
        """Find the codex CLI in PATH."""
        try:
            result = subprocess.run(
                ["which", "codex"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["codex", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "codex"
        except Exception:
            pass

        return "codex"

    def _check_available(self) -> bool:
        """Check whether the CLI can answer `--version`."""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception as exc:
            logger.warning(f"Codex CLI check failed: {exc}")
            return False

    def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: str = "",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        timeout: int = 180,
    ) -> Optional[str]:
        """Execute `codex exec` and return the final assistant message."""
        if not self.available:
            return None

        work_dir = _scratch_dir()
        output_path = work_dir / f"codex-last-{uuid.uuid4().hex}.txt"
        full_prompt = prompt if not system else f"{system}\n\n{prompt}"

        cmd = [
            self.cli_path,
            "exec",
            "--skip-git-repo-check",
            "--color",
            "never",
            "--sandbox",
            "read-only",
            "--cd",
            str(work_dir),
            "--output-last-message",
            str(output_path),
        ]
        if model:
            cmd.extend(["--model", model])
        cmd.append(full_prompt)

        if Config.DEBUG:
            logger.debug(
                "Running Codex CLI request with model=%r temperature=%s max_tokens=%s",
                model or "<default>",
                temperature,
                max_tokens,
            )

        env = os.environ.copy()
        for key in list(env):
            if key.startswith("CODEX_"):
                env.pop(key, None)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir,
                env=env,
            )

            if result.returncode != 0:
                stderr = result.stderr.strip() or result.stdout.strip()
                if "cannot access session files" in stderr.lower():
                    logger.error("Codex CLI cannot access session files in ~/.codex.")
                    logger.error("Solution: fix ~/.codex permissions or run outside a restricted sandbox.")
                else:
                    logger.error(f"Codex CLI error: {stderr}")
                return None

            if not output_path.exists():
                logger.error("Codex CLI returned success but produced no output file.")
                return None

            response = output_path.read_text(encoding="utf-8").strip()
            return response or None

        except subprocess.TimeoutExpired:
            logger.error(f"Codex CLI timed out after {timeout}s")
            return None
        except FileNotFoundError:
            logger.error(f"Codex CLI not found: {self.cli_path}")
            return None
        except Exception as exc:
            logger.error(f"Error calling Codex CLI: {exc}")
            return None
        finally:
            try:
                output_path.unlink(missing_ok=True)
            except Exception:
                pass


cli = CodexCLI()


class CodexCLIWrapper:
    """HTTP client for the local Codex wrapper server."""

    def __init__(
        self, model: str = "codex-default", host: str = "127.0.0.1", port: int = 8081
    ):
        self.model = model
        self.host = host
        self.port = port
        self.localhost_url = f"http://{host}:{port}"
        self.server_running = self._check_server()

    def _check_server(self) -> bool:
        try:
            import requests

            response = requests.get(f"{self.localhost_url}/", timeout=2)
            return response.status_code in (200, 404, 405)
        except Exception:
            return False

    def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> Optional[str]:
        try:
            import requests

            payload = {
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if self.model:
                payload["model"] = self.model
            if system:
                payload["system"] = system

            response = requests.post(
                f"{self.localhost_url}/api/generate", json=payload, timeout=Config.TIMEOUT
            )
            if response.status_code != 200:
                logger.error(f"Server error: {response.status_code}")
                return None

            data = response.json()
            return data.get("response", "")
        except ImportError:
            logger.error("requests library not found. Install with: pip install requests")
            return None
        except Exception as exc:
            logger.error(f"Query failed: {exc}")
            return None


class OllamaCompatibleHandler(BaseHTTPRequestHandler):
    """HTTP handler serving a minimal Ollama-compatible API."""

    def do_GET(self):
        if self.path == "/api/tags":
            self._send_json(
                200,
                {
                    "models": [
                        {"name": Config.MODEL or "codex-default", "size": 0},
                    ]
                },
            )
            return

        if self.path == "/":
            self._send_json(
                200,
                {
                    "status": "ok",
                    "message": "Codex CLI Server (Ollama-compatible)",
                    "cli_available": cli.available,
                    "cli_path": cli.cli_path,
                },
            )
            return

        if self.path == "/playground":
            html = _playground_html(Config.HOST, Config.PORT)
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/api/generate":
            self._handle_generate()
            return
        self._send_json(404, {"error": "not found"})

    def _handle_generate(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length)
            data = json.loads(raw_body.decode("utf-8"))

            prompt = data.get("prompt", "")
            if not prompt:
                self._send_json(400, {"error": "prompt required"})
                return

            model = data.get("model", Config.MODEL)
            system = data.get("system")
            stream = data.get("stream", False)
            temperature = float(data.get("temperature", Config.TEMPERATURE))
            max_tokens = int(data.get("max_tokens", Config.MAX_TOKENS))

            if not cli.available:
                self._send_json(
                    503,
                    {
                        "error": "Codex CLI not available",
                        "details": f"CLI path: {cli.cli_path}",
                        "solution": "Install Codex CLI and ensure `codex --version` succeeds.",
                    },
                )
                return

            response_text = cli.query(
                prompt=prompt,
                system=system,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=Config.TIMEOUT,
            )
            if response_text is None:
                self._send_json(500, {"error": "failed to generate response"})
                return

            if stream:
                self.send_response(200)
                self.send_header("Content-Type", "application/x-ndjson")
                self.end_headers()
                for word in response_text.split():
                    chunk = {
                        "model": model or Config.MODEL or "codex-default",
                        "response": word + " ",
                        "done": False,
                    }
                    self.wfile.write((json.dumps(chunk) + "\n").encode("utf-8"))
                final = {
                    "model": model or Config.MODEL or "codex-default",
                    "response": "",
                    "done": True,
                }
                self.wfile.write((json.dumps(final) + "\n").encode("utf-8"))
                return

            self._send_json(
                200,
                {
                    "model": model or Config.MODEL or "codex-default",
                    "response": response_text,
                    "done": True,
                },
            )

        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid json"})
        except Exception as exc:
            logger.error(f"Error handling request: {exc}")
            self._send_json(500, {"error": str(exc)})

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        if Config.DEBUG:
            logger.info(format % args)


def run_server(host: str = Config.HOST, port: int = Config.PORT):
    """Start the Codex CLI wrapper server."""
    server = HTTPServer((host, port), OllamaCompatibleHandler)

    print("\n" + "=" * 80)
    print("CODEX CLI SERVER (Ollama-Compatible)")
    print("=" * 80)
    print(f"\nServer running at: http://{host}:{port}")
    print(f"CLI available: {'Yes' if cli.available else 'No'}")
    if cli.available:
        print(f"CLI path: {cli.cli_path}")
    else:
        print(f"CLI path: {cli.cli_path} (NOT FOUND)")
        print("Install Codex CLI and ensure `codex --version` works.")
    print("\nTest endpoints:")
    print(f"  curl http://{host}:{port}/")
    print(f"  curl http://{host}:{port}/playground")
    print(f"  curl -X POST http://{host}:{port}/api/generate \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"prompt": "Reply exactly: OK", "stream": false}\'')
    print("\nPress Ctrl+C to stop\n")
    print("=" * 80 + "\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shut down cleanly")
        sys.exit(0)
    except Exception as exc:
        print(f"\nServer error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Codex CLI Server (Ollama-compatible API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 src/codex_cli_wrapper.py
  python3 src/codex_cli_wrapper.py --port 8081
  DEBUG=true python3 src/codex_cli_wrapper.py
        """,
    )
    parser.add_argument("--host", default=Config.HOST, help=f"Bind address (default: {Config.HOST})")
    parser.add_argument("--port", type=int, default=Config.PORT, help=f"Port to listen on (default: {Config.PORT})")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        Config.DEBUG = True
        logger.setLevel(logging.DEBUG)

    run_server(host=args.host, port=args.port)
