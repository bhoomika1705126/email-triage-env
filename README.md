---
title: Email Triage Environment
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: true
---

# 📧 Email Triage Environment for AI Agents

## 🎯 Real-World Utility

This environment simulates a **real customer support email triage system** used by companies like Zendesk, Freshdesk, and Salesforce. AI agents learn to:

- **Prioritize urgent issues** (account lock, security alerts)
- **Respond appropriately** to customer inquiries
- **Escalate critical problems** to human agents
- **Archive low-priority emails** (newsletters, suggestions)
- **Manage queue efficiently** under time pressure

## 📊 Three Difficulty Levels

| Task | Difficulty | Description | Success Criteria |
|------|------------|-------------|------------------|
| **Easy** | 🟢 Beginner | Handle low-urgency emails (1-2) | Archive or respond correctly |
| **Medium** | 🟡 Intermediate | Handle high-urgency emails (4-5) | Escalate or mark urgent |
| **Hard** | 🔴 Advanced | Complete email queue efficiently | Correct actions + speed bonus |

## 🎮 Action Space

| Action | Description | When to Use |
|--------|-------------|-------------|
| `respond` | Send a reply | Medium urgency, requires response |
| `escalate` | Forward to human | Urgent security/account issues |
| `archive` | Close without reply | Low-priority, no action needed |
| `request_info` | Ask for details | Missing information |
| `mark_urgent` | Set priority (1-5) | Time-sensitive issues |

## 👁️ Observation Space

Each step provides:
- Email subject and body
- Sender information
- Urgency keywords detected
- Current queue size
- Last action result

## 🏆 Baseline Performance

Using Groq Llama 3.3 70B:

| Task | Score |
|------|-------|
| Easy | 0.85 |
| Medium | 0.82 |
| Hard | 0.78 |
| **Average** | **0.82** |

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/bhoomika1705126/email-triage-env
cd email-triage-env

# Install dependencies
pip install -r requirements.txt

# Run baseline inference
export API_KEY="your-key"
python inference.py

# Run with Docker
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
