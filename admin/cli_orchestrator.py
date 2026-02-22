#!/usr/bin/env python3
"""
Stillwater CLI Orchestrator v3
Auth: 65537 | Status: REFACTORED

Instead of calling LLM directly, the CLI now:
1. Hits the LLM Portal at http://localhost:8788
2. Sends swarm execution requests
3. Gets back responses

The portal handles:
- Loading swarm metadata
- Injecting skills
- Calling LLM models
- Recipe execution on CPU nodes

Usage:
  python cli_orchestrator.py --swarm coder --prompt "Write a function" --model sonnet
  python cli_orchestrator.py --recipe gmail --task "Read emails"
"""

import sys
import argparse
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


# ============================================================
# Configuration
# ============================================================

PORTAL_URL = "http://localhost:8788"
DEFAULT_MODEL = "sonnet"
DEFAULT_SWARM = "coder"


# ============================================================
# Swarm Execution
# ============================================================

def execute_swarm(
    swarm_type: str,
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 2048,
    temperature: float = 0.0,
) -> dict:
    """Execute swarm via portal."""
    print(f"[CLI] Executing swarm: {swarm_type}")
    print(f"[CLI] Model: {model}")
    print(f"[CLI] Prompt length: {len(prompt)} chars")

    try:
        response = requests.post(
            f"{PORTAL_URL}/v1/swarm/execute",
            json={
                "swarm_type": swarm_type,
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=120,
        )

        if response.status_code != 200:
            print(f"[CLI] Error: {response.status_code}")
            print(f"[CLI] {response.text}")
            return {"success": False, "error": response.text}

        result = response.json()
        print(f"[CLI] Response received ({len(result.get('response', ''))} chars)")
        return result

    except requests.ConnectionError:
        return {
            "success": False,
            "error": f"Portal not running at {PORTAL_URL}. Start with: python admin/llm_portal_v3.py",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# Recipe Execution
# ============================================================

def execute_recipe(
    recipe_name: str,
    task: str,
    context: dict = None,
) -> dict:
    """Execute recipe via portal."""
    print(f"[CLI] Executing recipe: {recipe_name}")
    print(f"[CLI] Task: {task}")

    try:
        response = requests.post(
            f"{PORTAL_URL}/v1/recipe/execute",
            json={
                "recipe_name": recipe_name,
                "task": task,
                "context": context or {},
            },
            timeout=120,
        )

        if response.status_code != 200:
            print(f"[CLI] Error: {response.status_code}")
            print(f"[CLI] {response.text}")
            return {"success": False, "error": response.text}

        result = response.json()
        print(f"[CLI] Recipe execution complete")
        return result

    except requests.ConnectionError:
        return {
            "success": False,
            "error": f"Portal not running at {PORTAL_URL}. Start with: python admin/llm_portal_v3.py",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# Health Check
# ============================================================

def check_portal_health() -> bool:
    """Check if portal is running."""
    try:
        response = requests.get(f"{PORTAL_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# ============================================================
# Main CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Stillwater CLI Orchestrator - Hits LLM Portal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute coder swarm
  python cli_orchestrator.py --swarm coder --prompt "Write a function to sum a list" --model sonnet

  # Execute recipe
  python cli_orchestrator.py --recipe gmail --task "Read unread emails"

  # Check portal health
  python cli_orchestrator.py --health
        """,
    )

    parser.add_argument(
        "--swarm",
        type=str,
        default=None,
        help=f"Swarm type to execute (default: {DEFAULT_SWARM})",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Prompt/task for swarm execution",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        choices=["haiku", "sonnet", "opus"],
        help=f"LLM model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--recipe",
        type=str,
        default=None,
        help="Recipe to execute on CPU nodes",
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Task for recipe execution",
    )
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="JSON context for recipe (e.g., '{\"email\": \"me@example.com\"}')",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Check portal health and exit",
    )

    args = parser.parse_args()

    # Health check
    if args.health:
        print(f"[CLI] Checking portal health at {PORTAL_URL}...")
        if check_portal_health():
            print("[CLI] ✅ Portal is healthy")
            sys.exit(0)
        else:
            print("[CLI] ❌ Portal is not running")
            print(f"[CLI] Start with: python admin/llm_portal_v3.py")
            sys.exit(1)

    # Swarm execution
    if args.swarm or args.prompt:
        if not args.prompt:
            print("[CLI] Error: --prompt required for swarm execution")
            sys.exit(1)

        swarm_type = args.swarm or DEFAULT_SWARM
        result = execute_swarm(
            swarm_type=swarm_type,
            prompt=args.prompt,
            model=args.model,
        )

        if result["success"]:
            print("\n" + "=" * 70)
            print("RESPONSE FROM SWARM")
            print("=" * 70)
            print(result["response"])
            print("=" * 70)
        else:
            print(f"[CLI] Failed: {result['error']}")
            sys.exit(1)

        sys.exit(0)

    # Recipe execution
    if args.recipe:
        if not args.task:
            print("[CLI] Error: --task required for recipe execution")
            sys.exit(1)

        context = {}
        if args.context:
            try:
                context = json.loads(args.context)
            except json.JSONDecodeError:
                print("[CLI] Error: Invalid JSON in --context")
                sys.exit(1)

        result = execute_recipe(
            recipe_name=args.recipe,
            task=args.task,
            context=context,
        )

        if result["success"]:
            print("\n" + "=" * 70)
            print("RECIPE RESULT")
            print("=" * 70)
            print(json.dumps(result["result"], indent=2))
            print("=" * 70)
        else:
            print(f"[CLI] Failed: {result['error']}")
            sys.exit(1)

        sys.exit(0)

    # No command provided
    parser.print_help()


if __name__ == "__main__":
    main()
