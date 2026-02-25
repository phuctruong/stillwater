"""Recipe execution engine for JSON browser recipes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .recipe_audit import AuditChain
from .recipe_router import MailRouter
from .recipe_safety import SafetyGate


class RecipeExecutionError(RuntimeError):
    """Fail-closed recipe execution error with explicit halt code."""

    def __init__(self, message: str, halt_code: str = "EXIT_RECIPE_FAILED") -> None:
        super().__init__(message)
        self.halt_code = halt_code


class WebserviceClient:
    """Minimal JSON HTTP client for browser webservice."""

    def __init__(self, base_url: str = "http://localhost:9224", timeout: int = 15) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = int(timeout)

    def post_json(self, path: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        url = path if path.startswith("http://") or path.startswith("https://") else f"{self.base_url}{path}"
        body = json.dumps(payload or {}).encode("utf-8")
        req = Request(url=url, method="POST", headers={"Content-Type": "application/json"}, data=body)
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except HTTPError as exc:
            raise RecipeExecutionError(
                f"webservice HTTP error at {url}: {exc.code}",
                halt_code="EXIT_WEBSERVICE_HTTP_ERROR",
            ) from exc
        except URLError as exc:
            raise RecipeExecutionError(
                f"webservice connection error at {url}: {exc.reason}",
                halt_code="EXIT_WEBSERVICE_UNREACHABLE",
            ) from exc

        try:
            parsed = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError as exc:
            raise RecipeExecutionError(
                f"webservice returned invalid JSON at {url}",
                halt_code="EXIT_WEBSERVICE_INVALID_JSON",
            ) from exc
        if not isinstance(parsed, dict):
            raise RecipeExecutionError(
                f"webservice JSON must be object at {url}",
                halt_code="EXIT_WEBSERVICE_INVALID_JSON",
            )
        return parsed


class RecipeExecutor:
    """Executes JSON recipes with safety gates and hash-chain audit."""

    def __init__(
        self,
        recipe_path: str | Path,
        *,
        webservice_url: str = "http://localhost:9224",
        session_id: str | None = None,
        client: WebserviceClient | None = None,
        router: MailRouter | None = None,
        safety_gate: SafetyGate | None = None,
        audit_chain: AuditChain | None = None,
    ) -> None:
        self.recipe_path = Path(recipe_path)
        self.recipe = self._load_recipe(self.recipe_path)
        self.client = client or WebserviceClient(base_url=webservice_url)
        self.audit = audit_chain or AuditChain(session_id=session_id)
        self.router = router or MailRouter(cpu_threshold=0.80)
        self.safety = safety_gate or SafetyGate(session_id=self.audit.session_id)

    @staticmethod
    def _load_recipe(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise RecipeExecutionError(f"recipe file not found: {path}", halt_code="EXIT_RECIPE_NOT_FOUND")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RecipeExecutionError(
                f"recipe JSON parse error: {path}",
                halt_code="EXIT_RECIPE_INVALID_JSON",
            ) from exc
        if not isinstance(data, dict):
            raise RecipeExecutionError(
                f"recipe root must be object: {path}",
                halt_code="EXIT_RECIPE_INVALID_JSON",
            )
        if not isinstance(data.get("steps"), list):
            raise RecipeExecutionError("recipe must include list field 'steps'", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
        return data

    def execute(self, inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "inputs": dict(inputs or {}),
            "rows": [],
            "emails": [],
            "selected_email_ids": list((inputs or {}).get("email_ids", [])),
            "archived_count": 0,
            "snapshot_hash": None,
        }
        step_results: dict[str, Any] = {}

        for i, raw_step in enumerate(self.recipe.get("steps", []), start=1):
            if not isinstance(raw_step, dict):
                raise RecipeExecutionError(f"step #{i} must be an object", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
            step_name = str(raw_step.get("name") or f"step_{i}")
            action = str(raw_step.get("action") or "").strip()
            if not action:
                raise RecipeExecutionError(f"step '{step_name}' missing action", halt_code="EXIT_RECIPE_INVALID_SCHEMA")

            result = self.execute_step(raw_step, ctx)
            step_results[step_name] = result
            self.audit.log_event(
                "RECIPE_STEP",
                {"step_name": step_name, "action": action, "result_digest": _digest(result)},
            )

        summary = self._build_summary(ctx)
        self.audit.log_event(
            "RECIPE_COMPLETE",
            {
                "recipe_id": str(self.recipe.get("id", "")),
                "emails_processed": summary["emails_processed"],
                "archived": summary["archived"],
            },
        )
        chain_status = self.audit.verify_chain()
        if not chain_status.get("valid", False):
            raise RecipeExecutionError(f"audit chain verification failed: {chain_status}", halt_code="EXIT_AUDIT_CHAIN_INVALID")

        return {
            "recipe_id": str(self.recipe.get("id", "")),
            "session_id": self.audit.session_id,
            "steps": step_results,
            **summary,
            "audit_events": int(chain_status.get("events_checked", 0)),
            "part11_hash": str(chain_status.get("last_hash", "")),
        }

    def execute_step(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        action = str(step.get("action", ""))
        handlers = {
            "navigate": self._step_navigate,
            "extract": self._step_extract,
            "extract_fields": self._step_extract_fields,
            "click": self._step_click,
            "type": self._step_type,
            "press_key": self._step_press_key,
            "keyboard_shortcut": self._step_keyboard_shortcut,
            "check_token_scope": self._step_check_token_scope,
            "check_budget": self._step_check_budget,
            "require_human_confirmation": self._step_require_confirmation,
            "snapshot_pre_action": self._step_snapshot_pre_action,
            "select_by_filter": self._step_select_by_filter,
            "verify": self._step_verify,
            "log_to_part11": self._step_log_to_part11,
            "paginate": self._step_paginate,
        }
        fn = handlers.get(action)
        if fn is None:
            raise RecipeExecutionError(f"unknown recipe action: {action}", halt_code="EXIT_UNKNOWN_ACTION")
        return fn(step, ctx)

    def _step_navigate(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        url = str(step.get("url", "")).strip()
        if not url:
            raise RecipeExecutionError("navigate step requires 'url'", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
        payload: dict[str, Any] = {"url": url}
        if "wait_until" in step:
            payload["wait_until"] = step["wait_until"]
        return {"ok": True, "url": url, "response": self.client.post_json("/api/navigate", payload)}

    def _step_extract(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        selector = str(step.get("selector", "")).strip()
        if not selector:
            raise RecipeExecutionError("extract step requires 'selector'", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
        response = self.client.post_json("/api/snapshot", {"selector": selector})
        rows = _extract_rows_from_snapshot(response, max_rows=int(step.get("max_rows", 50)))
        ctx["rows"] = list(rows)
        if rows:
            ctx["emails"] = list(rows)
        return {"ok": True, "selector": selector, "count": len(rows), "rows": rows}

    def _step_extract_fields(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        rows = list(ctx.get("rows") or [])
        mapping = step.get("for_each_row")
        if not isinstance(mapping, dict):
            raise RecipeExecutionError("extract_fields requires 'for_each_row' object", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
        parsed: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            item: dict[str, Any] = {}
            for field_name, spec_raw in mapping.items():
                spec = spec_raw if isinstance(spec_raw, dict) else {}
                item[str(field_name)] = _extract_field_value(
                    row,
                    selector=str(spec.get("selector", "")).strip(),
                    field_type=str(spec.get("type", "text")),
                    spec=spec,
                )
            parsed.append(item)
        ctx["emails"] = parsed
        return {"ok": True, "count": len(parsed), "emails": parsed}

    def _step_click(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        selector = str(step.get("selector", "")).strip()
        if not selector:
            raise RecipeExecutionError("click step requires 'selector'", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
        response = self.client.post_json("/api/click", {"selector": selector})
        if "archive" in selector.lower():
            selected = list(ctx.get("selected_email_ids") or [])
            count = len(selected) if selected else 1
            ctx["archived_count"] = int(ctx.get("archived_count", 0)) + count
            self.safety.consume_budget("archive", count)
            self.audit.log_archive(selected or [f"synthetic-{count}"], success=True, halt_reason=None)
        return {"ok": True, "selector": selector, "response": response}

    def _step_type(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        selector = str(step.get("selector", "")).strip()
        text = str(step.get("text", ctx["inputs"].get("query", "")))
        if not selector:
            raise RecipeExecutionError("type step requires 'selector'", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
        return {"ok": True, "selector": selector, "typed_chars": len(text), "response": self.client.post_json("/api/type", {"selector": selector, "text": text})}

    def _step_press_key(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        key = str(step.get("key", "")).strip()
        if not key:
            raise RecipeExecutionError("press_key step requires 'key'", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
        return {"ok": True, "key": key, "response": self.client.post_json("/api/press-key", {"key": key})}

    def _step_keyboard_shortcut(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        shortcut = str(step.get("shortcut", "")).strip()
        if not shortcut:
            raise RecipeExecutionError("keyboard_shortcut step requires 'shortcut'", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
        return {"ok": True, "shortcut": shortcut, "response": self.client.post_json("/api/press-key", {"shortcut": shortcut})}

    def _step_check_token_scope(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        token_id = str(ctx["inputs"].get("oauth3_token_id", "") or ctx["inputs"].get("token_id", ""))
        required_scope = str(step.get("required_scope", "")).strip()
        ok, msg = self.safety.check_scope(token_id, required_scope)
        if not ok:
            self.audit.log_archive([], success=False, halt_reason=msg)
            raise RecipeExecutionError(msg, halt_code=msg)
        return {"ok": True, "required_scope": required_scope}

    def _step_check_budget(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        budget_type = str(step.get("budget_type", "archive"))
        limit = int(step.get("limit_per_session", self.safety.archive_limit))
        ok, msg, remaining = self.safety.check_budget(budget_type, limit)
        if not ok:
            self.audit.log_archive([], success=False, halt_reason=msg)
            raise RecipeExecutionError(msg, halt_code=msg)
        return {"ok": True, "budget_type": budget_type, "remaining": remaining}

    def _step_require_confirmation(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        selected = list(ctx.get("selected_email_ids") or [])
        email_count = len(selected)
        threshold = int(step.get("threshold_emails", self.safety.confirmation_threshold))
        if email_count <= threshold:
            return {"ok": True, "email_count": email_count, "required": False}
        if self.safety.confirmation_fn is None:
            msg = "EXIT_CONFIRMATION_DENIED"
            self.audit.log_archive(selected, success=False, halt_reason=msg)
            raise RecipeExecutionError(msg, halt_code=msg)
        approved = bool(self.safety.confirmation_fn(email_count))
        if not approved:
            msg = "EXIT_CONFIRMATION_DENIED"
            self.audit.log_archive(selected, success=False, halt_reason=msg)
            raise RecipeExecutionError(msg, halt_code=msg)
        return {"ok": True, "email_count": email_count, "required": True}

    def _step_snapshot_pre_action(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        target = str(step.get("target", "selected_emails"))
        payload: object = list(ctx.get("selected_email_ids") or []) if target == "selected_emails" else ctx.get(target, [])
        ok, msg, digest = self.safety.snapshot_pre_action(payload)
        if not ok:
            raise RecipeExecutionError(msg, halt_code=msg)
        ctx["snapshot_hash"] = digest
        return {"ok": True, "snapshot_hash": digest}

    def _step_select_by_filter(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        selected = ctx["inputs"].get("email_ids")
        if not isinstance(selected, list):
            raise RecipeExecutionError("select_by_filter requires input field 'email_ids' (list)", halt_code="EXIT_RECIPE_INVALID_INPUT")
        ctx["selected_email_ids"] = [str(item) for item in selected]
        return {"ok": True, "selected_count": len(ctx["selected_email_ids"])}

    def _step_verify(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        check_name = str(step.get("check", "")).strip()
        if not check_name:
            raise RecipeExecutionError("verify step requires 'check'", halt_code="EXIT_RECIPE_INVALID_SCHEMA")
        return {"ok": True, "check": check_name, "response": self.client.post_json("/api/snapshot", {"check": check_name})}

    def _step_log_to_part11(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        event_type = str(step.get("event_type", "RECIPE_EVENT")).strip() or "RECIPE_EVENT"
        details = dict(step.get("fields", {})) if isinstance(step.get("fields"), dict) else {}
        details["email_count"] = int(ctx.get("archived_count", 0))
        details["snapshot_hash"] = ctx.get("snapshot_hash")
        details["oauth3_token_id"] = ctx["inputs"].get("oauth3_token_id", "")
        details["timestamp"] = datetime.now(timezone.utc).isoformat()
        event_hash = self.audit.log_event(event_type, details)
        return {"ok": True, "event_type": event_type, "event_hash": event_hash}

    def _step_paginate(self, step: Mapping[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "status": "noop", "strategy": step.get("strategy", "none")}

    def _build_summary(self, ctx: Mapping[str, Any]) -> dict[str, Any]:
        emails = list(ctx.get("emails") or [])
        if not emails:
            return {
                "emails_processed": 0,
                "cpu_classified": 0,
                "llm_escalated": 0,
                "archived": int(ctx.get("archived_count", 0)),
                "tokens_used": 0,
                "tokens_saved": 0,
                "cost_usd": 0.0,
            }
        batch = self.router.classify_batch(emails)
        for email in list(batch.get("emails") or []):
            self.audit.log_classification(
                email=email,
                classification=str(email.get("classification", "unknown")),
                confidence=float(email.get("confidence", 0.0)),
                routed_to=str(email.get("routed_to", "unknown")),
            )
        processed = int(batch["emails_processed"])
        tokens_used = int(batch["tokens_used"])
        baseline = processed * 50
        return {
            "emails_processed": processed,
            "cpu_classified": int(batch["cpu_classified"]),
            "llm_escalated": int(batch["llm_escalated"]),
            "archived": int(ctx.get("archived_count", 0)),
            "tokens_used": tokens_used,
            "tokens_saved": max(0, baseline - tokens_used),
            "cost_usd": round((tokens_used / 1_000_000) * 0.59, 6),
        }


def _digest(data: object) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return payload[:400]


def _extract_rows_from_snapshot(snapshot: Mapping[str, Any], max_rows: int) -> list[dict[str, Any]]:
    if isinstance(snapshot.get("emails"), list):
        return [dict(item) for item in snapshot["emails"][:max_rows] if isinstance(item, dict)]
    if isinstance(snapshot.get("rows"), list):
        return [dict(item) for item in snapshot["rows"][:max_rows] if isinstance(item, dict)]

    root: Any = snapshot.get("snapshot", snapshot)
    tree = root.get("a11y_tree") if isinstance(root, dict) else None
    if tree is None and isinstance(root, dict):
        tree = root.get("aria_tree") or root.get("dom")
    if tree is None:
        return []

    rows: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if len(rows) >= max_rows:
            return
        if isinstance(node, dict):
            if str(node.get("role", "")).lower() == "row":
                rows.append(
                    {
                        "subject": str(node.get("subject", "") or node.get("name", "")),
                        "sender": str(node.get("sender", "")),
                        "unread": bool(node.get("unread", False)),
                        "starred": bool(node.get("starred", False)),
                        "has_attachment": bool(node.get("has_attachment", False)),
                        "attributes": dict(node.get("attributes", {}))
                        if isinstance(node.get("attributes"), dict)
                        else {},
                    }
                )
            for key in ("children", "nodes", "items"):
                children = node.get(key)
                if isinstance(children, list):
                    for child in children:
                        walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(tree)
    return rows


def _extract_field_value(row: Mapping[str, Any], *, selector: str, field_type: str, spec: Mapping[str, Any]) -> Any:
    selector = selector.lower()
    attr_name = str(spec.get("attribute", "")).strip()
    if field_type == "presence":
        if "unread" in selector:
            return bool(row.get("unread", False))
        if "starred" in selector:
            return bool(row.get("starred", False))
        if "attachment" in selector:
            return bool(row.get("has_attachment", False))
        return False
    if field_type == "attribute":
        attrs = row.get("attributes", {})
        if isinstance(attrs, dict) and attr_name:
            return attrs.get(attr_name, "")
        return ""
    if "heading" in selector or "subject" in selector:
        return str(row.get("subject", ""))
    if "email" in selector or "sender" in selector:
        return str(row.get("sender", "")) or str(row.get("sender_name", ""))
    if "timestamp" in selector:
        return str(row.get("timestamp", ""))
    return ""


__all__ = ["RecipeExecutionError", "WebserviceClient", "RecipeExecutor", "MailRouter", "SafetyGate", "AuditChain"]

