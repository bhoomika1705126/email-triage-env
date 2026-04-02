# Email Triage Environment for AI Agents

## Description
A realistic customer support email triage environment where AI agents learn to prioritize, respond to, and manage customer emails. This simulates the daily work of customer support representatives.

## Motivation
Email triage is a common task in customer service that requires:
- Prioritizing urgent issues
- Knowing when to escalate vs respond
- Professional communication
- Efficient queue management

## Action Space
- **respond**: Send a response (requires response_text)
- **escalate**: Escalate to human agent
- **archive**: Archive low-priority email
- **request_info**: Ask customer for more information
- **mark_urgent**: Mark with priority (1-5)

## Observation Space
- email_subject: string
- email_body: string
- sender: string
- urgency_keywords: list[string]
- current_queue_size: integer
- last_action_result: string

## Tasks

### Easy (Score 0.0-1.0)
Correctly handle low-urgency emails by archiving or responding appropriately.

### Medium (Score 0.0-1.0)
Properly escalate security/financial issues and assign correct priorities.

### Hard (Score 0.0-1.0)
Complete resolution of complex issues with professional communication and efficient workflow.

## Setup Instructions

### Local Development
```bash
# Clone repo
git clone <your-repo-url>
cd email-triage-env

# Install dependencies
pip install -r requirements.txt

# Run validation
openenv validate

# Run baseline
export OPENAI_API_KEY="your-key"
python inference.py

## Baseline Scores

Using Groq's Llama 3.3 70B model:

| Task | Score |
|------|-------|
| Easy | 0.50 |
| Medium | 1.00 |
| Hard | 0.90 |
| **Average** | **0.80** |

*Baseline achieved with llama-3.3-70b-versatile via Groq API*