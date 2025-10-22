# master
Copia (Copy/Mirror Repository)

This repository provides tools and instructions for creating a mirror clone of the SPAYTK/master repository.

## What is a Mirror Clone?

A mirror clone (`git clone --mirror`) creates a bare repository that is an exact copy of the source repository, including all refs, remote-tracking branches, and notes. This is useful for creating backups or migrating repositories.

## Quick Start

### Using the Script

Run the provided script to automatically clone the mirror:

```bash
./clone_mirror.sh
```

### Manual Clone

To manually create a mirror clone, run these commands:

```bash
git clone --mirror https://github.com/SPAYTK/master.git
cd master.git
```

## What Gets Cloned?

A mirror clone includes:
- All branches
- All tags
- All refs
- All remote-tracking information
- Complete commit history

## Pushing the Mirror to Another Remote

To push this mirror to a different remote repository:

```bash
cd master.git
git push --mirror <your-remote-url>
```

## Notes

- A mirror clone creates a **bare repository** (no working directory)
- The cloned directory will be named `master.git` by default
- This is different from a regular clone, which only gets the default branch and creates a working directory
