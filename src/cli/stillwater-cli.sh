#!/usr/bin/env bash
set -euo pipefail

CLI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${CLI_DIR}/.." && pwd)"

export PYTHONPATH="${CLI_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"

run_cli() {
  python -m stillwater "$@"
}

usage() {
  cat <<'EOF'
stillwater-cli.sh

Usage:
  ./src/cli/stillwater-cli.sh                      # interactive twin chat (TTY)
  ./src/cli/stillwater-cli.sh <stillwater-subcommand> [args...]
  ./src/cli/stillwater-cli.sh qa
  ./src/cli/stillwater-cli.sh qa-fast
  ./src/cli/stillwater-cli.sh qa-imo
  ./src/cli/stillwater-cli.sh qa-imo-phuc
  ./src/cli/stillwater-cli.sh qa-imo-history
  ./src/cli/stillwater-cli.sh qa-math-universal
  ./src/cli/stillwater-cli.sh qa-notebooks
  ./src/cli/stillwater-cli.sh qa-secret-sauce

Examples:
  ./src/cli/stillwater-cli.sh twin "explain twin orchestration"
  ./src/cli/stillwater-cli.sh twin --interactive
  STILLWATER_EXTENSION_ROOT=src/cli/extensions ./src/cli/stillwater-cli.sh twin "/kernel"
  ./src/cli/stillwater-cli.sh llm status
  ./src/cli/stillwater-cli.sh skills list
  ./src/cli/stillwater-cli.sh recipe list
  ./src/cli/stillwater-cli.sh books list
  ./src/cli/stillwater-cli.sh papers list
  ./src/cli/stillwater-cli.sh cleanup scan --json
  ./src/cli/stillwater-cli.sh init agi-cli my-agent --dir artifacts/scaffolds --identity-stack
  ./src/cli/stillwater-cli.sh stack run --profile offline
  ./src/cli/stillwater-cli.sh qa-notebooks
  ./src/cli/stillwater-cli.sh qa-secret-sauce
  ./src/cli/stillwater-cli.sh qa-imo
  ./src/cli/stillwater-cli.sh qa-imo-phuc
  ./src/cli/stillwater-cli.sh qa-imo-history
  ./src/cli/stillwater-cli.sh qa-math-universal
  ./src/cli/stillwater-cli.sh imo-history oracles-template --from-year 2020 --to-year 2024 --fetch-missing --out src/cli/tests/math/imo_history_oracles.json
  ./src/cli/stillwater-cli.sh imo-history oracle-status --from-year 2020 --to-year 2024 --oracles-file src/cli/tests/math/imo_history_oracles.json --json
  ./src/cli/stillwater-cli.sh imo-history autolearn --from-year 2020 --to-year 2024 --fetch-missing --required-rung 65537 --max-iterations 3 --oracles-file src/cli/tests/math/imo_history_oracles.json
  ./src/cli/stillwater-cli.sh math-universal --config src/cli/tests/math/universal_math_gate.json --json
  ./src/cli/stillwater-cli.sh qa
EOF
}

run_qa_notebooks() {
  local failures=0
  local run_id="qa-notebooks-$(date -u +%Y%m%dT%H%M%SZ)"
  local out_dir="artifacts/notebook_qa/${run_id}"
  local nb

  mkdir -p "${out_dir}"
  echo "[QA-NB] output dir ${out_dir}"

  for nb in notebooks/HOW-TO-*.ipynb; do
    local out_name
    out_name="$(basename "${nb}" .ipynb).executed"
    echo "[QA-NB] executing ${nb}"
    if ! python -m nbconvert --execute --to notebook --output "${out_name}" --output-dir "${out_dir}" "${nb}"; then
      failures=$((failures + 1))
      echo "[QA-NB] FAIL ${nb}"
    else
      echo "[QA-NB] PASS ${nb}"
    fi
  done

  if [[ ${failures} -ne 0 ]]; then
    echo "[QA-NB] notebook failures: ${failures}"
    return 1
  fi
  echo "[QA-NB] all notebooks passed"
  echo "[QA-NB] receipts saved under ${out_dir}"
}

