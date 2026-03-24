from __future__ import annotations

import json

from stillwater.cli import main


def test_cli_store_status_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "stillwater.cli.store_client.catalog_status",
        lambda **kwargs: {  # noqa: ARG005
            "source": "git-manifest-store",
            "manifest_app_count": 10,
            "catalog_app_count": 11,
            "manifest_index_in_sync": True,
            "git": {"branch": "main", "commit_short": "abc1234"},
        },
    )

    rc = main(["store", "status", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["catalog_app_count"] == 11


def test_cli_store_apps_text(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "stillwater.cli.store_client.list_apps",
        lambda **kwargs: {  # noqa: ARG005
            "total": 11,
            "available_count": 3,
            "locked_count": 8,
            "installed_count": 0,
            "items": [
                {"app_id": "solaceagi-browser", "status": "available", "category": "platform", "version": "0.1.0"},
                {"app_id": "gmail-inbox-triage", "status": "available", "category": "communications", "version": "0.1.0"},
            ],
        },
    )

    rc = main(["store", "apps"])
    assert rc == 0
    stdout = capsys.readouterr().out
    assert "apps: total=11 available=3 locked=8 installed=0" in stdout
    assert "- solaceagi-browser [available] platform v0.1.0" in stdout


def test_cli_store_install_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "stillwater.cli.store_client.install_app",
        lambda app_id, **kwargs: {  # noqa: ARG005
            "app_id": app_id,
            "status": "installed",
            "granted_scopes": ["gmail.read.inbox", "local.evidence.write"],
        },
    )

    rc = main(["store", "install", "gmail-inbox-triage", "--optional-scope", "gmail.send.email", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "installed"
    assert data["app_id"] == "gmail-inbox-triage"
