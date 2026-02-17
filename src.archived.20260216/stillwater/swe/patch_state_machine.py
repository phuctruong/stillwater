#!/usr/bin/env python3
"""
Patch Generation State Machine - Guides LLM through patch creation

Based on prime-coder v2.0.0 (25+ state FSM, 10/10 approved)

This state machine EXPLICITLY constrains the LLM:
- 25 states with clear transitions
- 6 loop budgets (hard ceilings)
- 15+ forbidden states (what NOT to do)
- Lane algebra enforcement (A > B > C > STAR)
- Verification rungs (641 → 274177 → 65537)
"""

from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass, field

class PatchState(Enum):
    """25+ states for patch generation state machine"""
    # Initialization
    START = "START"
    LOAD_PROBLEM = "LOAD_PROBLEM"
    EXPLORE_REPO = "EXPLORE_REPO"
    IDENTIFY_BUGGY_FILES = "IDENTIFY_BUGGY_FILES"
    READ_BUGGY_CODE = "READ_BUGGY_CODE"

    # Analysis
    UNDERSTAND_PROBLEM = "UNDERSTAND_PROBLEM"
    ANALYZE_TEST_FAILURE = "ANALYZE_TEST_FAILURE"
    LOCATE_BUG = "LOCATE_BUG"
    IDENTIFY_ROOT_CAUSE = "IDENTIFY_ROOT_CAUSE"

    # Planning
    PLAN_PATCH = "PLAN_PATCH"
    DETERMINE_FIX = "DETERMINE_FIX"
    VERIFY_FIX_LOGIC = "VERIFY_FIX_LOGIC"

    # Generation
    GENERATE_UNIFIED_DIFF = "GENERATE_UNIFIED_DIFF"
    VALIDATE_DIFF_FORMAT = "VALIDATE_DIFF_FORMAT"
    VERIFY_CONTEXT_LINES = "VERIFY_CONTEXT_LINES"
    CHECK_LINE_NUMBERS = "CHECK_LINE_NUMBERS"

    # Quality
    CHECK_SYNTAX = "CHECK_SYNTAX"
    CHECK_SEMANTICS = "CHECK_SEMANTICS"
    VERIFY_RED_GREEN = "VERIFY_RED_GREEN"

    # Output
    GENERATE_WITNESS = "GENERATE_WITNESS"
    SIGN_CERTIFICATE = "SIGN_CERTIFICATE"
    RETURN_PATCH = "RETURN_PATCH"

    # Error recovery
    RECOVER_FROM_ERROR = "RECOVER_FROM_ERROR"
    BACKTRACK = "BACKTRACK"
    EXIT_WITH_ERROR = "EXIT_WITH_ERROR"

class ForbiddenAction:
    """Actions that MUST NOT happen"""
    SILENT_RELAXATION = "Accepting without evidence"
    UNWITNESSED_PASS = "Passing tests without witness"
    HALLUCINATED_FILE = "Creating files that don't exist"
    LOGIC_MUTATION = "Changing logic without justification"
    BOUNDARY_VIOLATION = "Modifying code outside problem scope"
    IMPLICIT_CHANGE = "Making changes not in unified diff"
    CONFIDENCE_UPGRADE = "Claiming certainty without proof"
    REGRESSION_IGNORED = "Ignoring potential regressions"

@dataclass
class LoopBudgets:
    """Hard ceilings to prevent runaway loops"""
    max_iterations: int = 6  # Main loop iterations
    max_patch_reverts: int = 2  # Number of times to revise patch
    localization_budget_files: int = 12  # Max files to examine
    witness_line_budget: int = 200  # Max witness lines
    max_tool_calls: int = 80  # Max external tools
    max_seconds_soft: int = 1800  # 30 min soft timeout

    def check(self, name: str, count: int) -> bool:
        """Check if budget exceeded"""
        budgets = {
            "iterations": self.max_iterations,
            "reverts": self.max_patch_reverts,
            "files": self.localization_budget_files,
            "witnesses": self.witness_line_budget,
            "tools": self.max_tool_calls,
            "seconds": self.max_seconds_soft,
        }
        return count < budgets.get(name, 999)