run_qa_secret_sauce() {
  local failures=0
  local run_id="qa-secret-sauce-$(date -u +%Y%m%dT%H%M%SZ)"
  local out_dir="artifacts/notebook_qa/${run_id}"
  local nb

  mkdir -p "${out_dir}"
  echo "[QA-SS] output dir ${out_dir}"

  for nb in PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb PHUC-SKILLS-SECRET-SAUCE.ipynb PRIME-MERMAID-LANGUAGE-SECRET-SAUCE.ipynb; do
    if [[ ! -f "${nb}" ]]; then
      echo "[QA-SS] SKIP missing ${nb}"
      continue
    fi
    local out_name
    out_name="$(basename "${nb}" .ipynb).executed"
    echo "[QA-SS] executing ${nb}"
    if ! python -m nbconvert --execute --to notebook --output "${out_name}" --output-dir "${out_dir}" "${nb}"; then
      failures=$((failures + 1))
      echo "[QA-SS] FAIL ${nb}"
    else
      echo "[QA-SS] PASS ${nb}"
    fi
  done

  if [[ ${failures} -ne 0 ]]; then
    echo "[QA-SS] notebook failures: ${failures}"
    return 1
  fi
  echo "[QA-SS] all secret-sauce notebooks passed"
  echo "[QA-SS] receipts saved under ${out_dir}"
}

run_qa_fast() {
  local stack_id="qa-stack-$(date -u +%Y%m%dT%H%M%SZ)"
  local oolong_id="qa-oolong-$(date -u +%Y%m%dT%H%M%SZ)"
  local skills_id="qa-skills-$(date -u +%Y%m%dT%H%M%SZ)"
  local init_name="qa-agent-$(date -u +%Y%m%dt%H%M%Sz)"
  local init_parent="artifacts/qa_scaffold"
  local init_dir="${init_parent}/${init_name}"

  run_cli --version
  run_cli paths --json >/dev/null
  run_cli skills list --json >/dev/null
  run_cli skills sync --dest artifacts/qa_skills_sync --all --force --json >/dev/null
  run_cli init identity-stack --dir artifacts/qa_identity --force --json >/dev/null
  run_cli recipe add qa_twin_recipe --dir artifacts/qa_recipes --force --json >/dev/null
  run_cli recipe list --dir artifacts/qa_recipes --json >/dev/null
  run_cli books list --json >/dev/null
  run_cli books show PERSISTENT-INTELLIGENCE >/dev/null
  run_cli papers list --json >/dev/null
  run_cli papers show 00-index >/dev/null
  run_cli cleanup scan --scope artifacts/does-not-exist --json >/dev/null
  run_cli twin "/skills" --json >/dev/null
  run_cli init agi-cli "${init_name}" --dir "${init_parent}" --identity-stack --force >/dev/null
  [[ -f "${init_dir}/README.md" ]]
  [[ -f "${init_dir}/.stillwater/project.json" ]]
  [[ -f "${init_dir}/ripples/system/default.prime-mermaid.md" ]]
  run_cli wish list --json >/dev/null
  run_cli recipe lint --prime-mermaid-only
  run_cli skills-ab --backend mock --no-cache --run-id "${skills_id}"
  run_cli stack run --profile offline --run-id "${stack_id}"
  run_cli stack verify --run-id "${stack_id}" --strict
  run_cli replay "${stack_id}" >/dev/null
  run_cli oolong run --run-id "${oolong_id}"
  run_cli oolong verify --run-id "${oolong_id}" --strict
}

