#!/usr/bin/env python3
"""
Tests for git_show_ref.py
"""

import subprocess
import sys
from pathlib import Path


def test_output_format():
    """Test that output format matches git show-ref."""
    # Run git show-ref
    git_result = subprocess.run(
        ['git', 'show-ref'],
        capture_output=True,
        text=True
    )
    
    # Run our script
    script_result = subprocess.run(
        ['python3', 'git_show_ref.py'],
        capture_output=True,
        text=True
    )
    
    print("Git show-ref output:")
    print(git_result.stdout)
    
    print("\nPython script output:")
    print(script_result.stdout)
    
    # Parse both outputs
    git_refs = {}
    for line in git_result.stdout.strip().split('\n'):
        if line:
            parts = line.split(None, 1)
            if len(parts) == 2:
                git_refs[parts[1]] = parts[0]
    
    script_refs = {}
    for line in script_result.stdout.strip().split('\n'):
        if line:
            parts = line.split(None, 1)
            if len(parts) == 2:
                script_refs[parts[1]] = parts[0]
    
    # Compare
    if git_refs == script_refs:
        print("\n✓ Output matches git show-ref")
        return True
    else:
        print("\n✗ Output does NOT match git show-ref")
        print(f"Git refs: {git_refs}")
        print(f"Script refs: {script_refs}")
        return False


def test_error_handling():
    """Test error handling outside git repository."""
    result = subprocess.run(
        ['python3', '/home/runner/work/master/master/git_show_ref.py'],
        cwd='/tmp',
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0 and 'not a git repository' in result.stderr:
        print("✓ Error handling works correctly")
        return True
    else:
        print("✗ Error handling does NOT work correctly")
        print(f"Return code: {result.returncode}")
        print(f"Stderr: {result.stderr}")
        return False


def main():
    """Run all tests."""
    print("Running tests...\n")
    
    tests = [
        test_output_format,
        test_error_handling
    ]
    
    results = []
    for test in tests:
        print(f"\n{'='*60}")
        print(f"Running {test.__name__}...")
        print('='*60)
        results.append(test())
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