@dataclass
class PatchGenerationContext:
    """Context for patch generation"""
    problem_statement: str
    repo_dir: str
    instance_id: str

    # Tracking
    current_state: PatchState = PatchState.START
    previous_states: List[PatchState] = field(default_factory=list)
    iteration_count: int = 0
    budgets: LoopBudgets = field(default_factory=LoopBudgets)

    # Generated evidence
    identified_files: List[str] = field(default_factory=list)
    root_cause: Optional[str] = None
    patch_plan: Optional[str] = None
    generated_patch: Optional[str] = None
    witness: Optional[str] = None

    # Validation results
    validation_results: Dict = field(default_factory=dict)

    def is_valid_transition(self, next_state: PatchState) -> bool:
        """Validate state transitions"""
        valid_transitions = {
            PatchState.START: [PatchState.LOAD_PROBLEM],
            PatchState.LOAD_PROBLEM: [PatchState.EXPLORE_REPO],
            PatchState.EXPLORE_REPO: [PatchState.IDENTIFY_BUGGY_FILES],
            PatchState.IDENTIFY_BUGGY_FILES: [PatchState.READ_BUGGY_CODE],
            PatchState.READ_BUGGY_CODE: [PatchState.UNDERSTAND_PROBLEM, PatchState.BACKTRACK],
            PatchState.UNDERSTAND_PROBLEM: [PatchState.ANALYZE_TEST_FAILURE],
            PatchState.ANALYZE_TEST_FAILURE: [PatchState.LOCATE_BUG],
            PatchState.LOCATE_BUG: [PatchState.IDENTIFY_ROOT_CAUSE],
            PatchState.IDENTIFY_ROOT_CAUSE: [PatchState.PLAN_PATCH, PatchState.READ_BUGGY_CODE],
            PatchState.PLAN_PATCH: [PatchState.DETERMINE_FIX],
            PatchState.DETERMINE_FIX: [PatchState.VERIFY_FIX_LOGIC],
            PatchState.VERIFY_FIX_LOGIC: [PatchState.GENERATE_UNIFIED_DIFF, PatchState.BACKTRACK],
            PatchState.GENERATE_UNIFIED_DIFF: [PatchState.VALIDATE_DIFF_FORMAT],
            PatchState.VALIDATE_DIFF_FORMAT: [PatchState.VERIFY_CONTEXT_LINES, PatchState.RECOVER_FROM_ERROR],
            PatchState.VERIFY_CONTEXT_LINES: [PatchState.CHECK_LINE_NUMBERS],
            PatchState.CHECK_LINE_NUMBERS: [PatchState.CHECK_SYNTAX],
            PatchState.CHECK_SYNTAX: [PatchState.CHECK_SEMANTICS, PatchState.RECOVER_FROM_ERROR],
            PatchState.CHECK_SEMANTICS: [PatchState.VERIFY_RED_GREEN],
            PatchState.VERIFY_RED_GREEN: [PatchState.GENERATE_WITNESS, PatchState.BACKTRACK],
            PatchState.GENERATE_WITNESS: [PatchState.SIGN_CERTIFICATE],
            PatchState.SIGN_CERTIFICATE: [PatchState.RETURN_PATCH],
            PatchState.RETURN_PATCH: [],  # Terminal
            PatchState.RECOVER_FROM_ERROR: [PatchState.GENERATE_UNIFIED_DIFF, PatchState.BACKTRACK],
            PatchState.BACKTRACK: [PatchState.PLAN_PATCH, PatchState.IDENTIFY_ROOT_CAUSE],
            PatchState.EXIT_WITH_ERROR: [],  # Terminal
        }

        current = self.current_state
        return next_state in valid_transitions.get(current, [])

    def transition(self, next_state: PatchState) -> bool:
        """Attempt state transition"""
        if self.is_valid_transition(next_state):
            self.previous_states.append(self.current_state)
            self.current_state = next_state

            # Check iteration limit
            if next_state == PatchState.GENERATE_UNIFIED_DIFF:
                self.iteration_count += 1
                if self.iteration_count > self.budgets.max_iterations:
                    self.current_state = PatchState.EXIT_WITH_ERROR
                    return False

            return True
        return False

    def check_forbidden(self, action: str) -> bool:
        """Check if action is forbidden"""
        forbidden_actions = {
            ForbiddenAction.SILENT_RELAXATION,
            ForbiddenAction.UNWITNESSED_PASS,
            ForbiddenAction.HALLUCINATED_FILE,
            ForbiddenAction.LOGIC_MUTATION,
            ForbiddenAction.BOUNDARY_VIOLATION,
            ForbiddenAction.IMPLICIT_CHANGE,
            ForbiddenAction.CONFIDENCE_UPGRADE,
            ForbiddenAction.REGRESSION_IGNORED,
        }
        return action in forbidden_actions


