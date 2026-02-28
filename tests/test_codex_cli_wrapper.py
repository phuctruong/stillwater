#!/usr/bin/env python3
"""
tests/test_codex_cli_wrapper.py — Unit tests for src/cli/src/codex_cli_wrapper.py

All subprocess and network calls are mocked.
Rung target: 641
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


CLI_SRC = Path(__file__).resolve().parent.parent / "src" / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))


def _make_handler(path: str, method: str = "GET", body: bytes = b"", headers: dict | None = None):
    import email
    from codex_cli_wrapper import OllamaCompatibleHandler

    out_buf = io.BytesIO()
    all_headers = {"Content-Length": str(len(body))}
    if headers:
        all_headers.update(headers)

    raw_headers = "".join(f"{k}: {v}\r\n" for k, v in all_headers.items()).encode()
    parsed_headers = email.message_from_bytes(raw_headers)

    handler = OllamaCompatibleHandler.__new__(OllamaCompatibleHandler)
    handler.rfile = io.BytesIO(body)
    handler.wfile = out_buf
    handler.path = path
    handler.command = method
    handler.headers = parsed_headers
    handler.server = MagicMock()
    handler.connection = MagicMock()
    handler.request = MagicMock()
    handler.client_address = ("127.0.0.1", 9999)
    handler.requestline = f"{method} {path} HTTP/1.1"
    handler.request_version = "HTTP/1.1"
    handler.close_connection = False
    handler.log_message = lambda fmt, *args: None
    handler.log_request = lambda *args: None

    if method == "GET":
        handler.do_GET()
    elif method == "POST":
        handler.do_POST()

    return handler, out_buf.getvalue()


def _parse_response(raw: bytes) -> tuple[int, dict]:
    text = raw.decode(errors="replace")
    lines = text.split("\r\n")
    status = int(lines[0].split(" ", 2)[1])
    blank = lines.index("")
    body_str = "\r\n".join(lines[blank + 1 :])
    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        body = {"_raw": body_str}
    return status, body


class TestConfig:
    def test_default_port_is_int(self):
        from codex_cli_wrapper import Config

        assert isinstance(Config.PORT, int)
        assert Config.PORT > 0

    def test_env_override_port(self, monkeypatch):
        monkeypatch.setenv("CODEX_WRAPPER_PORT", "8899")
        import importlib
        import codex_cli_wrapper as module

        importlib.reload(module)
        assert module.Config.PORT == 8899
        monkeypatch.delenv("CODEX_WRAPPER_PORT", raising=False)
        importlib.reload(module)


class TestCodexCLI:
    def _available_cli(self):
        from codex_cli_wrapper import CodexCLI

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="/usr/bin/codex\n", stderr="")
            cli = CodexCLI()
            cli.available = True
            cli.cli_path = "codex"
        return cli

    def test_find_cli_prefers_which_codex(self):
        from codex_cli_wrapper import CodexCLI

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="/usr/bin/codex\n", stderr="")
            cli = CodexCLI()
        assert cli.cli_path == "/usr/bin/codex"

    def test_check_available_false_on_exception(self):
        from codex_cli_wrapper import CodexCLI

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="/usr/bin/codex\n", stderr="")
            cli = CodexCLI()
        with patch("subprocess.run", side_effect=OSError("nope")):
            assert cli._check_available() is False

    def test_query_returns_none_when_unavailable(self):
        from codex_cli_wrapper import CodexCLI

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="/usr/bin/codex\n", stderr="")
            cli = CodexCLI()
            cli.available = False
        assert cli.query("hello") is None

    def test_query_reads_output_file_on_success(self):
        cli = self._available_cli()
        with patch("subprocess.run") as mock_run, patch("codex_cli_wrapper._scratch_dir") as mock_scratch:
            scratch = MagicMock()
            path = Path("/tmp/codex-wrapper-test")
            path.mkdir(parents=True, exist_ok=True)
            mock_scratch.return_value = path

            def side_effect(cmd, **kwargs):
                output_path = Path(cmd[cmd.index("--output-last-message") + 1])
                output_path.write_text("wrapper ok\n", encoding="utf-8")
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = side_effect
            assert cli.query("hello") == "wrapper ok"

    def test_query_prepends_system_prompt(self):
        cli = self._available_cli()
        with patch("subprocess.run") as mock_run, patch("codex_cli_wrapper._scratch_dir", return_value=Path("/tmp")):
            def side_effect(cmd, **kwargs):
                output_path = Path(cmd[cmd.index("--output-last-message") + 1])
                output_path.write_text("ok\n", encoding="utf-8")
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = side_effect
            cli.query("hello", system="be brief")
            called_cmd = mock_run.call_args[0][0]
        assert called_cmd[-1] == "be brief\n\nhello"

    def test_query_strips_codex_env_vars(self):
        cli = self._available_cli()
        with patch("subprocess.run") as mock_run, patch.dict("os.environ", {"CODEX_THREAD_ID": "123", "HOME": "/tmp"}):
            def side_effect(cmd, **kwargs):
                output_path = Path(cmd[cmd.index("--output-last-message") + 1])
                output_path.write_text("ok\n", encoding="utf-8")
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = side_effect
            cli.query("hello")
            env = mock_run.call_args[1]["env"]
        assert "CODEX_THREAD_ID" not in env
        assert env["HOME"] == "/tmp"

    def test_query_returns_none_on_missing_output_file(self):
        cli = self._available_cli()
        with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="", stderr="")), patch(
            "codex_cli_wrapper._scratch_dir", return_value=Path("/tmp")
        ):
            assert cli.query("hello") is None

    def test_query_returns_none_on_cli_error(self):
        cli = self._available_cli()
        with patch("subprocess.run", return_value=MagicMock(returncode=1, stdout="", stderr="bad")):
            assert cli.query("hello") is None

    def test_query_returns_none_on_timeout(self):
        cli = self._available_cli()
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("codex", 10)):
            assert cli.query("hello", timeout=10) is None


class TestCodexCLIWrapperClient:
    def _make_wrapper(self, server_up: bool = False):
        from codex_cli_wrapper import CodexCLIWrapper

        with patch("requests.get") as mock_get:
            if server_up:
                mock_get.return_value = MagicMock(status_code=200)
            else:
                mock_get.side_effect = ConnectionError("refused")
            wrapper = CodexCLIWrapper(model="codex-default", host="127.0.0.1", port=8081)
        return wrapper

    def test_init_sets_localhost_url(self):
        wrapper = self._make_wrapper()
        assert wrapper.localhost_url == "http://127.0.0.1:8081"

    def test_server_running_true_when_check_succeeds(self):
        wrapper = self._make_wrapper(server_up=True)
        assert wrapper.server_running is True

    def test_query_returns_response_text(self):
        wrapper = self._make_wrapper(server_up=True)
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: {"response": "hello", "done": True})
            assert wrapper.query("Say hello") == "hello"

    def test_query_returns_none_on_http_error(self):
        wrapper = self._make_wrapper(server_up=True)
        with patch("requests.post", return_value=MagicMock(status_code=500)):
            assert wrapper.query("hello") is None


class TestHandlerGet:
    def test_root_returns_health_json(self):
        from codex_cli_wrapper import cli

        with patch.object(cli, "available", True), patch.object(cli, "cli_path", "/usr/bin/codex"):
            _, raw = _make_handler("/", "GET")
        status, body = _parse_response(raw)
        assert status == 200
        assert body["status"] == "ok"
        assert body["cli_available"] is True

    def test_api_tags_returns_models(self):
        _, raw = _make_handler("/api/tags", "GET")
        status, body = _parse_response(raw)
        assert status == 200
        assert len(body["models"]) >= 1

    def test_playground_returns_html(self):
        _, raw = _make_handler("/playground", "GET")
        text = raw.decode(errors="replace")
        assert "200 OK" in text
        assert "Codex Wrapper Playground" in text

    def test_playground_links_to_claude_playground(self):
        _, raw = _make_handler("/playground", "GET")
        text = raw.decode(errors="replace")
        assert "http://127.0.0.1:8080/playground" in text

    def test_unknown_get_returns_404(self):
        _, raw = _make_handler("/missing", "GET")
        status, body = _parse_response(raw)
        assert status == 404
        assert body["error"] == "not found"


class TestHandlerPostGenerate:
    def _post_generate(self, payload: dict, cli_response: str | None = "Hello!"):
        from codex_cli_wrapper import cli

        body = json.dumps(payload).encode()
        with patch.object(cli, "available", True), patch.object(cli, "query", return_value=cli_response):
            _, raw = _make_handler("/api/generate", "POST", body)
        return _parse_response(raw)

    def test_success_returns_200(self):
        status, body = self._post_generate({"prompt": "hi"})
        assert status == 200
        assert body["response"] == "Hello!"

    def test_missing_prompt_returns_400(self):
        status, body = self._post_generate({"model": "codex-default"})
        assert status == 400
        assert "error" in body

    def test_cli_unavailable_returns_503(self):
        from codex_cli_wrapper import cli

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
        from codex_cli_wrapper import cli

        with patch.object(cli, "available", True):
            _, raw = _make_handler("/api/generate", "POST", b"not-json")
        status, body = _parse_response(raw)
        assert status == 400
        assert "error" in body

    def test_streaming_response_ends_done_true(self):
        from codex_cli_wrapper import cli

        body = json.dumps({"prompt": "hi", "stream": True}).encode()
        with patch.object(cli, "available", True), patch.object(cli, "query", return_value="one two"):
            _, raw = _make_handler("/api/generate", "POST", body)
        raw_text = raw.decode(errors="replace")
        ndjson_body = raw_text.split("\r\n\r\n", 1)[1]
        last = json.loads([line for line in ndjson_body.strip().split("\n") if line][-1])
        assert last["done"] is True

    def test_unknown_post_returns_404(self):
        from codex_cli_wrapper import cli

        body = json.dumps({"prompt": "hi"}).encode()
        with patch.object(cli, "available", True):
            _, raw = _make_handler("/api/chat", "POST", body)
        status, payload = _parse_response(raw)
        assert status == 404
        assert payload["error"] == "not found"


class TestRunServer:
    def test_run_server_creates_httpserver(self):
        from codex_cli_wrapper import run_server

        with patch("codex_cli_wrapper.HTTPServer") as mock_server_cls:
            server = MagicMock()
            server.serve_forever.side_effect = KeyboardInterrupt
            mock_server_cls.return_value = server
            with pytest.raises(SystemExit):
                run_server(host="127.0.0.1", port=18081)

        mock_server_cls.assert_called_once_with(
            ("127.0.0.1", 18081),
            pytest.importorskip("codex_cli_wrapper").OllamaCompatibleHandler,
        )


class TestModuleImport:
    def test_module_importable(self):
        import codex_cli_wrapper

        assert codex_cli_wrapper is not None

    def test_global_cli_exists(self):
        from codex_cli_wrapper import cli

        assert cli is not None

    def test_handler_is_http_handler(self):
        from codex_cli_wrapper import OllamaCompatibleHandler

        assert issubclass(OllamaCompatibleHandler, BaseHTTPRequestHandler)

    def test_wrapper_class_importable(self):
        from codex_cli_wrapper import CodexCLIWrapper

        assert CodexCLIWrapper is not None
