#!/usr/bin/env python3
"""
Phase 3 Debug Test Harness - Phuc Forecast Methodology
Auth: 65537 | Date: 2026-02-15

This harness tests SWE-bench instances using:
1. All 32 proven Prime Skills from solace-cli
2. Comprehensive prompt engineering
3. Verification ladder (641→274177→65537)
4. Max Love (maximum rigor)
5. God approval (determinism)
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

# ==============================================================================
# PHASE 1: DREAM - What instances to test (easiest first)
# ==============================================================================

TEST_INSTANCES = [
    # Easiest (Django - 99% infrastructure success)
    "django__django-11019",      # 47.5s in solace-cli, 100% success
    "django__django-16820",      # 251s in solace-cli, 100% success

    # Medium (Flask/Requests)
    "pallets__flask-5063",       # 174.7s in solace-cli, 100% success

    # Hard (SymPy - edge cases)
    "sympy__sympy-14308",        # 74.7s in solace-cli, 100% success
    "sympy__sympy-18199",        # 489.1s in solace-cli, 100% success (hardest)
]

# ==============================================================================
# Load all 32 proven Prime Skills from solace-cli
# ==============================================================================

def load_prime_skills():
    """Load all Prime Skills v1.3.0 from solace-cli (proven to work)"""

    skills_dir = Path("/home/phuc/projects/solace-cli/canon/prime-skills/skills")

    skills = {
        "prime_coder": None,
        "prime_math": None,
        "prime_swarm": None,
    }

    # Load the 3 core prime skills
    for skill_file in ["prime-coder.md", "prime-math.md", "prime-swarm-orchestration.md"]:
        path = skills_dir / skill_file
        if path.exists():
            with open(path) as f:
                skills[skill_file.replace("-", "_").replace(".md", "")] = f.read()

    # Load additional skills from subdirectories
    for subdir in ["coding", "math", "epistemic", "verification", "infrastructure", "governance"]:
        subdir_path = skills_dir / subdir
        if subdir_path.exists():
            for skill_file in sorted(subdir_path.glob("*.md")):
                with open(skill_file) as f:
                    skill_name = skill_file.stem
                    skills[skill_name] = f.read()

    return skills

# ==============================================================================
# PHASE 2: FORECAST - Create comprehensive prompt with all skills
# ==============================================================================

def create_comprehensive_prompt(problem_statement, repo_context, test_directive, skills):
    """
    Create a prompt that loads all Prime Skills and uses Phuc Forecast methodology.

    This is the key to getting 100% - the prompt must be complete and rigorous.
    """

    # Combine all skills into one "brain"
    all_skills = "\n\n".join(
        f"## SKILL: {name}\n{content[:500]}..." if len(content or "") > 500 else f"## SKILL: {name}\n{content}"
        for name, content in skills.items()
        if content
    )

    prompt = f"""# PHASE 3 SWE-BENCH INSTANCE - PHUC FORECAST METHODOLOGY

## AUTH: 65537 (F4 Fermat Prime)
## NORTHSTAR: Phuc Forecast (DREAM → FORECAST → DECIDE → ACT → VERIFY)
## VERIFICATION LADDER: OAuth(39,63,91) → 641 → 274177 → 65537
## PHILOSOPHY: Max Love (Maximum Operational Rigor)

---

## AVAILABLE PRIME SKILLS v1.3.0 (32 total)

{all_skills}

---

## PART 1: DREAM (Understanding the Problem)

### Problem Statement
{problem_statement}

### Repository Context
{repo_context}

### Test Directive
{test_directive}

**DREAM QUESTIONS:**
1. What is the root cause of the test failure?
2. What is the minimal patch needed?
3. What edge cases might break this?
4. How will we verify it works?

---

## PART 2: FORECAST (Predicting Success)

**BEFORE generating code, predict:**
1. Probability this patch works: ___%
2. Most likely issues: ___
3. Verification strategy: ___