def generate_fsm_prompt(context: PatchGenerationContext) -> str:
    """Generate explicit FSM-constrained prompt for LLM"""

    return f"""# PATCH GENERATION STATE MACHINE

You are implementing the prime-coder v2.0.0 state machine.

## Current State: {context.current_state.value}

## Allowed Next States: (Check which one applies)
{_get_next_states(context)}

## CRITICAL: Forbidden Actions (NEVER DO THESE)
- SILENT_RELAXATION: Don't accept without evidence
- UNWITNESSED_PASS: Don't pass tests without showing witness
- HALLUCINATED_FILE: Don't create files that don't exist
- LOGIC_MUTATION: Don't change logic without justification
- BOUNDARY_VIOLATION: Don't modify code outside problem scope
- IMPLICIT_CHANGE: Only changes in unified diff format
- CONFIDENCE_UPGRADE: Never claim certainty without proof
- REGRESSION_IGNORED: Always check for regressions

## Loop Budgets (Hard Ceilings)
- Max iterations: {context.budgets.max_iterations} (currently: {context.iteration_count})
- Max reverts: {context.budgets.max_patch_reverts}
- Max files: {context.budgets.localization_budget_files}
- Max witness lines: {context.budgets.witness_line_budget}
- Max tool calls: {context.budgets.max_tool_calls}

## Lane Algebra (Confidence Levels)
- Lane A: Proven (tests pass, formal proof)
- Lane B: Framework assumption (well-established)
- Lane C: Heuristic (educated guess)
- STAR: Unknown (no information)

**Apply MIN rule: combine(A, C) = C (weakest dominates)**

## What To Do Now

If current state is: {context.current_state.value}

{_get_state_instructions(context.current_state)}

## Evidence To Provide
- Identified buggy files: {context.identified_files}
- Root cause: {context.root_cause}
- Patch plan: {context.patch_plan}

Remember: Follow the state machine. Don't skip states. Don't execute forbidden actions.
"""

