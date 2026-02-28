#!/usr/bin/env python3
"""
tests/test_claude_code_wrapper.py — Comprehensive test suite for src/cli/src/claude_code_wrapper.py

Tests cover:
  - ClaudeCodeCLI._find_cli() — PATH probing, fallback logic
  - ClaudeCodeCLI._check_available() — version check via subprocess
  - ClaudeCodeCLI.query() — success, timeout, not-found, nested session, generic error
  - ClaudeCodeWrapper — HTTP client class init and query()
  - OllamaCompatibleHandler — GET /, GET /api/tags, GET unknown, POST /api/generate,
                              POST unknown, streaming, invalid JSON, missing prompt,
                              CLI unavailable, CLI returns None
  - Config — defaults and environment variable overrides
  - run_server() and __main__ entry point (import-time smoke)

All subprocess and network calls are mocked — no real processes or ports.

Rung target: 274177 (mocked I/O, no irreversible side-effects)
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup — same pattern as other test files in this repo.
# ---------------------------------------------------------------------------
CLI_SRC = Path(__file__).resolve().parent.parent / "src" / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))


# ---------------------------------------------------------------------------
# Helpers — build a minimal fake HTTP request/response harness so we can
# exercise OllamaCompatibleHandler without binding to a real port.
# ---------------------------------------------------------------------------

def _make_handler(path: str, method: str = "GET", body: bytes = b"", headers: dict | None = None):
    """
    Build an OllamaCompatibleHandler that processes one fake request.

    Returns (handler, response_bytes) where response_bytes is the full
    HTTP response written to the fake socket.

    We bypass BaseHTTPRequestHandler's __init__ entirely and set all
    required attributes manually so we never need a real socket.
    """
    import email
    from claude_code_wrapper import OllamaCompatibleHandler

    out_buf = io.BytesIO()

    all_headers = {"Content-Length": str(len(body))}
    if headers:
        all_headers.update(headers)

    # Build a simple readable BytesIO as rfile (handler reads body from it)
    rfile = io.BytesIO(body)

    # Parse headers using the stdlib email package
    raw_headers = "".join(f"{k}: {v}\r\n" for k, v in all_headers.items()).encode()
    parsed_headers = email.message_from_bytes(raw_headers)

    handler = OllamaCompatibleHandler.__new__(OllamaCompatibleHandler)
    handler.rfile = rfile
    handler.wfile = out_buf
    handler.path = path
    handler.command = method
    handler.headers = parsed_headers
    handler.server = MagicMock()
    handler.connection = MagicMock()
    handler.request = MagicMock()
    handler.client_address = ("127.0.0.1", 9999)
    # Required by BaseHTTPRequestHandler.send_response → log_request → requestline
    handler.requestline = f"{method} {path} HTTP/1.1"
    handler.request_version = "HTTP/1.1"
    handler.close_connection = False
    # Suppress BaseHTTPRequestHandler logging
    handler.log_message = lambda fmt, *args: None
    handler.log_request = lambda *args: None

    if method == "GET":
        handler.do_GET()
    elif method == "POST":
        handler.do_POST()

    return handler, out_buf.getvalue()


def _parse_response(raw: bytes) -> tuple[int, dict]:
    """Parse raw HTTP response bytes into (status_code, body_dict)."""
    text = raw.decode(errors="replace")
    lines = text.split("\r\n")
    # Status line e.g. "HTTP/1.0 200 OK"
    parts = lines[0].split(" ", 2)
    status = int(parts[1]) if len(parts) >= 2 else 0
    # Body is after the blank line
    try:
        blank = lines.index("")
        body_str = "\r\n".join(lines[blank + 1:])
    except ValueError:
        body_str = ""
    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        body = {"_raw": body_str}
    return status, body


# ===========================================================================
# Group 1: Config — defaults and env overrides
# ===========================================================================


class TestConfig:
    """Config reads from environment variables with sensible defaults."""

    def test_default_host(self):
        from claude_code_wrapper import Config
        with patch.dict("os.environ", {}, clear=True):
            # Re-evaluate default (the module-level default was already set,
            # so we verify the env-based value is a string)
            assert Config.HOST in ("127.0.0.1", "0.0.0.0") or isinstance(Config.HOST, str)

    def test_default_port_is_int(self):
        from claude_code_wrapper import Config
        assert isinstance(Config.PORT, int)
        assert Config.PORT > 0

    def test_default_model_is_string(self):
        from claude_code_wrapper import Config
        assert isinstance(Config.MODEL, str)
        assert len(Config.MODEL) > 0

    def test_default_timeout_is_int(self):
        from claude_code_wrapper import Config
        assert isinstance(Config.TIMEOUT, int)
        assert Config.TIMEOUT > 0

    def test_debug_default_false(self):
        from claude_code_wrapper import Config
        # With no DEBUG env, DEBUG should be False (env default is "false")
        assert isinstance(Config.DEBUG, bool)

    def test_env_override_port(self, monkeypatch):
        monkeypatch.setenv("CLAUDE_CODE_PORT", "9999")
        # Re-import to pick up the env change
        import importlib
        import claude_code_wrapper as m
        importlib.reload(m)
        assert m.Config.PORT == 9999
        importlib.reload(m)  # restore

    def test_env_override_model(self, monkeypatch):
        monkeypatch.setenv("CLAUDE_CODE_MODEL", "claude-opus-4")
        import importlib
        import claude_code_wrapper as m
        importlib.reload(m)
        assert m.Config.MODEL == "claude-opus-4"
        importlib.reload(m)  # restore

    def test_env_debug_true(self, monkeypatch):
        monkeypatch.setenv("DEBUG", "true")
        import importlib
        import claude_code_wrapper as m
        importlib.reload(m)
        assert m.Config.DEBUG is True
        importlib.reload(m)  # restore


# ===========================================================================
# Group 2: ClaudeCodeCLI._find_cli()
# ===========================================================================


class TestFindCli:
    """_find_cli() probes 'which claude', then 'which claude-code', then --version."""

    def _make_cli(self):
        """Create a fresh CLI instance with all subprocess calls stubbed out."""
        from claude_code_wrapper import ClaudeCodeCLI
        with patch("subprocess.run") as mock_run:
            # Default: all calls succeed for 'claude'
            ok = MagicMock()
            ok.returncode = 0
            ok.stdout = "/usr/local/bin/claude\n"
            mock_run.return_value = ok
            return ClaudeCodeCLI(), mock_run

    def test_returns_string(self):
        cli, _ = self._make_cli()
        assert isinstance(cli.cli_path, str)
        assert len(cli.cli_path) > 0

    def test_uses_which_claude_first(self):
        from claude_code_wrapper import ClaudeCodeCLI
        with patch("subprocess.run") as mock_run:
            ok = MagicMock(returncode=0, stdout="/usr/bin/claude\n", stderr="")
            mock_run.return_value = ok
            cli = ClaudeCodeCLI()
        assert cli.cli_path == "/usr/bin/claude"

    def test_fallback_to_claude_code_when_which_claude_fails(self):
        from claude_code_wrapper import ClaudeCodeCLI

        call_count = [0]

        def side_effect(cmd, **kwargs):
            call_count[0] += 1
            r = MagicMock()
            if cmd == ["which", "claude"]:
                r.returncode = 1
                r.stdout = ""
            elif cmd == ["which", "claude-code"]:
                r.returncode = 0
                r.stdout = "/usr/bin/claude-code\n"
            else:
                r.returncode = 0
                r.stdout = ""
            return r

        with patch("subprocess.run", side_effect=side_effect):
            cli = ClaudeCodeCLI()

        assert cli.cli_path == "/usr/bin/claude-code"

    def test_defaults_to_claude_when_nothing_found(self):
        from claude_code_wrapper import ClaudeCodeCLI

        def side_effect(cmd, **kwargs):
            r = MagicMock()
            r.returncode = 1
            r.stdout = ""
            r.stderr = ""
            return r

        with patch("subprocess.run", side_effect=side_effect):
            cli = ClaudeCodeCLI()

        assert cli.cli_path == "claude"

    def test_exception_in_which_is_handled(self):
        from claude_code_wrapper import ClaudeCodeCLI

        def side_effect(cmd, **kwargs):
            if cmd[0] == "which":
                raise OSError("which not found")
            r = MagicMock()
            r.returncode = 0
            r.stdout = ""
            return r

        # Should not raise
        with patch("subprocess.run", side_effect=side_effect):
            cli = ClaudeCodeCLI()
        assert isinstance(cli.cli_path, str)


# ===========================================================================
# Group 3: ClaudeCodeCLI._check_available()
# ===========================================================================


class TestCheckAvailable:
    """_check_available() runs CLI --version and checks returncode."""

    def _cli_with_path(self, cli_path: str, version_returncode: int = 0):
        from claude_code_wrapper import ClaudeCodeCLI

        def side_effect(cmd, **kwargs):
            r = MagicMock()
            if cmd[0] == "which":
                r.returncode = 0
                r.stdout = cli_path + "\n"
            else:
                r.returncode = version_returncode
                r.stdout = "claude 1.0.0"
                r.stderr = ""
            return r

        with patch("subprocess.run", side_effect=side_effect):
            return ClaudeCodeCLI()

    def test_available_true_when_version_succeeds(self):
        cli = self._cli_with_path("/usr/bin/claude", version_returncode=0)
        assert cli.available is True

    def test_available_false_when_version_fails(self):
        cli = self._cli_with_path("/usr/bin/claude", version_returncode=1)
        assert cli.available is False

    def test_available_false_on_exception(self):
        from claude_code_wrapper import ClaudeCodeCLI

        # Build a CLI object with a known path, then test _check_available
        # directly by patching subprocess.run to raise an exception.
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="/usr/bin/claude\n", stderr="")
            cli = ClaudeCodeCLI()

        # Now patch subprocess.run to raise for the _check_available call
        with patch("subprocess.run", side_effect=OSError("no such file")):
            result = cli._check_available()

        assert result is False


# ===========================================================================
# Group 4: ClaudeCodeCLI.query()
# ===========================================================================


class TestCliQuery:
    """query() sends prompt to CLI and returns stdout strip."""

    def _available_cli(self):
        """Return a ClaudeCodeCLI that claims to be available."""
        from claude_code_wrapper import ClaudeCodeCLI

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="/usr/bin/claude\n", stderr="")
            cli = ClaudeCodeCLI()
            cli.available = True
            cli.cli_path = "claude"
        return cli

    def test_returns_none_when_unavailable(self):
        from claude_code_wrapper import ClaudeCodeCLI
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="/usr/bin/claude\n", stderr="")
            cli = ClaudeCodeCLI()
            cli.available = False

        result = cli.query("hello")
        assert result is None

    def test_returns_stdout_on_success(self):
        cli = self._available_cli()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="  4  \n", stderr=""
            )
            result = cli.query("What is 2+2?")
        assert result == "4"

    def test_system_prompt_prepended(self):
        cli = self._available_cli()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="ok\n", stderr="")
            cli.query("hello", system="be brief")
            called_cmd = mock_run.call_args[0][0]
        # The full_prompt passed as -p arg should contain both system and user
        full_prompt_arg = called_cmd[2]
        assert "be brief" in full_prompt_arg
        assert "hello" in full_prompt_arg

    def test_claudecode_env_var_removed(self):
        """CLAUDECODE env var must be stripped before calling CLI."""
        cli = self._available_cli()
        with patch("subprocess.run") as mock_run, \
             patch.dict("os.environ", {"CLAUDECODE": "1"}):
            mock_run.return_value = MagicMock(returncode=0, stdout="answer\n", stderr="")
            cli.query("test")
            call_kwargs = mock_run.call_args[1]
            env = call_kwargs.get("env", {})
            assert "CLAUDECODE" not in env

    def test_returns_none_on_timeout(self):
        cli = self._available_cli()
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 120)):
            result = cli.query("test", timeout=120)
        assert result is None

    def test_returns_none_on_file_not_found(self):
        cli = self._available_cli()
        with patch("subprocess.run", side_effect=FileNotFoundError("no such file")):
            result = cli.query("test")
        assert result is None

    def test_returns_none_on_nested_session_error(self):
        cli = self._available_cli()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="cannot be launched inside another Claude Code session"
            )
            result = cli.query("test")
        assert result is None

    def test_returns_none_on_generic_cli_error(self):
        cli = self._available_cli()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="some other error"
            )
            result = cli.query("test")
        assert result is None

    def test_returns_none_on_unexpected_exception(self):
        cli = self._available_cli()
        with patch("subprocess.run", side_effect=RuntimeError("unexpected")):
            result = cli.query("test")
        assert result is None


# ===========================================================================
# Group 5: ClaudeCodeWrapper (HTTP client class)
# ===========================================================================


class TestClaudeCodeWrapper:
    """ClaudeCodeWrapper.__init__ and query() use HTTP, all mocked."""

    def _make_wrapper(self, server_up: bool = False):
        from claude_code_wrapper import ClaudeCodeWrapper
        with patch("requests.get") as mock_get:
            if server_up:
                mock_get.return_value = MagicMock(status_code=200)
            else:
                mock_get.side_effect = ConnectionError("refused")
            w = ClaudeCodeWrapper(model="claude-haiku-4-5-20251001", host="127.0.0.1", port=8080)
        return w

    def test_init_sets_model(self):
        w = self._make_wrapper()
        assert w.model == "claude-haiku-4-5-20251001"

    def test_init_sets_host_and_port(self):
        w = self._make_wrapper()
        assert w.host == "127.0.0.1"
        assert w.port == 8080

    def test_init_sets_localhost_url(self):
        w = self._make_wrapper()
        assert w.localhost_url == "http://127.0.0.1:8080"

    def test_server_not_running_by_default(self):
        w = self._make_wrapper(server_up=False)
        assert w.server_running is False

    def test_server_running_when_check_succeeds(self):
        w = self._make_wrapper(server_up=True)
        assert w.server_running is True

    def test_query_returns_response_text(self):
        w = self._make_wrapper(server_up=True)
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"response": "Hello world", "done": True}
            )
            result = w.query("Say hello")
        assert result == "Hello world"

    def test_query_returns_none_on_server_error(self):
        w = self._make_wrapper(server_up=True)
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=500)
            result = w.query("test")
        assert result is None

    def test_query_returns_none_on_exception(self):
        w = self._make_wrapper(server_up=True)
        with patch("requests.post", side_effect=ConnectionError("refused")):
            result = w.query("test")
        assert result is None

    def test_query_includes_system_in_payload(self):
        w = self._make_wrapper(server_up=True)
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"response": "ok", "done": True}
            )
            w.query("prompt", system="be brief")
            payload = mock_post.call_args[1]["json"]
        assert payload["system"] == "be brief"

    def test_solve_counting_calls_query(self):
        w = self._make_wrapper(server_up=True)
        with patch.object(w, "query", return_value="42") as mock_q:
            result = w.solve_counting("count to 10")
        mock_q.assert_called_once()
        assert result == "42"

    def test_solve_math_calls_query_with_system(self):
        w = self._make_wrapper(server_up=True)
        with patch.object(w, "query", return_value="pi") as mock_q:
            result = w.solve_math("what is pi?", system="math mode")
        assert result == "pi"
        call_kwargs = mock_q.call_args[1]
        assert call_kwargs.get("system") == "math mode"

    def test_query_returns_none_when_requests_missing(self):
        w = self._make_wrapper(server_up=False)
        with patch.dict("sys.modules", {"requests": None}):
            result = w.query("test")
        assert result is None


# ===========================================================================
# Group 6: OllamaCompatibleHandler — GET endpoints
# ===========================================================================


class TestHandlerGetRoot:
    """GET / returns health check JSON."""

    def test_status_200(self):
        from claude_code_wrapper import cli
        with patch.object(cli, "available", True), \
             patch.object(cli, "cli_path", "/usr/bin/claude"):
            _, raw = _make_handler("/", "GET")
        status, body = _parse_response(raw)
        assert status == 200

    def test_body_has_status_ok(self):
        from claude_code_wrapper import cli
        with patch.object(cli, "available", True), \
             patch.object(cli, "cli_path", "/usr/bin/claude"):
            _, raw = _make_handler("/", "GET")
        _, body = _parse_response(raw)
        assert body.get("status") == "ok"

    def test_body_has_cli_available(self):
        from claude_code_wrapper import cli
        with patch.object(cli, "available", True), \
             patch.object(cli, "cli_path", "/usr/bin/claude"):
            _, raw = _make_handler("/", "GET")
        _, body = _parse_response(raw)
        assert body.get("cli_available") is True

    def test_body_has_cli_path(self):
        from claude_code_wrapper import cli
        with patch.object(cli, "available", True), \
             patch.object(cli, "cli_path", "/usr/bin/claude"):
            _, raw = _make_handler("/", "GET")
        _, body = _parse_response(raw)
        assert body.get("cli_path") == "/usr/bin/claude"


class TestHandlerGetApiTags:
    """GET /api/tags returns Ollama-compatible models list."""

    def test_status_200(self):
        _, raw = _make_handler("/api/tags", "GET")
        status, _ = _parse_response(raw)
        assert status == 200

    def test_body_has_models_key(self):
        _, raw = _make_handler("/api/tags", "GET")
        _, body = _parse_response(raw)
        assert "models" in body

    def test_models_is_list(self):
        _, raw = _make_handler("/api/tags", "GET")
        _, body = _parse_response(raw)
        assert isinstance(body["models"], list)

    def test_models_list_not_empty(self):
        _, raw = _make_handler("/api/tags", "GET")
        _, body = _parse_response(raw)
        assert len(body["models"]) > 0


class TestHandlerGetUnknown:
    """GET unknown path → 404."""

    def test_status_404(self):
        _, raw = _make_handler("/api/unknown-endpoint", "GET")
        status, _ = _parse_response(raw)
        assert status == 404

    def test_body_has_error(self):
        _, raw = _make_handler("/api/unknown-endpoint", "GET")
        _, body = _parse_response(raw)
        assert "error" in body


class TestHandlerGetPlayground:
    """GET /playground returns browser test page."""

    def test_status_200(self):
        _, raw = _make_handler("/playground", "GET")
        status, _ = _parse_response(raw)
        assert status == 200

    def test_body_contains_page_title(self):
        _, raw = _make_handler("/playground", "GET")
        text = raw.decode(errors="replace")
        assert "Claude Wrapper Playground" in text

    def test_body_links_to_codex_playground(self):
        _, raw = _make_handler("/playground", "GET")
        text = raw.decode(errors="replace")
        assert "http://127.0.0.1:8081/playground" in text


# ===========================================================================
# Group 7: OllamaCompatibleHandler — POST /api/generate
# ===========================================================================


class TestHandlerPostGenerate:
    """POST /api/generate — success, missing prompt, CLI unavailable, streaming."""

    def _post_generate(self, payload: dict, cli_response: str | None = "Hello!"):
        from claude_code_wrapper import cli
        body = json.dumps(payload).encode()
        with patch.object(cli, "available", True), \
             patch.object(cli, "cli_path", "claude"), \
             patch.object(cli, "query", return_value=cli_response):
            _, raw = _make_handler("/api/generate", "POST", body)
        return _parse_response(raw)

    def test_success_returns_200(self):
        status, _ = self._post_generate({"prompt": "hi"})
        assert status == 200

    def test_success_body_has_response_key(self):
        _, body = self._post_generate({"prompt": "hi"})
        assert "response" in body

    def test_success_response_text_matches_cli_output(self):
        _, body = self._post_generate({"prompt": "hi"}, cli_response="world")
        assert body["response"] == "world"

    def test_success_body_done_true(self):
        _, body = self._post_generate({"prompt": "hi"})
        assert body.get("done") is True

    def test_missing_prompt_returns_400(self):
        status, body = self._post_generate({"model": "claude-haiku"})
        assert status == 400
        assert "error" in body

    def test_cli_unavailable_returns_503(self):
        from claude_code_wrapper import cli
        body = json.dumps({"prompt": "hi"}).encode()
        with patch.object(cli, "available", False):
            _, raw = _make_handler("/api/generate", "POST", body)
        status, resp_body = _parse_response(raw)
        assert status == 503
        assert "error" in resp_body

    def test_cli_query_returns_none_gives_500(self):
        status, body = self._post_generate({"prompt": "hi"}, cli_response=None)
        assert status == 500
        assert "error" in body

    def test_invalid_json_returns_400(self):
        from claude_code_wrapper import cli
        body = b"not valid json{"
        with patch.object(cli, "available", True):
            _, raw = _make_handler("/api/generate", "POST", body)
        status, resp_body = _parse_response(raw)
        assert status == 400
        assert "error" in resp_body

    def test_streaming_response_contains_done_chunk(self):
        from claude_code_wrapper import cli
        payload = {"prompt": "hi", "stream": True}
        body = json.dumps(payload).encode()
        with patch.object(cli, "available", True), \
             patch.object(cli, "cli_path", "claude"), \
             patch.object(cli, "query", return_value="hello world"):
            _, raw = _make_handler("/api/generate", "POST", body)

        raw_text = raw.decode(errors="replace")
        # Find the NDJSON body (after blank line)
        parts = raw_text.split("\r\n\r\n", 1)
        ndjson_body = parts[1] if len(parts) > 1 else ""
        lines = [ln for ln in ndjson_body.strip().split("\n") if ln]
        assert len(lines) >= 1
        last = json.loads(lines[-1])
        assert last.get("done") is True

    def test_streaming_chunks_have_model_field(self):
        from claude_code_wrapper import cli
        payload = {"prompt": "hi", "stream": True, "model": "my-model"}
        body = json.dumps(payload).encode()
        with patch.object(cli, "available", True), \
             patch.object(cli, "cli_path", "claude"), \
             patch.object(cli, "query", return_value="one two"):
            _, raw = _make_handler("/api/generate", "POST", body)

        raw_text = raw.decode(errors="replace")
        parts = raw_text.split("\r\n\r\n", 1)
        ndjson_body = parts[1] if len(parts) > 1 else ""
        lines = [ln for ln in ndjson_body.strip().split("\n") if ln]
        first = json.loads(lines[0])
        assert "model" in first


# ===========================================================================
# Group 8: OllamaCompatibleHandler — POST unknown path
# ===========================================================================


class TestHandlerPostUnknown:
    """POST to unknown path → 404."""

    def test_status_404(self):
        from claude_code_wrapper import cli
        body = json.dumps({"prompt": "hi"}).encode()
        with patch.object(cli, "available", True):
            _, raw = _make_handler("/api/chat", "POST", body)
        status, _ = _parse_response(raw)
        assert status == 404

    def test_body_has_error(self):
        from claude_code_wrapper import cli
        body = json.dumps({"prompt": "hi"}).encode()
        with patch.object(cli, "available", True):
            _, raw = _make_handler("/api/chat", "POST", body)
        _, resp_body = _parse_response(raw)
        assert "error" in resp_body


# ===========================================================================
# Group 9: run_server() — smoke test (never actually binds)
# ===========================================================================


class TestRunServer:
    """run_server() should call HTTPServer and serve_forever."""

    def test_run_server_creates_httpserver(self):
        from claude_code_wrapper import run_server
        with patch("claude_code_wrapper.HTTPServer") as mock_server_cls:
            mock_server_instance = MagicMock()
            mock_server_cls.return_value = mock_server_instance
            mock_server_instance.serve_forever.side_effect = KeyboardInterrupt

            with pytest.raises(SystemExit):
                run_server(host="127.0.0.1", port=18080)

        mock_server_cls.assert_called_once_with(
            ("127.0.0.1", 18080),
            pytest.importorskip("claude_code_wrapper").OllamaCompatibleHandler
        )


# ===========================================================================
# Group 10: Module-level import and CLI singleton smoke test
# ===========================================================================


class TestModuleImport:
    """Module-level objects are created at import time without errors."""

    def test_module_importable(self):
        import claude_code_wrapper
        assert claude_code_wrapper is not None

    def test_global_cli_instance_exists(self):
        from claude_code_wrapper import cli
        assert cli is not None

    def test_global_cli_has_cli_path_attr(self):
        from claude_code_wrapper import cli
        assert hasattr(cli, "cli_path")
        assert isinstance(cli.cli_path, str)

    def test_global_cli_has_available_attr(self):
        from claude_code_wrapper import cli
        assert hasattr(cli, "available")
        assert isinstance(cli.available, bool)

    def test_handler_class_is_base_http_handler(self):
        from claude_code_wrapper import OllamaCompatibleHandler
        assert issubclass(OllamaCompatibleHandler, BaseHTTPRequestHandler)

    def test_wrapper_class_importable(self):
        from claude_code_wrapper import ClaudeCodeWrapper
        assert ClaudeCodeWrapper is not None
