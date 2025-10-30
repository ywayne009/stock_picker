# How to Resume This Project with Claude Code

## 🎯 Quick Reference

When you come back to work on this project, **just say one of these to Claude:**

---

### Option 1: Let Claude Catch Up (Recommended)
```
"Read PROJECT_STATUS.md and let me know where we are"
```
Claude will read the status file and tell you what's done and what's next.

---

### Option 2: Simple Resume
```
"I'm back to work on the stock picker project"
```
Claude will check the project and ask what you want to work on.

---

### Option 3: Direct Request
```
"Continue implementing [specific feature]"
```
Jump straight into what you want to build.

---

## 📚 Key Files for Context

| File | Purpose |
|------|---------|
| **PROJECT_STATUS.md** | Current state, what's next, session log |
| **CLAUDE.md** | Development guidelines (Claude reads this automatically) |
| **CHECKPOINTS.md** | How to save/restore checkpoints |
| **GIT_WORKFLOW.md** | Git commands reference |

---

## 💾 Project Location

```bash
cd /Users/wayne/main/labs/stock_picker
```

---

## 🌐 GitHub Repository

https://github.com/ywayne009/stock_picker

---

## 🔄 Before Starting Work

```bash
# Get latest changes
git pull

# Check status
git status

# See what was done recently
git log --oneline -5
```

---

## ✅ After Finishing Work

Claude should:
1. Update PROJECT_STATUS.md with progress
2. Commit changes: `git add -A && git commit -m "Description"`
3. Push to GitHub: `git push`
4. Create checkpoint if major milestone: `git tag -a "v0.X" -m "Description" && git push --tags`

---

## 📍 Current Checkpoint

**v0.1-initial-setup** - Project structure complete, ready for development

To see all checkpoints:
```bash
git tag -l
```

---

## 🎓 Example Sessions

### Session Start
**You:** "Read PROJECT_STATUS.md and catch me up on the stock picker project"

**Claude:** "I've read the project status. Initial setup is complete with backend/frontend structure, virtual environment, and documentation all in place. The next priority is setting up database services (PostgreSQL/Redis). Have you installed Docker or would you like to set up the databases locally? What would you like to work on today?"

### During Work
**You:** "Let's implement the database models for strategies"

**Claude:** [Implements the models, tests them, commits to git]

### Session End
**You:** "That's all for today"

**Claude:** "Great work! I've updated PROJECT_STATUS.md to reflect:
- ✅ Database models implemented
- Updated session log
- Set next priority as 'Create database migrations'

Everything has been committed and pushed to GitHub. Next time just say 'Read PROJECT_STATUS.md' and I'll catch up on today's work!"

---

## 🆘 If Something Goes Wrong

### Lost Changes?
```bash
# See what changed
git status

# Undo uncommitted changes
git reset --hard HEAD

# Go back to checkpoint
git reset --hard v0.1-initial-setup
```

### Can't Remember What Was Done?
```bash
# Read the status file
cat PROJECT_STATUS.md

# See recent commits
git log --oneline -10

# See what changed in last commit
git show
```

---

## 🚀 Quick Start Commands

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm run dev
```

---

**That's it! Just tell Claude to read PROJECT_STATUS.md and you're ready to go!** 🎉