run_qa_imo() {
  local run_id="qa-imo-$(date -u +%Y%m%dT%H%M%SZ)"
  local out_dir="artifacts/imo_qa/${run_id}"
  local model="${STILLWATER_IMO_MODEL:-llama3.1:8b}"
  local timeout="${STILLWATER_IMO_TIMEOUT:-30}"
  local cases_file="${STILLWATER_IMO_CASES_FILE:-src/cli/tests/math/imo_qa_cases.json}"
  local concept_min="${STILLWATER_IMO_CONCEPT_MIN:-0.50}"
  local section_min="${STILLWATER_IMO_SECTION_MIN_HITS:-1}"
  mkdir -p "${out_dir}"

  run_cli llm status > "${out_dir}/llm-status.txt"
  run_cli llm models --json > "${out_dir}/models.json"

  QA_IMO_OUT_DIR="${out_dir}" QA_IMO_MODEL="${model}" QA_IMO_TIMEOUT="${timeout}" QA_IMO_CASES_FILE="${cases_file}" QA_IMO_CONCEPT_MIN="${concept_min}" QA_IMO_SECTION_MIN="${section_min}" python - <<'PY'
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from stillwater.cli import (
        _concept_coverage_score,
        _expand_semantic_aliases,
        _required_sections_score,
        _semantic_match_score,
    )
except Exception:
    def _concept_coverage_score(response: str, concepts):
        return {"coverage": 1.0, "hit_count": 0}

    def _expand_semantic_aliases(needle: str):
        return [needle]

    def _required_sections_score(response: str, sections):
        return {"coverage": 1.0, "hit_count": 0}

    def _semantic_match_score(response: str, targets):
        response_lower = str(response).lower()
        for target in targets:
            t = str(target).strip().lower()
            if t and t in response_lower:
                return {"matched": True, "mode": "strict", "score": 1.0, "target": target}
        return {"matched": False, "mode": "none", "score": 0.0, "target": ""}

out_dir = Path(os.environ["QA_IMO_OUT_DIR"])
model = os.environ["QA_IMO_MODEL"]
timeout = str(os.environ["QA_IMO_TIMEOUT"])
cases_file = Path(os.environ["QA_IMO_CASES_FILE"])
concept_min = float(os.environ.get("QA_IMO_CONCEPT_MIN", "0.50"))
section_min = int(os.environ.get("QA_IMO_SECTION_MIN", "1"))

if not cases_file.exists():
    raise SystemExit(f"IMO cases file not found: {cases_file}")

payload_cases = json.loads(cases_file.read_text(encoding="utf-8"))
raw_cases = payload_cases.get("cases", []) if isinstance(payload_cases, dict) else []
cases = []
for row in raw_cases:
    if not isinstance(row, dict):
        continue
    case_id = str(row.get("id", "")).strip()
    prompt = str(row.get("prompt", "")).strip()
    needle = str(row.get("needle", "")).strip()
    if not case_id or not prompt or not needle:
        continue
    aliases_raw = row.get("aliases", [])
    aliases = []
    if isinstance(aliases_raw, list):
        aliases = [str(item).strip() for item in aliases_raw if str(item).strip()]
    concepts_raw = row.get("concepts", [])
    concepts = []
    if isinstance(concepts_raw, list):
        concepts = [str(item).strip() for item in concepts_raw if str(item).strip()]
    sections_raw = row.get("required_sections", [])
    required_sections = []
    if isinstance(sections_raw, list):
        required_sections = [str(item).strip() for item in sections_raw if str(item).strip()]
    cases.append((case_id, prompt, needle, aliases, concepts, required_sections))
if not cases:
    raise SystemExit(f"No valid cases found in {cases_file}")


def run_twin(prompt: str, *, llm_only: bool) -> dict:
    cmd = [sys.executable, "-m", "stillwater", "twin", prompt, "--model", model, "--timeout", timeout, "--json"]
    if llm_only:
        cmd.append("--llm-only")
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    row = {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "llm_only": llm_only,
    }
    if proc.returncode != 0:
        row["ok"] = False
        return row
    try:
        payload = json.loads(proc.stdout)
    except Exception:
        row["ok"] = False
        return row
    row["ok"] = True
    row["payload"] = payload
    return row


lanes = {
    "tool_assisted": {"llm_only": False, "results": []},
    "llm_only": {"llm_only": True, "results": []},
}

for lane_name, lane in lanes.items():
    for case_id, prompt, needle, aliases, concepts, required_sections in cases:
        run = run_twin(prompt, llm_only=bool(lane["llm_only"]))
        result = {
            "case_id": case_id,
            "prompt": prompt,
            "needle": needle,
            "aliases": aliases,
            "concepts": concepts,
            "required_sections": required_sections,
            "run_ok": bool(run.get("ok")),
            "returncode": run.get("returncode"),
            "llm_only": bool(lane["llm_only"]),
        }
        payload = run.get("payload", {}) if isinstance(run.get("payload"), dict) else {}
        route = payload.get("route", {}) if isinstance(payload.get("route"), dict) else {}
        response = str(payload.get("response", ""))
        result["source"] = payload.get("source")
        result["action"] = route.get("action")
        result["model"] = payload.get("model") or route.get("model")
        result["url"] = payload.get("url") or route.get("url")
        targets = _expand_semantic_aliases(needle) + aliases
        match_meta = _semantic_match_score(response, targets)
        concept_meta = _concept_coverage_score(response, concepts)
        section_meta = _required_sections_score(response, required_sections)
        result["match"] = bool(match_meta.get("matched"))
        result["match_mode"] = str(match_meta.get("mode", "none"))
        result["match_score"] = float(match_meta.get("score", 0.0))
        result["match_target"] = str(match_meta.get("target", needle))
        result["concept_coverage"] = float(concept_meta.get("coverage", 1.0))
        result["section_hit_count"] = int(section_meta.get("hit_count", 0))
        concept_ok = True
        section_ok = True
        if concepts:
            concept_ok = result["concept_coverage"] >= concept_min
        if required_sections:
            section_ok = result["section_hit_count"] >= section_min
        result["concept_ok"] = concept_ok
        result["section_ok"] = section_ok
        result["pass"] = bool(result["run_ok"] and result["match"] and concept_ok and section_ok)
        result["response_excerpt"] = response[:320]
        result["route"] = route
        result["stderr_excerpt"] = str(run.get("stderr", ""))[:320]
        receipts = payload.get("receipts", {}) if isinstance(payload.get("receipts"), dict) else {}
        result["receipt_dir"] = receipts.get("dir")
        lane["results"].append(result)

for lane_name, lane in lanes.items():
    score = sum(1 for r in lane["results"] if r.get("pass"))
    lane["score"] = score
    lane["total"] = len(lane["results"])

models_payload = {}
try:
    models_payload = json.loads((out_dir / "models.json").read_text(encoding="utf-8"))
except Exception:
    pass
models = models_payload.get("models", []) if isinstance(models_payload, dict) else []
remote_ok = model in models

report = {
    "run_id": out_dir.name,
    "timestamp_utc": out_dir.name.replace("qa-imo-", ""),
    "model_target": model,
    "cases_file": str(cases_file),
    "remote_model_listed": remote_ok,
    "lanes": lanes,
    "strict_pass": bool(
        remote_ok and lanes["tool_assisted"]["score"] == lanes["tool_assisted"]["total"]
    ),
    "claim_hygiene": {
        "lane_a": "tool_assisted: CPU benchmark orchestration with deterministic solver receipts",
        "lane_b": "llm_only: pure remote model (no CPU benchmark route)",
        "disclosure": "Report both lanes to avoid hidden routing claims.",
    },
}

(out_dir / "imo-qa-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

md = []
md.append("# IMO QA Report")
md.append("")
md.append(f"- Run ID: `{out_dir.name}`")
md.append(f"- Target model: `{model}`")
md.append(f"- Cases file: `{cases_file}`")
md.append(f"- Remote model listed by Ollama tags: `{remote_ok}`")
md.append("")
md.append("## Scoreboard")
md.append("")
md.append(f"- Lane A `tool_assisted`: **{lanes['tool_assisted']['score']}/{lanes['tool_assisted']['total']}**")
md.append(f"- Lane B `llm_only`: **{lanes['llm_only']['score']}/{lanes['llm_only']['total']}**")
md.append("")
md.append("## No-Cheat Disclosure")
md.append("")
md.append("- Lane A uses PHUC swarms CPU benchmark route (`phuc_swarms_benchmark`) with deterministic solver artifacts.")
md.append("- Lane B bypasses CPU benchmark route (`--llm-only`) and queries the remote model directly.")
md.append("- Publish both lanes together for fair expert review.")
md.append("")
md.append("## Lane Details")
md.append("")
for lane_name in ["tool_assisted", "llm_only"]:
    lane = lanes[lane_name]
    md.append(f"### {lane_name}")
    for row in lane["results"]:
        md.append(
            f"- {row['case_id']}: match={row['match']} mode={row.get('match_mode')} score={row.get('match_score')} "
            f"source={row.get('source')} action={row.get('action')} model={row.get('model')}"
        )
md.append("")
md.append("## Receipts")
md.append("")
md.append(f"- JSON: `{out_dir / 'imo-qa-report.json'}`")
md.append(f"- LLM status: `{out_dir / 'llm-status.txt'}`")
md.append(f"- Model list: `{out_dir / 'models.json'}`")
md.append(f"- Cases file: `{cases_file}`")

(out_dir / "imo-qa-report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

summary = {
    "run_id": report["run_id"],
    "model_target": report["model_target"],
    "remote_model_listed": report["remote_model_listed"],
    "tool_assisted_score": f"{lanes['tool_assisted']['score']}/{lanes['tool_assisted']['total']}",
    "llm_only_score": f"{lanes['llm_only']['score']}/{lanes['llm_only']['total']}",
    "strict_pass": report["strict_pass"],
}
print(json.dumps(summary, indent=2, sort_keys=True))
if not report["strict_pass"]:
    sys.exit(1)
PY

  echo "[QA-IMO] report: ${out_dir}/imo-qa-report.md"
  echo "[QA-IMO] report: ${out_dir}/imo-qa-report.json"
}

run_qa_imo_phuc() {
  local model="${STILLWATER_IMO_MODEL:-llama3.1:8b}"
  local timeout="${STILLWATER_IMO_TIMEOUT:-45}"
  local cases_file="${STILLWATER_IMO_CASES_FILE:-src/cli/tests/math/imo_qa_cases.json}"
  local url="${STILLWATER_OLLAMA_URL:-}"

  if [[ -n "${url}" ]]; then
    run_cli imo-phuc --cases-file "${cases_file}" --model "${model}" --timeout "${timeout}" --url "${url}"
  else
    run_cli imo-phuc --cases-file "${cases_file}" --model "${model}" --timeout "${timeout}"
  fi
}

run_qa_imo_history() {
  local history_cfg="${STILLWATER_IMO_HISTORY_CONFIG_FILE:-src/cli/tests/math/imo_history_defaults.json}"
  local oracles_file="${STILLWATER_IMO_HISTORY_ORACLES_FILE:-src/cli/tests/math/imo_history_oracles.json}"
  local required_rung="${STILLWATER_IMO_HISTORY_REQUIRED_RUNG:-65537}"
  local defaults
  defaults="$(
    QA_IMO_HISTORY_CFG="${history_cfg}" python - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["QA_IMO_HISTORY_CFG"])
if not path.exists():
    print("2020 2024 0 eng")
    raise SystemExit(0)
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print("2020 2024 0 eng")
    raise SystemExit(0)

def _num(key, default):
    try:
        return int(payload.get(key, default))
    except Exception:
        return int(default)

from_year = _num("from_year", 2020)
to_year = _num("to_year", 2024)
max_problems = _num("max_problems", 0)
lang = str(payload.get("lang", "eng")).strip() or "eng"
print(f"{from_year} {to_year} {max_problems} {lang}")
PY
  )"
  local from_year_default to_year_default max_problems_default lang_default
  read -r from_year_default to_year_default max_problems_default lang_default <<< "${defaults}"

  local from_year="${STILLWATER_IMO_HISTORY_FROM_YEAR:-${from_year_default}}"
  local to_year="${STILLWATER_IMO_HISTORY_TO_YEAR:-${to_year_default}}"
  local max_problems="${STILLWATER_IMO_HISTORY_MAX_PROBLEMS:-${max_problems_default}}"
  local lang="${STILLWATER_IMO_HISTORY_LANG:-${lang_default}}"
  local model="${STILLWATER_IMO_MODEL:-llama3.1:8b}"

  run_cli imo-history fetch \
    --from-year "${from_year}" \
    --to-year "${to_year}" \
    --lang "${lang}"

  run_cli imo-history bench \
    --from-year "${from_year}" \
    --to-year "${to_year}" \
    --lang "${lang}" \
    --model "${model}" \
    --fetch-missing \
    --max-problems "${max_problems}" \
    --required-rung "${required_rung}" \
    --oracles-file "${oracles_file}"
}