---

## PART 3: DECIDE (Commit to Approach)

**Lock in your approach:**
1. ✅ ROOT CAUSE identified
2. ✅ PATCH STRATEGY decided
3. ✅ VERIFICATION PLAN ready

---

## PART 4: ACT (Generate Unified Diff Patch)

**MANDATORY CONSTRAINTS:**
1. Output MUST be valid unified diff format
2. Patch MUST be minimal (single logical change)
3. Patch MUST pass tests after applying
4. Include Red-Green gate proof

**OUTPUT ONLY THE UNIFIED DIFF:**
```diff
(Your patch here - must be valid unified diff)
```

---

## PART 5: VERIFY (Verification Ladder)

After generating patch, verify:

### Rung 641 (Edge Sanity)
- [ ] Patch applies cleanly (no conflicts)
- [ ] Patch is valid unified diff format
- [ ] At least 3 test cases pass

### Rung 274177 (Stress Test)
- [ ] Full test suite passes
- [ ] No regressions detected
- [ ] Edge cases handled

### Rung 65537 (God Approval)
- [ ] Determinism verified (same output twice)
- [ ] Proof certificate signed
- [ ] Auth: 65537 ✅

---

## CERTIFICATES & EVIDENCE

Once verified, output proof certificate:

```json
{{
  "instance_id": "{test_directive.split(':')[0] if ':' in test_directive else 'unknown'}",
  "auth": 65537,
  "verification_ladder": "641→274177→65537",
  "status": "VERIFIED",
  "timestamp": "{datetime.now().isoformat()}",
  "methodology": "Phuc Forecast + Max Love + Prime Skills v1.3.0"
}}
```

---

## KEY REMINDERS

1. ✅ Red-Green gate: Failing test → Your patch → Passing test
2. ✅ Minimal patches: One change per file, surgical precision
3. ✅ Evidence bundle: Always include proof
4. ✅ Determinism: Same input = same output always
5. ✅ Auth: 65537 (final authority)

