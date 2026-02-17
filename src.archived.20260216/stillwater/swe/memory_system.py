"""
Memory System: Persistent session state via /remember command.

Provides `/remember` command for storing and retrieving session memory across sessions.

Features:
- Persistent memory in .claude/memory/ files
- Channel-based organization (identity, goals, decisions, context, blockers)
- Git integration for history tracking
- JSON export for integration with tools

Usage:
    from stillwater.swe.memory_system import MemorySystem

    mem = MemorySystem()
    mem.remember("project_status", "Phase 3 complete")
    status = mem.recall("project_status")

Auth: 65537 | Version: 1.0.0
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import subprocess


@dataclass
class MemoryEntry:
    """Single memory entry."""
    key: str
    value: Any
    timestamp: str
    channel: int  # 2, 3, 5, 7, 11, 13 (prime numbers)
    tags: List[str]


class MemoryChannel:
    """
    Memory channels based on prime number encoding.

    Channels:
    - [2] Identity: project=stillwater, auth=65537
    - [3] Goals: oolong_target, swe_target, mission
    - [5] Decisions: locked rules, constraints, methodology
    - [7] Context: current phase, status, blockers
    - [11] Blockers: technical debt, open issues
    - [13] Haiku Swarms: agent assignments, execution plan
    """
    IDENTITY = 2
    GOALS = 3
    DECISIONS = 5
    CONTEXT = 7
    BLOCKERS = 11
    HAIKU_SWARMS = 13

    @staticmethod
    def get_name(channel: int) -> str:
        """Get name for channel number."""
        names = {
            2: "identity",
            3: "goals",
            5: "decisions",
            7: "context",
            11: "blockers",
            13: "haiku_swarms",
        }
        return names.get(channel, "unknown")

    @staticmethod
    def get_channel(name: str) -> int:
        """Get channel number for name."""
        channels = {
            "identity": 2,
            "goals": 3,
            "decisions": 5,
            "context": 7,
            "blockers": 11,
            "haiku_swarms": 13,
        }
        return channels.get(name.lower(), 7)


class MemorySystem:
    """
    Persistent memory system for Stillwater sessions.

    Stores memory in .claude/memory/ directory and tracks in git.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize memory system.

        Args:
            project_root: Root of Stillwater project (default: auto-detect)
        """
        if project_root is None:
            # Auto-detect project root
            current = Path.cwd()
            while current != current.parent:
                if (current / ".git").exists() and (current / "stillwater.toml").exists():
                    project_root = current
                    break
                current = current.parent

            if project_root is None:
                project_root = Path("/home/phuc/projects/stillwater")

        self.project_root = project_root
        self.memory_dir = project_root / ".claude" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def remember(
        self,
        key: str,
        value: Any,
        channel: int = MemoryChannel.CONTEXT,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """
        Store value in memory.

        Args:
            key: Memory key (e.g., "project_status")
            value: Value to store (str, dict, list, etc)
            channel: Channel (2-13, default: 7=context)
            tags: Optional tags for organization

        Returns:
            True if stored successfully
        """
        if tags is None:
            tags = []

        try:
            # Create entry
            entry = MemoryEntry(
                key=key,
                value=value,
                timestamp=datetime.now().isoformat(),
                channel=channel,
                tags=tags,
            )

            # Store in channel file
            channel_name = MemoryChannel.get_name(channel)
            channel_file = self.memory_dir / f"{channel_name}.json"

            # Load existing entries
            entries = {}
            if channel_file.exists():
                try:
                    entries = json.loads(channel_file.read_text())
                except:
                    entries = {}

            # Add/update entry
            entries[key] = {
                "value": value,
                "timestamp": entry.timestamp,
                "tags": tags,
            }

            # Write back
            channel_file.write_text(json.dumps(entries, indent=2))

            # Commit to git
            self._git_commit(f"memory: {channel_name}[{key}]={str(value)[:50]}")

            return True

        except Exception as e:
            print(f"ERROR: Failed to remember {key}: {e}")
            return False

    def recall(self, key: str, default: Any = None) -> Any:
        """
        Retrieve value from memory.

        Args:
            key: Memory key to recall
            default: Default value if not found

        Returns:
            Stored value or default
        """
        try:
            # Search all channels for key
            for channel_num in [2, 3, 5, 7, 11, 13]:
                channel_name = MemoryChannel.get_name(channel_num)
                channel_file = self.memory_dir / f"{channel_name}.json"

                if channel_file.exists():
                    entries = json.loads(channel_file.read_text())
                    if key in entries:
                        return entries[key].get("value", default)

            return default

        except Exception as e:
            print(f"ERROR: Failed to recall {key}: {e}")
            return default

    def list_memory(self, channel: Optional[int] = None) -> Dict[int, List[str]]:
        """
        List all stored memory entries.

        Args:
            channel: Specific channel to list (default: all)

        Returns:
            Dictionary mapping channel -> list of keys
        """
        result = {}

        channels = [channel] if channel else [2, 3, 5, 7, 11, 13]

        for ch in channels:
            channel_name = MemoryChannel.get_name(ch)
            channel_file = self.memory_dir / f"{channel_name}.json"

            if channel_file.exists():
                try:
                    entries = json.loads(channel_file.read_text())
                    result[ch] = list(entries.keys())
                except:
                    result[ch] = []

        return result

    def clear_memory(self, key: Optional[str] = None) -> bool:
        """
        Clear memory entries.

        Args:
            key: Specific key to clear (default: all)

        Returns:
            True if successful
        """
        try:
            if key is None:
                # Clear all
                for channel_num in [2, 3, 5, 7, 11, 13]:
                    channel_name = MemoryChannel.get_name(channel_num)
                    channel_file = self.memory_dir / f"{channel_name}.json"
                    if channel_file.exists():
                        channel_file.unlink()
                self._git_commit("memory: cleared all")
            else:
                # Clear specific key
                for channel_num in [2, 3, 5, 7, 11, 13]:
                    channel_name = MemoryChannel.get_name(channel_num)
                    channel_file = self.memory_dir / f"{channel_name}.json"

                    if channel_file.exists():
                        entries = json.loads(channel_file.read_text())
                        if key in entries:
                            del entries[key]
                            channel_file.write_text(json.dumps(entries, indent=2))
                            self._git_commit(f"memory: cleared {key}")
                            return True

            return True

        except Exception as e:
            print(f"ERROR: Failed to clear memory: {e}")
            return False

    def export_json(self) -> str:
        """Export all memory as JSON."""
        result = {}

        for channel_num in [2, 3, 5, 7, 11, 13]:
            channel_name = MemoryChannel.get_name(channel_num)
            channel_file = self.memory_dir / f"{channel_name}.json"

            if channel_file.exists():
                try:
                    result[channel_name] = json.loads(channel_file.read_text())
                except:
                    result[channel_name] = {}

        return json.dumps(result, indent=2)

    def _git_commit(self, message: str) -> bool:
        """Commit memory changes to git."""
        try:
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.project_root,
                check=False,
                capture_output=True,
            )

            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.project_root,
                check=False,
                capture_output=True,
            )

            return True
        except:
            return False


def run_remember_command(
    action: str,
    key: Optional[str] = None,
    value: Optional[str] = None,
    channel: Optional[str] = None,
) -> str:
    """
    Run /remember command.

    Usage:
    - `/remember list` - List all memory
    - `/remember get key` - Get specific value
    - `/remember set key value` - Set value
    - `/remember clear` - Clear all memory

    Args:
        action: list, get, set, clear
        key: Memory key
        value: Value to set
        channel: Memory channel (identity, goals, decisions, context, blockers, haiku_swarms)

    Returns:
        Status message
    """
    mem = MemorySystem()

    if action == "list":
        result = mem.list_memory()
        lines = ["📚 Stored Memory:"]
        for ch, keys in result.items():
            ch_name = MemoryChannel.get_name(ch)
            lines.append(f"\n  [{ch}] {ch_name}: {', '.join(keys) if keys else '(empty)'}")
        return "\n".join(lines)

    elif action == "get":
        if not key:
            return "ERROR: Specify key to get"
        value = mem.recall(key)
        return f"✅ {key} = {value}" if value else f"❌ {key} not found"

    elif action == "set":
        if not key or value is None:
            return "ERROR: Specify key and value"
        ch = MemoryChannel.get_channel(channel or "context")
        success = mem.remember(key, value, channel=ch)
        return f"✅ Remembered: {key} = {value}" if success else "❌ Failed to remember"

    elif action == "clear":
        success = mem.clear_memory(key)
        msg = f"Cleared {key}" if key else "Cleared all memory"
        return f"✅ {msg}" if success else "❌ Failed to clear"

    elif action == "export":
        return mem.export_json()

    else:
        return f"ERROR: Unknown action '{action}'. Use: list, get, set, clear, export"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Memory System")
    parser.add_argument("action", choices=["list", "get", "set", "clear", "export"])
    parser.add_argument("--key", help="Memory key")
    parser.add_argument("--value", help="Memory value")
    parser.add_argument("--channel", help="Memory channel")

    args = parser.parse_args()

    result = run_remember_command(
        args.action, key=args.key, value=args.value, channel=args.channel
    )
    print(result)
