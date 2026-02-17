#!/usr/bin/env python3
"""
Diff Post-Processor: Repair malformed unified diffs

Problem: LLM generates diffs with missing/incorrect line prefixes
Solution: Parse the diff, extract intent, regenerate correct format

Auth: 65537
"""

import re
from typing import Optional, List, Dict, Tuple

class DiffPostProcessor:
    """Repair malformed unified diffs from LLM output."""

    def repair(self, malformed_diff: str, source_code: str) -> Optional[str]:
        """
        Repair a malformed diff:
        1. Extract diff intent (file, removed lines, added lines)
        2. Identify actual line numbers in source
        3. Regenerate unified diff with correct formatting

        Args:
            malformed_diff: The (possibly malformed) diff from LLM
            source_code: The original source code content

        Returns:
            Correct unified diff or None if can't repair
        """
        try:
            # Try to extract key information from the malformed diff
            file_match = re.search(r'--- a/([\w/\.\-]+)', malformed_diff)
            if not file_match:
                return None

            filepath = file_match.group(1)

            # Extract all lines that look like they're trying to be +/- lines
            removed_content = []
            added_content = []

            for line in malformed_diff.split('\n'):
                # Try to identify removed lines (start with - or just have " --" pattern)
                if line.startswith('- ') or (line.startswith('-') and len(line) > 1):
                    # Extract the actual code (skip the prefix)
                    code = line[1:] if line.startswith('-') else line[2:]
                    removed_content.append(code.rstrip())
                # Try to identify added lines
                elif line.startswith('+ ') or (line.startswith('+') and len(line) > 1 and line[1] != '+'):
                    # Extract the actual code
                    code = line[1:] if line.startswith('+') else line[2:]
                    added_content.append(code.rstrip())

            if not removed_content and not added_content:
                return None

            # Find where these lines appear in the source
            source_lines = source_code.split('\n')

            # Find the line number where the first removed line appears
            start_line = None
            for i, src_line in enumerate(source_lines):
                if removed_content and src_line.rstrip() == removed_content[0]:
                    start_line = i + 1  # 1-indexed
                    break

            if not start_line:
                # Try to find where added lines would go
                # Look for context before the expected insertion point
                return None

            # Determine line count for hunk header
            # Hunk includes: context lines + removed lines + (will have context + added lines)
            context_before = 3
            context_after = 3

            actual_start = max(1, start_line - context_before)
            actual_end = min(len(source_lines), start_line + len(removed_content) + context_after)

            # Generate correct unified diff
            return self._generate_correct_diff(
                filepath=filepath,
                source_lines=source_lines,
                start_line=actual_start,
                removed_lines=removed_content,
                added_lines=added_content,
                context_before=context_before,
                context_after=context_after
            )

        except Exception as e:
            print(f"Repair failed: {e}")
            return None

    def _generate_correct_diff(
        self,
        filepath: str,
        source_lines: List[str],
        start_line: int,
        removed_lines: List[str],
        added_lines: List[str],
        context_before: int,
        context_after: int
    ) -> str:
        """Generate a correct unified diff."""

        # Build the hunk
        hunk_lines = []

        # Find where removed lines appear
        removed_start_idx = None
        for i in range(start_line - 1, len(source_lines)):
            if source_lines[i].rstrip() == removed_lines[0]:
                removed_start_idx = i
                break

        if removed_start_idx is None:
            return None

        # Add context lines before
        context_start = max(0, removed_start_idx - context_before)
        for i in range(context_start, removed_start_idx):
            hunk_lines.append(' ' + source_lines[i])

        # Add removed lines
        for removed_line in removed_lines:
            hunk_lines.append('-' + removed_line)

        # Add added lines
        for added_line in added_lines:
            hunk_lines.append('+' + added_line)

        # Add context lines after
        context_end = min(len(source_lines), removed_start_idx + len(removed_lines) + context_after)
        for i in range(removed_start_idx + len(removed_lines), context_end):
            hunk_lines.append(' ' + source_lines[i])

        # Calculate hunk header
        old_start = context_start + 1
        old_count = (removed_start_idx - context_start) + len(removed_lines) + (context_end - removed_start_idx - len(removed_lines))
        new_start = context_start + 1
        new_count = (removed_start_idx - context_start) + len(added_lines) + (context_end - removed_start_idx - len(removed_lines))

        # Build the diff
        diff_lines = [
            f"--- a/{filepath}",
            f"+++ b/{filepath}",
            f"@@ -{old_start},{old_count} +{new_start},{new_count} @@"
        ]
        diff_lines.extend(hunk_lines)

        return '\n'.join(diff_lines)


# Test
if __name__ == "__main__":
    test_source = """def calculate(x):
    if x > 0:
        return x * 2
    else:
        return 0

def main():
    print(calculate(5))
"""

    test_diff = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 def calculate(x):
-    if x > 0:
+    if x >= 0:
     return x * 2
"""

    processor = DiffPostProcessor()
    repaired = processor.repair(test_diff, test_source)
    print("Original malformed diff:")
    print(test_diff)
    print("\nRepaired diff:")
    print(repaired)