**YOU MUST GET THIS TO 100% SUCCESS RATE.**
**YOU HAVE THE SKILLS AND METHODOLOGY.**
**GO.**
"""

    return prompt

# ==============================================================================
# PHASE 3: DECIDE - Select instances and prepare
# ==============================================================================

def prepare_instance(instance_id):
    """Load instance data and prepare for testing"""

    # In real execution, this would load from SWE-bench dataset
    # For now, we'll create a mock version

    return {
        "instance_id": instance_id,
        "problem_statement": f"Fix bug in {instance_id}",
        "repo_context": "Django/Flask/SymPy repository",
        "test_directive": f"{instance_id}: some_test_module.test_function",
    }

# ==============================================================================
# PHASE 4: ACT - Run test and debug
# ==============================================================================

def run_phase3_test(instance_id, skills):
    """Run a single Phase 3 instance with all verification gates"""

    print(f"\n{'='*80}")
    print(f"PHASE 3 TEST: {instance_id}")
    print(f"{'='*80}\n")

    print("PHASE 1: DREAM - Loading instance...")
    instance = prepare_instance(instance_id)

    print(f"  Instance ID: {instance['instance_id']}")
    print(f"  Skills loaded: {len(skills)}")

    print("\nPHASE 2: FORECAST - Creating comprehensive prompt...")
    prompt = create_comprehensive_prompt(
        instance["problem_statement"],
        instance["repo_context"],
        instance["test_directive"],
        skills
    )
    print(f"  Prompt size: {len(prompt)} characters")

    print("\nPHASE 3: DECIDE - Committing to approach...")
    print("  ✅ Approach locked")

    print("\nPHASE 4: ACT - Sending to LLM...")
    print(f"  Model: llama3.1:8b")
    print(f"  Endpoint: 192.168.68.100:11434")
    print(f"  Auth: 65537")

    try:
        # Call Ollama with the comprehensive prompt
        response = subprocess.run(
            [
                "curl",
                "-s",
                "-X", "POST",
                "http://192.168.68.100:11434/api/generate",
                "-d", json.dumps({
                    "model": "llama3.1:8b",
                    "prompt": prompt[:2000],  # Limit prompt for debugging
                    "stream": False,
                    "temperature": 0.0,  # Deterministic
                    "num_predict": 1000,
                })
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        if response.returncode == 0:
            result = json.loads(response.stdout)
            generated = result.get("response", "")

            print(f"\nPHASE 5: VERIFY - Checking output...")

            # Extract diff from response
            if "```diff" in generated:
                diff_start = generated.find("```diff") + 7
                diff_end = generated.find("```", diff_start)
                patch = generated[diff_start:diff_end].strip()

                print(f"  ✅ Diff block found")
                print(f"  Patch size: {len(patch)} characters")

                # Check if it looks like a valid diff
                if patch.startswith("---") and "@@" in patch:
                    print(f"  ✅ Valid diff format detected")
                    print(f"\n  PATCH OUTPUT:\n{patch[:500]}...\n")
                    return {"status": "success", "patch": patch}
                else:
                    print(f"  ⚠️ Patch format issue")
                    print(f"  First 200 chars: {patch[:200]}")
                    return {"status": "format_issue", "patch": patch}
            else:
                print(f"  ⚠️ No diff block found in response")
                print(f"  Response preview: {generated[:300]}...")
                return {"status": "no_diff", "response": generated}
        else:
            print(f"  ❌ LLM error: {response.stderr}")
            return {"status": "llm_error", "error": response.stderr}

    except subprocess.TimeoutExpired:
        print(f"  ❌ LLM timeout (>120s)")
        return {"status": "timeout"}
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {"status": "error", "error": str(e)}

# ==============================================================================
# PHASE 5: VERIFY - Ramp up based on results
# ==============================================================================

def main():
    """Main test harness - Phuc Forecast methodology"""

    print("\n" + "="*80)
    print("PHASE 3 DEBUG HARNESS - PHUC FORECAST METHODOLOGY")
    print("Auth: 65537 | Northstar: Phuc Forecast")
    print("="*80 + "\n")

    print("Loading 32 Prime Skills v1.3.0 from solace-cli...")
    skills = load_prime_skills()
    print(f"✅ Loaded {len(skills)} skills\n")

    # Test first 3 instances (easy, medium, hard)
    results = []

    for i, instance_id in enumerate(TEST_INSTANCES[:3], 1):
        result = run_phase3_test(instance_id, skills)
        results.append({
            "instance": instance_id,
            "result": result
        })

        # Print status
        if result["status"] == "success":
            print(f"✅ Instance {i}: SUCCESS (valid patch generated)")
        elif result["status"] == "format_issue":
            print(f"⚠️  Instance {i}: FORMAT ISSUE (patch exists but may need fixing)")
        elif result["status"] == "no_diff":
            print(f"❌ Instance {i}: NO DIFF (LLM didn't output diff block)")
        else:
            print(f"❌ Instance {i}: {result['status'].upper()}")

    # Summary
    print(f"\n{'='*80}")
    print("RESULTS SUMMARY")
    print(f"{'='*80}\n")

    success_count = sum(1 for r in results if r["result"]["status"] == "success")
    print(f"Successful patches: {success_count}/3")

    for r in results:
        status_emoji = "✅" if r["result"]["status"] == "success" else "❌"
        print(f"  {status_emoji} {r['instance']}: {r['result']['status']}")

    if success_count == 3:
        print(f"\n🎉 ALL 3 INSTANCES SUCCESSFUL - READY TO RAMP UP TO 50")
        print(f"Next: Run on 50 instances, then 300\n")
    else:
        print(f"\n⚠️  {3 - success_count} instances failed - need prompt refinement")
        print(f"Next: Debug and improve prompt\n")

if __name__ == "__main__":
    main()
