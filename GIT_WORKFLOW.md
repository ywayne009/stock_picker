# Git Workflow Guide

Quick reference for working with this project's Git repository.

## Daily Workflow

### Starting Your Work Session
```bash
cd /Users/wayne/main/labs/stock_picker

# Get latest changes from GitHub
git pull

# Check current status
git status
```

### While Working
```bash
# See what you changed
git status

# See detailed changes
git diff

# See changes in a specific file
git diff backend/app/main.py
```

### Saving Your Work

#### Quick Save (Commit Locally)
```bash
# Stage all changes
git add -A

# Commit with message
git commit -m "Describe what you did"
```

#### Push to GitHub
```bash
# Push your commits to GitHub
git push
```

#### Create a Checkpoint
```bash
# Commit and tag
git add -A
git commit -m "Completed feature X"
git tag -a "v0.2-feature-name" -m "Description"

# Push commits and tags
git push
git push --tags
```

## Common Tasks

### Undo Changes

**Undo uncommitted changes (in working directory):**
```bash
# Undo changes to a specific file
git checkout -- backend/app/main.py

# Undo ALL uncommitted changes
git reset --hard HEAD
```

**Undo last commit (keep changes):**
```bash
git reset --soft HEAD~1
```

**Undo last commit (discard changes):**
```bash
git reset --hard HEAD~1
```

### View History

```bash
# View commit log
git log --oneline

# View with graph
git log --oneline --graph --decorate --all

# See what changed in a commit
git show <commit-hash>
```

### Branches

**Create and switch to a new branch:**
```bash
git checkout -b feature-name
```

**Switch between branches:**
```bash
git checkout main
git checkout feature-name
```

**Merge branch into main:**
```bash
git checkout main
git merge feature-name
```

**Delete branch:**
```bash
git branch -d feature-name  # Safe delete
git branch -D feature-name  # Force delete
```

### Working with GitHub

**Clone on another computer:**
```bash
git clone git@github.com:ywayne009/stock_picker.git
cd stock_picker
```

**Pull latest changes:**
```bash
git pull
```

**Push your changes:**
```bash
git push
```

**View remote info:**
```bash
git remote -v
```

## Example Workflows

### Scenario 1: Quick Fix
```bash
# Make your changes
# ...

# Quick commit and push
git add -A
git commit -m "Fix: corrected database connection issue"
git push
```

### Scenario 2: Experiment Safely
```bash
# Create experimental branch
git checkout -b experiment-new-feature

# Make changes, test
# ...

# If it works:
git checkout main
git merge experiment-new-feature
git push

# If it doesn't work:
git checkout main
git branch -D experiment-new-feature
```

### Scenario 3: Major Feature with Checkpoint
```bash
# Work on feature
# Make multiple commits as you go
git add -A
git commit -m "Part 1: Setup database models"

git add -A
git commit -m "Part 2: Add API endpoints"

git add -A
git commit -m "Part 3: Add tests"

# When complete, create checkpoint
git tag -a "v0.2-user-authentication" -m "Completed user authentication system"

# Push everything
git push
git push --tags
```

### Scenario 4: Oh No, I Broke Everything!
```bash
# Option 1: Undo all uncommitted changes
git reset --hard HEAD

# Option 2: Go back to last checkpoint
git reset --hard v0.1-initial-setup

# Option 3: See what you did recently
git log --oneline -10
git reset --hard <commit-hash>
```

## Git Status Meanings

```bash
git status
```

**Output meanings:**
- `modified:` - File changed but not staged
- `new file:` - File added but not staged
- `deleted:` - File deleted but not staged
- `Changes to be committed:` - Staged, ready to commit
- `Untracked files:` - New files Git doesn't track yet

## Useful Aliases (Optional)

Add these to `~/.gitconfig` for shortcuts:

```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --decorate --all
```

Then use: `git st`, `git co main`, etc.

## Tips

✅ **Commit Often** - Small, frequent commits are better than large ones

✅ **Meaningful Messages** - Use descriptive commit messages
   - Good: "Add user authentication endpoint"
   - Bad: "changes" or "fix stuff"

✅ **Pull Before Push** - Always `git pull` before `git push` to avoid conflicts

✅ **Use Branches** - For experimental features, use branches instead of working on main

✅ **Checkpoint Major Milestones** - Tag important versions

✅ **Review Before Commit** - Use `git diff` to review your changes before committing

## Get Help

```bash
# Help for any command
git help <command>
git help commit
git help push

# Quick help
git <command> --help
```

## Quick Reference Card

```bash
# Essential Commands
git status              # See what changed
git add -A              # Stage all changes
git commit -m "msg"     # Commit with message
git push                # Push to GitHub
git pull                # Get updates from GitHub

# Safety
git diff                # See changes before committing
git log --oneline       # See history
git reset --hard HEAD   # Undo all uncommitted changes

# Checkpoints
git tag -l              # List checkpoints
git tag -a "v0.X" -m "" # Create checkpoint
git checkout v0.X       # Go to checkpoint
git checkout main       # Return to latest
```

---

**Repository:** https://github.com/ywayne009/stock_picker

For checkpoint management, see [CHECKPOINTS.md](./CHECKPOINTS.md)