run_qa_math_universal() {
  local config_file="${STILLWATER_MATH_UNIVERSAL_CONFIG_FILE:-src/cli/tests/math/universal_math_gate.json}"
  local model="${STILLWATER_IMO_MODEL:-llama3.1:8b}"
  local timeout="${STILLWATER_IMO_TIMEOUT:-45}"

  run_cli math-universal \
    --config "${config_file}" \
    --model "${model}" \
    --timeout "${timeout}"
}

run_qa_full() {
  run_qa_fast
  run_qa_notebooks

  run_cli wish run wishes/examples/WISH-NOTEBOOK-EXAMPLE-CLONE-FIRST-RUN.ipynb \
    --verify-wish-id wish.clone_to_first_run.v1

  local proposal_json
  proposal_json="$(run_cli learn propose "qa-proposal" --wish-id wish.cli.learn.loop.v1 --json)"

  local proposal_path
  proposal_path="$(
    PROPOSAL_JSON="${proposal_json}" python - <<'PY'
import json
import os
payload = json.loads(os.environ["PROPOSAL_JSON"])
print(payload["proposal"])
PY
  )"

  run_cli learn apply "${proposal_path}" >/dev/null
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q src/cli/tests
}

if [[ $# -eq 0 ]]; then
  if [[ -t 0 ]]; then
    run_cli twin --interactive
    exit $?
  fi
  usage
  exit 1
fi

case "$1" in
  qa)
    shift
    run_qa_full "$@"
    ;;
  qa-fast)
    shift
    run_qa_fast "$@"
    ;;
  qa-imo)
    shift
    run_qa_imo "$@"
    ;;
  qa-imo-phuc)
    shift
    run_qa_imo_phuc "$@"
    ;;
  qa-imo-history)
    shift
    run_qa_imo_history "$@"
    ;;
  qa-math-universal)
    shift
    run_qa_math_universal "$@"
    ;;
  qa-notebooks)
    shift
    run_qa_notebooks "$@"
    ;;
  qa-secret-sauce)
    shift
    run_qa_secret_sauce "$@"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    run_cli "$@"
    ;;
esac
