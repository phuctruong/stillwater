from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests
from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def frontend_server_url() -> str:
    port = _free_port()
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{REPO_ROOT / 'cli' / 'src'}:{REPO_ROOT}:{pythonpath}".rstrip(":")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "admin.app:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--log-level",
        "warning",
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    base = f"http://127.0.0.1:{port}"
    deadline = time.time() + 25
    while time.time() < deadline:
        try:
            resp = requests.get(f"{base}/health", timeout=1)
            if resp.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(0.25)
    else:
        proc.terminate()
        raise RuntimeError("frontend test server failed to start")

    try:
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        yield browser
        browser.close()


def _dashboard_columns(page) -> int:
    return int(page.evaluate(
        """() => {
            const cards = [...document.querySelectorAll('#tab-dashboard .hero-card')];
            const visible = cards.filter(el => el.offsetParent !== null);
            if (!visible.length) return 0;
            const tops = visible.map(el => Math.round(el.getBoundingClientRect().top));
            const minTop = Math.min(...tops);
            return visible.filter(el => Math.abs(Math.round(el.getBoundingClientRect().top) - minTop) <= 1).length;
        }"""
    ))


def _modal_centered(page) -> bool:
    return bool(page.evaluate(
        """() => {
            const modal = document.querySelector('#llmModal.show .modal-box');
            if (!modal) return false;
            const r = modal.getBoundingClientRect();
            const cx = r.left + (r.width / 2);
            const cy = r.top + (r.height / 2);
            return Math.abs(cx - (window.innerWidth / 2)) <= 24 && Math.abs(cy - (window.innerHeight / 2)) <= 24;
        }"""
    ))


