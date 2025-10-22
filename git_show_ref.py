#!/usr/bin/env python3
"""
A Python implementation of git show-ref command.
Displays Git references (branches and tags) with their commit SHAs.
"""

import os
import sys
from pathlib import Path


def find_git_dir():
    """Find the .git directory starting from the current directory."""
    current = Path.cwd()
    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.exists() and git_dir.is_dir():
            return git_dir
        current = current.parent
    return None


def read_ref(ref_path):
    """Read a reference file and return the commit SHA."""
    try:
        with open(ref_path, 'r') as f:
            content = f.read().strip()
            # Handle symbolic refs
            if content.startswith('ref: '):
                ref_target = content[5:]  # Remove 'ref: ' prefix
                git_dir = find_git_dir()
                if git_dir:
                    target_path = git_dir / ref_target
                    if target_path.exists():
                        return read_ref(target_path)
            return content
    except Exception:
        return None


def read_packed_refs(git_dir):
    """Read references from packed-refs file."""
    packed_refs = []
    packed_refs_file = git_dir / "packed-refs"
    
    if not packed_refs_file.exists():
        return packed_refs
    
    try:
        with open(packed_refs_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Skip peeled refs (lines starting with ^)
                if line.startswith('^'):
                    continue
                
                parts = line.split(None, 1)
                if len(parts) == 2:
                    sha, ref_name = parts
                    packed_refs.append((sha, ref_name))
    except Exception:
        pass
    
    return packed_refs


def list_refs(git_dir):
    """List all references in the repository."""
    refs = []
    refs_dict = {}
    
    # First, read packed refs
    for sha, ref_name in read_packed_refs(git_dir):
        refs_dict[ref_name] = sha
    
    # Then read loose refs (these override packed refs)
    refs_dir = git_dir / "refs"
    if refs_dir.exists():
        for root, dirs, files in os.walk(refs_dir):
            for file in files:
                ref_file = Path(root) / file
                # Calculate relative path from git_dir
                relative_path = ref_file.relative_to(git_dir)
                ref_name = str(relative_path)
                
                sha = read_ref(ref_file)
                if sha:
                    refs_dict[ref_name] = sha
    
    # Convert dict to list of tuples
    refs = [(sha, ref_name) for ref_name, sha in refs_dict.items()]
    
    return refs


def show_refs():
    """Main function to display all Git references."""
    git_dir = find_git_dir()
    
    if not git_dir:
        print("fatal: not a git repository (or any of the parent directories): .git", 
              file=sys.stderr)
        return 1
    
    refs = list_refs(git_dir)
    
    # Sort refs by name for consistent output
    refs.sort(key=lambda x: x[1])
    
    # Print refs in format: SHA ref_name
    for sha, ref_name in refs:
        print(f"{sha} {ref_name}")
    
    return 0


if __name__ == "__main__":
    sys.exit(show_refs())
