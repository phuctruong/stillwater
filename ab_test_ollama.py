#!/usr/bin/env python3
"""
A|B Test: Ollama 8B with and without skills

Compare code quality metrics baseline vs with skill injection:
- A: Baseline (no skills)
- B: With skills (prime-coder injected)
"""

import sys
import json
import time
import subprocess
import ast
from pathlib import Path
from datetime import datetime

_CLI_SRC = Path(__file__).parent / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

from stillwater.llm_client import LLMClient

# Test tasks
TASKS = {
    "task_1_sum": {
        "name": "Simple Sum",
        "prompt": "Write a Python function that returns the sum of two numbers",
        "test": lambda code: eval(code + "\nassert sum_func(2, 3) == 5"),
    },
    "task_2_palindrome": {
        "name": "Check Palindrome",
        "prompt": "Write a function that checks if a string is a palindrome",
        "test": lambda code: eval(code + "\nassert is_palindrome('racecar') == True\nassert is_palindrome('hello') == False"),
    },
    "task_3_fibonacci": {
        "name": "Fibonacci",
        "prompt": "Write a function that returns the nth Fibonacci number",
        "test": lambda code: eval(code + "\nassert fibonacci(5) == 5"),
    },
}

# Skills to inject for B
SKILL_PACK = ["prime-safety", "prime-coder"]

def extract_code(response: str) -> str:
    """Extract Python code from response."""
    if "```python" in response:
        start = response.find("```python") + 9
        end = response.find("```", start)
        return response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        return response[start:end].strip()
    return response

def validate_syntax(code: str) -> tuple[bool, str]:
    """Check if code is valid Python."""
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, str(e)

def test_functionality(code: str, test_func) -> tuple[bool, str]:
    """Run test on generated code."""
    try:
        test_func(code)
        return True, ""
    except Exception as e:
        return False, str(e)

def load_skills() -> str:
    """Load and combine skill content."""
    skills_dir = Path(__file__).parent / "skills"
    parts = []

    for skill_name in SKILL_PACK:
        skill_file = skills_dir / f"{skill_name}.md"
        if skill_file.exists():
            content = skill_file.read_text()
            # Extract QUICK LOAD if available
            if "<!-- QUICK LOAD" in content:
                start = content.find("<!-- QUICK LOAD")
                end = content.find("-->", start) + 3
                parts.append(f"## {skill_name}\n{content[start:end]}")
            else:
                parts.append(f"## {skill_name}\n{content[:500]}")

    return "\n\n".join(parts)

def run_test(task_name: str, task_info: dict, with_skills: bool) -> dict:
    """Run A|B test on a single task."""
    print(f"\n  {task_name}: {'[WITH SKILLS]' if with_skills else '[BASELINE]'}", flush=True)

    # Create client with Ollama (use 3B Qwen Coder for fast inference)
    llm = LLMClient(provider="ollama", config={
        "ollama": {"model": "qwen2.5-coder:3b", "base_url": "http://localhost:11434"}
    })

    # Build prompt
    system_prompt = ""
    if with_skills:
        system_prompt = load_skills() + "\n\n"
    system_prompt += "You are an expert Python programmer. Write clean, working code."

    start = time.time()
    try:
        result = llm.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_info["prompt"]},
            ],
            model="qwen2.5-coder:3b",
            max_tokens=256,
            temperature=0.0,
            timeout=30.0,
        )
        latency = int((time.time() - start) * 1000)
        response_text = result.text
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        return {
            "task": task_name,
            "with_skills": with_skills,
            "success": False,
            "error": str(e),
            "latency_ms": latency,
        }

    # Extract and validate code
    code = extract_code(response_text)
    syntax_valid, syntax_error = validate_syntax(code)

    # Test functionality
    functional_pass = False
    functional_error = ""
    if syntax_valid:
        functional_pass, functional_error = test_functionality(code, task_info["test"])

    return {
        "task": task_name,
        "with_skills": with_skills,
        "success": syntax_valid and functional_pass,
        "syntax_valid": syntax_valid,
        "functional_pass": functional_pass,
        "syntax_error": syntax_error,
        "functional_error": functional_error,
        "code_length": len(code),
        "latency_ms": latency,
        "response": response_text[:200],
    }

def main():
    print("=" * 70)
    print("A|B Test: Ollama 3B (Qwen Coder) with/without Skills")
    print("=" * 70)
    print(f"\nModel: qwen2.5-coder:3b (Ollama) - much faster!")
    print(f"Tasks: {len(TASKS)}")
    print(f"Skills: {', '.join(SKILL_PACK)}")
    print("")

    results = []

    for task_name, task_info in TASKS.items():
        print(f"Testing: {task_info['name']}")

        # A: Baseline
        result_a = run_test(task_name, task_info, with_skills=False)
        results.append(result_a)
        print(f"    A (baseline): {'✓' if result_a['success'] else '✗'} ({result_a['latency_ms']}ms)")

        # B: With skills
        result_b = run_test(task_name, task_info, with_skills=True)
        results.append(result_b)
        print(f"    B (skills):   {'✓' if result_b['success'] else '✗'} ({result_b['latency_ms']}ms)")

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    baseline_pass = sum(1 for r in results if not r["with_skills"] and r["success"])
    skills_pass = sum(1 for r in results if r["with_skills"] and r["success"])
    baseline_total = len([r for r in results if not r["with_skills"]])
    skills_total = len([r for r in results if r["with_skills"]])

    baseline_pct = (baseline_pass / baseline_total * 100) if baseline_total > 0 else 0
    skills_pct = (skills_pass / skills_total * 100) if skills_total > 0 else 0
    uplift = skills_pct - baseline_pct

    print(f"\nBaseline (A): {baseline_pass}/{baseline_total} passed ({baseline_pct:.0f}%)")
    print(f"With Skills (B): {skills_pass}/{skills_total} passed ({skills_pct:.0f}%)")
    print(f"Uplift: {uplift:+.0f}%")

    # Save results
    output_file = Path(__file__).parent / "ab_test_ollama_3b_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "model": "qwen2.5-coder:3b",
            "baseline_pass_rate": baseline_pct,
            "skills_pass_rate": skills_pct,
            "uplift_percentage": uplift,
            "results": results,
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
