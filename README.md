---
Title: Email Triage Environment
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Email Triage Environment for AI Agents

A realistic customer support email triage environment where AI agents learn to prioritize, respond to, and manage customer emails.

## API Endpoints

- `GET /health` - Health check
- `GET /reset` - Reset environment
- `POST /step` - Take an action (requires JSON body)
- `GET /state` - Get current state

## Baseline Scores (Groq Llama 3.3 70B)

| Task | Score |
|------|-------|
| Easy | 0.50 |
| Medium | 1.00 |
| Hard | 0.90 |
| **Average** | **0.80** |

## Example Usage

```bash
# Health check
curl https://bhoomika1265905-email-triage-env.hf.space/health

# Reset environment
curl https://bhoomika1265905-email-triage-env.hf.space/reset

# Take an action
curl -X POST https://bhoomika1265905-email-triage-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"action_type": "archive"}}'


## Step 2: Commit and Push the Updated README

```powershell
# Add the updated README
git add README.md

# Commit
git commit -m "Add HF Space metadata to README"

# Push to HF Space
git push space master
