#!/usr/bin/env python3
"""
Real-time Phase 3 Monitoring Dashboard

Displays:
- Live progress (X/300 instances)
- Verification rate
- Speed (instances/minute)
- Estimated time remaining
- Gamification scoreboard updates
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta

def read_progress():
    """Read current progress from progress file"""
    progress_file = Path("stillwater-swe-lite-progress.json")

    if not progress_file.exists():
        return None

    try:
        with open(progress_file) as f:
            return json.load(f)
    except:
        return None

def read_log_tail(n=50):
    """Read last N lines of log file"""
    log_file = Path("swe_phase3_run.log")

    if not log_file.exists():
        return []

    try:
        result = subprocess.run(
            ["tail", "-n", str(n), str(log_file)],
            capture_output=True,
            text=True
        )
        return result.stdout.split('\n')
    except:
        return []

def format_time(seconds):
    """Format seconds to human-readable time"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m {int(seconds%60)}s"
    else:
        h = int(seconds/3600)
        m = int((seconds % 3600)/60)
        return f"{h}h {m}m"

def get_speed(results):
    """Calculate instances processed per minute"""
    if len(results) < 2:
        return 0

    # Simple average: total instances / runtime
    # Better would be to track timestamps but this is good enough
    return len(results) / 5  # Rough estimate, 5 min into run

def main():
    """Real-time monitoring loop"""

    start_time = datetime.now()
    last_count = 0

    print("\n" + "="*80)
    print("PHASE 3 LIVE MONITORING DASHBOARD")
    print("="*80)
    print(f"Start Time: {start_time.strftime('%H:%M:%S')}")
    print(f"Model: qwen2.5-coder:7b")
    print(f"Target: 40%+ verification (120+/300 instances)")
    print("="*80 + "\n")

    iteration = 0

    while True:
        iteration += 1

        # Read progress
        progress = read_progress()

        if progress is None:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Waiting for progress file...")
            time.sleep(10)
            continue

        completed = len(progress.get('completed', []))
        results = progress.get('results', [])
        verified = sum(1 for r in results if r.get('verified', False))
        failed = completed - verified

        # Calculate metrics
        elapsed = (datetime.now() - start_time).total_seconds()
        elapsed_formatted = format_time(elapsed)

        speed = completed / (elapsed / 60) if elapsed > 0 else 0
        remaining_instances = 300 - completed
        eta_seconds = (remaining_instances / speed * 60) if speed > 0 else 999999
        eta_formatted = format_time(eta_seconds)

        # Display dashboard
        clear_lines = 30
        for _ in range(clear_lines):
            print("\033[A\033[K", end='')  # Clear line

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Phase 3 Progress")
        print("-" * 80)

        # Progress bar
        bar_length = 50
        filled = int(bar_length * completed / 300)
        bar = "█" * filled + "░" * (bar_length - filled)
        percentage = (completed / 300) * 100

        print(f"📊 Progress: [{bar}] {completed:3}/300 ({percentage:5.1f}%)")

        # Verification rate
        if completed > 0:
            verify_rate = (verified / completed) * 100
            print(f"✅ Verified: {verified:3}/{completed} ({verify_rate:5.1f}%)")
        else:
            print(f"✅ Verified: 0/0")

        # Speed
        print(f"⚡ Speed: {speed:.1f} instances/min")

        # ETA
        if speed > 0:
            print(f"⏱️  ETA: {eta_formatted} ({(datetime.now() + timedelta(seconds=eta_seconds)).strftime('%H:%M')})")
        else:
            print(f"⏱️  ETA: calculating...")

        # Elapsed
        print(f"⏰ Elapsed: {elapsed_formatted}")

        # Recent status from log
        print("\n📋 Recent Activity:")
        log_lines = read_log_tail(8)

        for line in log_lines[-5:]:
            if line.strip():
                # Show only interesting lines
                if any(x in line for x in ["Processing", "✅", "❌", "VERIFIED", "FAILED"]):
                    print(f"   {line[:75]}")

        # Estimate final result
        print("\n🎯 Projected Results:")
        if completed >= 10:
            # Extrapolate
            projected_verified = (verified / completed) * 300
            projected_rate = (verified / completed) * 100
            print(f"   If rate holds: {int(projected_verified)}/300 ({projected_rate:.1f}%)")

            if projected_rate >= 40:
                print(f"   ✅ ON TRACK for 40%+ target!")
            elif projected_rate >= 30:
                print(f"   ⚠️  Approaching target (need {40-projected_rate:.1f}pp more)")
            else:
                print(f"   ❌ Below target (need prompt refinement)")

        print("\n" + "-" * 80)
        print("Press Ctrl+C to stop monitoring")
        print("(Run will continue in background)")

        # Check if done
        if completed >= 300:
            print("\n" + "="*80)
            print("🎉 PHASE 3 COMPLETE!")
            print("="*80)
            print(f"Final Results: {verified}/300 verified ({(verified/300)*100:.1f}%)")
            break

        # Wait before next update
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Monitoring paused (background process continues)")
        print("Resume with: python3 monitor_phase3.py")