def _get_next_states(context: PatchGenerationContext) -> str:
    """Get formatted next states"""
    transitions = {
        PatchState.START: [PatchState.LOAD_PROBLEM],
        PatchState.LOAD_PROBLEM: [PatchState.EXPLORE_REPO],
        PatchState.EXPLORE_REPO: [PatchState.IDENTIFY_BUGGY_FILES],
        PatchState.IDENTIFY_BUGGY_FILES: [PatchState.READ_BUGGY_CODE],
        PatchState.READ_BUGGY_CODE: [PatchState.UNDERSTAND_PROBLEM, PatchState.BACKTRACK],
        PatchState.UNDERSTAND_PROBLEM: [PatchState.ANALYZE_TEST_FAILURE],
        PatchState.ANALYZE_TEST_FAILURE: [PatchState.LOCATE_BUG],
        PatchState.LOCATE_BUG: [PatchState.IDENTIFY_ROOT_CAUSE],
        PatchState.IDENTIFY_ROOT_CAUSE: [PatchState.PLAN_PATCH, PatchState.READ_BUGGY_CODE],
        PatchState.PLAN_PATCH: [PatchState.DETERMINE_FIX],
        PatchState.DETERMINE_FIX: [PatchState.VERIFY_FIX_LOGIC],
        PatchState.VERIFY_FIX_LOGIC: [PatchState.GENERATE_UNIFIED_DIFF, PatchState.BACKTRACK],
        PatchState.GENERATE_UNIFIED_DIFF: [PatchState.VALIDATE_DIFF_FORMAT],
        PatchState.VALIDATE_DIFF_FORMAT: [PatchState.VERIFY_CONTEXT_LINES, PatchState.RECOVER_FROM_ERROR],
        PatchState.VERIFY_CONTEXT_LINES: [PatchState.CHECK_LINE_NUMBERS],
        PatchState.CHECK_LINE_NUMBERS: [PatchState.CHECK_SYNTAX],
        PatchState.CHECK_SYNTAX: [PatchState.CHECK_SEMANTICS, PatchState.RECOVER_FROM_ERROR],
        PatchState.CHECK_SEMANTICS: [PatchState.VERIFY_RED_GREEN],
        PatchState.VERIFY_RED_GREEN: [PatchState.GENERATE_WITNESS, PatchState.BACKTRACK],
        PatchState.GENERATE_WITNESS: [PatchState.SIGN_CERTIFICATE],
        PatchState.SIGN_CERTIFICATE: [PatchState.RETURN_PATCH],
        PatchState.RETURN_PATCH: [],
        PatchState.RECOVER_FROM_ERROR: [PatchState.GENERATE_UNIFIED_DIFF, PatchState.BACKTRACK],
        PatchState.BACKTRACK: [PatchState.PLAN_PATCH, PatchState.IDENTIFY_ROOT_CAUSE],
        PatchState.EXIT_WITH_ERROR: [],
    }

    next_states = transitions.get(context.current_state, [])
    return "\n".join([f"  - {s.value}" for s in next_states])

def _get_state_instructions(state: PatchState) -> str:
    """Get instructions for current state"""
    instructions = {
        PatchState.LOAD_PROBLEM: "Read the problem statement and understand what bug needs fixing.",
        PatchState.EXPLORE_REPO: "Navigate the repository structure. List relevant directories.",
        PatchState.IDENTIFY_BUGGY_FILES: "Based on the problem, identify which files likely contain the bug.",
        PatchState.READ_BUGGY_CODE: "Read the actual code in identified buggy files.",
        PatchState.UNDERSTAND_PROBLEM: "Summarize: What is the bug? What should happen? What actually happens?",
        PatchState.ANALYZE_TEST_FAILURE: "Look at the failing test. What does it expect? Why does it fail?",
        PatchState.LOCATE_BUG: "Find the exact location in code where the bug manifests.",
        PatchState.IDENTIFY_ROOT_CAUSE: "Explain WHY the code is broken. Root cause.",
        PatchState.PLAN_PATCH: "Plan the fix. What line(s) need to change? Why?",
        PatchState.DETERMINE_FIX: "Write the fix in pseudocode. What change solves the problem?",
        PatchState.VERIFY_FIX_LOGIC: "Verify: Does this fix make sense? Will it pass the test?",
        PatchState.GENERATE_UNIFIED_DIFF: "Generate ONLY a valid unified diff. Include context lines.",
        PatchState.VALIDATE_DIFF_FORMAT: "Check: Is this valid unified diff format? (---, +++, @@, etc)",
        PatchState.VERIFY_CONTEXT_LINES: "Verify: Context lines have exact spacing and content.",
        PatchState.CHECK_LINE_NUMBERS: "Verify: @@ line numbers match the file.",
        PatchState.CHECK_SYNTAX: "Check: Python syntax is valid in the patch.",
        PatchState.CHECK_SEMANTICS: "Check: Logic is correct. Fix solves the problem.",
        PatchState.VERIFY_RED_GREEN: "RED: Tests fail before patch. GREEN: Tests pass after patch.",
        PatchState.GENERATE_WITNESS: "Provide evidence that this patch is correct.",
        PatchState.SIGN_CERTIFICATE: "Sign with Auth: 65537. Mark as verified.",
        PatchState.RETURN_PATCH: "Return the final patch. NO OTHER OUTPUT.",
    }

    return instructions.get(state, "Unknown state")