def test_smoke_interactions_and_persistence(frontend_server_url: str, browser):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    console_errors: list[str] = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    page.goto(f"{frontend_server_url}/", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    skills_count = requests.get(f"{frontend_server_url}/api/skills/list", timeout=5).json()["count"]
    swarms_count = requests.get(f"{frontend_server_url}/api/swarms/list", timeout=5).json()["count"]
    personas_count = requests.get(f"{frontend_server_url}/api/personas/list", timeout=5).json()["count"]

    assert page.locator(".hero-card").count() == 5
    assert page.locator('.hero-card[data-navigate^="http"]').count() == 0
    assert page.locator(".welcome-heading").inner_text().strip() == "Stillwater Admin"
    assert "stillwater serve" in page.locator(".welcome-desc").inner_text()
    assert page.locator("#badgeSkillsCount").inner_text().strip().lower() == f"skills: {skills_count}"
    assert page.locator("#badgeSwarmsCount").inner_text().strip().lower() == f"swarms: {swarms_count}"
    assert page.locator("#badgePersonasCount").inner_text().strip().lower() == f"personas: {personas_count}"
    assert page.evaluate("() => [...document.querySelectorAll('.hero-badge')].every(el => !!el.getAttribute('title'))")
    assert page.locator(".term-hint[title]").count() >= 3
    assert page.evaluate(
        """() => [...document.querySelectorAll('.hero-card img')]
            .every(img => img.complete && img.naturalWidth > 0)"""
    )

    status_text = page.locator("#serverStatus").inner_text().strip()
    assert "Online" in status_text or "Offline" in status_text or "Connecting" in status_text

    page.locator('.hero-card[data-navigate="orchestration"]').first.click()
    assert page.locator("#tab-orchestration").evaluate("el => el.classList.contains('active')")
    page.locator('.tab-btn[data-tab="dashboard"]').click()

    for tab in ["orchestration", "skills", "swarms", "personas", "recipes"]:
        page.locator(f'.tab-btn[data-tab="{tab}"]').click()
        page.wait_for_timeout(400)
        graph_ok = page.evaluate(
            f"""() => {{
                const wrap = document.getElementById('mermaid-{tab}');
                return !!wrap.querySelector('svg, .loading-text, .mermaid-loading');
            }}"""
        )
        assert graph_ok

    page.locator("#btnConfigLLM").click()
    assert page.locator("#llmModal").evaluate("el => el.classList.contains('show')")
    page.locator('input[name="llmModel"][value="sonnet"]').check()
    page.locator("#btnSaveLLM").click()
    page.locator("#llmModalNotice.modal-notice-success").wait_for(timeout=5000)
    page.wait_for_timeout(2300)
    assert page.locator("#llmModal").evaluate("el => el.classList.contains('show')")
    page.locator("#btnCloseLLM").click()
    assert not page.locator("#llmModal").evaluate("el => el.classList.contains('show')")

    page.locator("#btnConfigSolace").click()
    page.fill("#solaceApiKey", "sw_sk_demo_key_0123456789")
    page.locator("#btnCancelSolace").click()
    page.locator("#btnConfigSolace").click()
    assert page.locator("#solaceApiKey").input_value() == ""
    page.fill("#solaceApiKey", "sw_sk_demo_key_0123456789")
    page.locator("#btnSaveSolace").click()
    page.locator("#solaceModalNotice.modal-notice-success").wait_for(timeout=5000)
    page.wait_for_timeout(2300)
    assert page.locator("#solaceModal").evaluate("el => el.classList.contains('show')")
    page.locator("#btnCloseSolace").click()
    assert not page.locator("#solaceModal").evaluate("el => el.classList.contains('show')")

    page.locator('.tab-btn[data-tab="recipes"]').click()
    page.reload(wait_until="domcontentloaded")
    assert page.locator("#tab-recipes").evaluate("el => el.classList.contains('active')")

    # Modal close methods + focus trap checks.
    page.locator("#btnConfigLLM").click()
    assert page.locator("#llmModal").get_attribute("aria-hidden") == "false"
    for _ in range(12):
        page.keyboard.press("Tab")
        assert page.evaluate("() => document.getElementById('llmModal').contains(document.activeElement)")
    page.keyboard.press("Escape")
    assert page.locator("#llmModal").get_attribute("aria-hidden") == "true"

    page.locator("#btnConfigLLM").click()
    page.locator("#btnCloseLLM").click()
    assert not page.locator("#llmModal").evaluate("el => el.classList.contains('show')")

    page.locator("#btnConfigLLM").click()
    page.locator("#btnCancelLLM").click()
    assert not page.locator("#llmModal").evaluate("el => el.classList.contains('show')")

    page.locator("#btnConfigLLM").click()
    page.locator("#llmModal").click(position={"x": 5, "y": 5})
    assert not page.locator("#llmModal").evaluate("el => el.classList.contains('show')")

    assert console_errors == []
    context.close()


def test_accessibility_and_polling(frontend_server_url: str, browser):
    context = browser.new_context(viewport={"width": 1366, "height": 900})
    page = context.new_page()

    llm_status_requests = {"count": 0}

    def _count_requests(req):
        if "/api/llm/status" in req.url:
            llm_status_requests["count"] += 1

    page.on("request", _count_requests)
    page.goto(f"{frontend_server_url}/", wait_until="domcontentloaded")
    assert page.locator('script[src*="mermaid.min.js"]').count() == 0
    page.locator('.tab-btn[data-tab="orchestration"]').click()
    page.locator('script[src*="mermaid.min.js"]').first.wait_for(state="attached", timeout=8000)
    page.locator('.tab-btn[data-tab="dashboard"]').click()

    interactive_focusable = page.evaluate(
        """() => {
            const els = [...document.querySelectorAll('button, [href], input, [role="button"]')];
            return els.every(el => {
                if (el.disabled) return true;
                const ti = el.getAttribute('tabindex');
                return ti === null || Number(ti) >= 0;
            });
        }"""
    )
    assert interactive_focusable

    contrast_ratio = page.evaluate(
        """() => {
            function hexToRgb(hex) {
                const raw = hex.trim().replace('#', '');
                const normalized = raw.length === 3
                    ? raw.split('').map(c => c + c).join('')
                    : raw;
                const intVal = parseInt(normalized, 16);
                return {
                    r: (intVal >> 16) & 255,
                    g: (intVal >> 8) & 255,
                    b: intVal & 255
                };
            }
            function luminance({r, g, b}) {
                const srgb = [r, g, b].map(v => v / 255).map(v => (
                    v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
                ));
                return (0.2126 * srgb[0]) + (0.7152 * srgb[1]) + (0.0722 * srgb[2]);
            }
            const root = getComputedStyle(document.documentElement);
            const text = root.getPropertyValue('--text-muted');
            const bg = root.getPropertyValue('--bg-dark');
            const l1 = luminance(hexToRgb(text));
            const l2 = luminance(hexToRgb(bg));
            const light = Math.max(l1, l2);
            const dark = Math.min(l1, l2);
            return (light + 0.05) / (dark + 0.05);
        }"""
    )
    assert contrast_ratio >= 4.5

    assert page.evaluate(
        """() => [...document.querySelectorAll('img')].every(img => !!img.getAttribute('alt'))"""
    )

    page.wait_for_timeout(11_000)
    assert llm_status_requests["count"] >= 2

    # Polling should resume when a visibilitychange event fires after stopPolling().
    requests_before_stop = llm_status_requests["count"]
    page.evaluate("() => stopPolling()")
    page.wait_for_timeout(6_000)
    requests_after_stop = llm_status_requests["count"]
    assert requests_after_stop <= requests_before_stop + 1

    page.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")
    page.wait_for_timeout(6_000)
    assert llm_status_requests["count"] >= requests_after_stop + 1

    # Light mode token override sanity check.
    page.evaluate("() => { document.documentElement.setAttribute('data-theme', 'light'); }")
    page.wait_for_timeout(150)
    assert page.evaluate(
        """() => getComputedStyle(document.body).color !== '' &&
                getComputedStyle(document.querySelector('.topbar')).backgroundColor !== ''"""
    )

    context.close()


def test_clickjacking_headers_present(frontend_server_url: str) -> None:
    resp = requests.get(f"{frontend_server_url}/", timeout=5)
    assert resp.status_code == 200
    assert resp.headers.get("X-Frame-Options") == "DENY"
    csp = resp.headers.get("Content-Security-Policy", "")
    assert "frame-ancestors 'none'" in csp


def test_offline_states_and_sticky_error_alert(frontend_server_url: str, browser):
    context = browser.new_context(viewport={"width": 1366, "height": 900})
    page = context.new_page()

    page.route("**/health", lambda route: route.abort())
    page.route("**/api/llm/status", lambda route: route.abort())
    page.route("**/api/solace-agi/status", lambda route: route.abort())
    page.route("**/api/skills/list", lambda route: route.abort())
    page.route("**/api/swarms/list", lambda route: route.abort())
    page.route("**/api/personas/list", lambda route: route.abort())
    page.route("**/api/mermaid/**", lambda route: route.abort())

    page.goto(f"{frontend_server_url}/", wait_until="domcontentloaded")
    page.wait_for_timeout(700)

    for _ in range(2):
        page.locator("#btnRetryHealth").click()
        page.wait_for_timeout(350)

    assert "Server Offline" in page.locator("#serverStatus").inner_text()
    assert page.locator("#llmStatus").inner_text().strip() == "Unavailable — server offline"
    assert page.locator("#solaceStatus").inner_text().strip() == "Unavailable — server offline"
    assert page.locator("#skillsStatus").inner_text().strip() == "Unavailable — server offline"

    page.locator('.tab-btn[data-tab="orchestration"]').click()
    page.locator("#mermaid-orchestration .loading-text").first.wait_for(timeout=5000)
    assert "Start the server to view this diagram. Run: stillwater serve" in page.locator(
        "#mermaid-orchestration .loading-text"
    ).inner_text()

    page.locator("#btnConfigSolace").click()
    page.fill("#solaceApiKey", "short")
    page.locator("#btnSaveSolace").click()
    page.locator(".alert-error").first.wait_for(timeout=4000)
    page.wait_for_timeout(5200)
    assert page.locator(".alert-error").count() >= 1
    page.locator("#btnCancelSolace").click()
    page.locator(".alert-error .alert-close").first.click()
    page.wait_for_timeout(200)
    assert page.locator(".alert-error").count() == 0

    context.close()


def test_llm_save_double_submit_guard(frontend_server_url: str, browser):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    llm_save_calls = {"count": 0}

    def _handle_llm_config(route, request):
        del request
        llm_save_calls["count"] += 1
        time.sleep(1)
        route.fulfill(
            status=200,
            headers={"Content-Type": "application/json"},
            body='{"saved": true, "config_path": "data/custom/llm_config.yaml"}',
        )

    page.route("**/api/llm/config", _handle_llm_config)
    page.goto(f"{frontend_server_url}/", wait_until="domcontentloaded")
    page.locator("#btnConfigLLM").click()
    page.evaluate(
        """() => {
            const btn = document.getElementById('btnSaveLLM');
            btn.click();
            btn.click();
        }"""
    )
    page.locator("#llmModalNotice.modal-notice-success").wait_for(timeout=8000)
    assert llm_save_calls["count"] == 1

    context.close()


def test_responsive_layout_and_modal_centering(frontend_server_url: str, browser):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.goto(f"{frontend_server_url}/", wait_until="domcontentloaded")

    # 1440 desktop
    assert page.evaluate("() => getComputedStyle(document.querySelector('.main-layout')).flexDirection") == "row"

    # 1024 breakpoint
    page.set_viewport_size({"width": 1024, "height": 900})
    page.wait_for_timeout(250)
    assert page.evaluate("() => getComputedStyle(document.querySelector('.main-layout')).flexDirection") == "row"
    sidebar_width = page.evaluate("() => document.querySelector('.sidebar').getBoundingClientRect().width")
    assert sidebar_width <= 260

    # 768 breakpoint
    page.set_viewport_size({"width": 768, "height": 900})
    page.wait_for_timeout(250)
    assert page.evaluate("() => getComputedStyle(document.querySelector('.main-layout')).flexDirection") == "column"
    assert _dashboard_columns(page) == 2

    # 480 breakpoint
    page.set_viewport_size({"width": 480, "height": 900})
    page.wait_for_timeout(250)
    assert _dashboard_columns(page) == 1
    assert page.evaluate(
        """() => {
            const el = document.querySelector('.tab-bar');
            return el.scrollWidth > el.clientWidth;
        }"""
    )

    for width in (1440, 1024, 768, 480):
        page.set_viewport_size({"width": width, "height": 900})
        page.wait_for_timeout(200)
        page.locator("#btnConfigLLM").click()
        assert _modal_centered(page)
        page.keyboard.press("Escape")

    context.close()


def test_service_worker_cached_graph_badge(frontend_server_url: str, browser):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    page.goto(f"{frontend_server_url}/", wait_until="domcontentloaded")

    # Ensure registration and warm cache while online.
    page.wait_for_timeout(1200)
    page.evaluate(
        """() => navigator.serviceWorker.ready.then(() => true)"""
    )
    page.locator('.tab-btn[data-tab="orchestration"]').click()
    page.locator("#mermaid-orchestration svg, #mermaid-orchestration .loading-text").first.wait_for(timeout=8000)
    page.locator('.tab-btn[data-tab="dashboard"]').click()

    # Keep reload on dashboard so graph cache starts empty in JS state.
    page.evaluate("() => localStorage.setItem('sw-active-tab', 'dashboard')")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(800)
    assert page.evaluate("() => !!navigator.serviceWorker.controller")

    context.set_offline(True)
    page.locator('.tab-btn[data-tab="orchestration"]').click()
    page.locator("#mermaid-orchestration .cache-badge").first.wait_for(timeout=8000)
    assert page.locator("#mermaid-orchestration .cache-badge").first.inner_text().strip().lower() == "cached"

    context.set_offline(False)
    context.close()
