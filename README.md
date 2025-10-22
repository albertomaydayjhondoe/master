# master

## Git Show-Ref Python Implementation

This repository contains a Python implementation of the `git show-ref` command.

### Usage

Run the script from within a Git repository:

```bash
python3 git_show_ref.py
```

Or make it executable and run directly:

```bash
chmod +x git_show_ref.py
./git_show_ref.py
```

### Features

- Lists all Git references (branches, tags, and remote branches)
- Reads both loose refs from `.git/refs/` and packed refs from `.git/packed-refs`
- Outputs in the same format as `git show-ref`: `<SHA> <ref-name>`
- Handles symbolic references
- Proper error handling when not in a Git repository

### Example Output

```
6550a886769583dcde77da0f62b0b22c4f5a6186 refs/heads/main
6550a886769583dcde77da0f62b0b22c4f5a6186 refs/remotes/origin/main
abc1234567890def1234567890abcdef12345678 refs/tags/v1.0.0
```
