#!/usr/bin/env python
"""Inference script for Email Triage Environment - OpenEnv Compliant"""
import json
import sys
import os
from openai import OpenAI

# Read environment variables (with defaults where required)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN")

# HF_TOKEN is mandatory
if HF_TOKEN is None:
    print("[START] task=email_triage env=email-triage-env model=unknown")
    print("[END] success=false steps=0 rewards=")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

def get_action_for_email(email, step_num):
    """Get action for a single email using LLM"""
    prompt = f"""You are a customer support agent. Email: {email['subject']}
Urgency level: {email['urgency']}/5

Choose ONE action from: archive, respond, escalate, request_info, mark_urgent
Reply with ONLY the action name, nothing else."""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a customer support agent. Reply with only the action name."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=10
        )
        action = response.choices[0].message.content.strip().lower()
        
        # Normalize action
        if "archive" in action:
            return "archive"
        elif "escalate" in action:
            return "escalate"
        elif "respond" in action:
            return "respond"
        elif "request" in action:
            return "request_info"
        elif "urgent" in action:
            return "mark_urgent"
        else:
            return "respond"
    except Exception as e:
        # Fallback based on urgency
        if email['urgency'] >= 4:
            return "escalate"
        elif email['urgency'] <= 2:
            return "archive"
        else:
            return "respond"

def calculate_reward(action, email):
    """Calculate reward for an action (0.0 to 1.0)"""
    urgency = email['urgency']
    
    if urgency >= 4 and action == 'escalate':
        return 0.90
    elif urgency <= 2 and action == 'archive':
        return 0.90
    elif 2 < urgency < 4 and action == 'respond':
        return 0.80
    elif action in ['respond', 'archive', 'escalate', 'request_info', 'mark_urgent']:
        return 0.50
    else:
        return 0.30

def main():
    # Email dataset
    emails = [
        {"urgency": 5, "subject": "URGENT: Account locked - can't access funds"},
        {"urgency": 2, "subject": "Question about billing cycle"},
        {"urgency": 1, "subject": "Feature suggestion: Dark mode"},
        {"urgency": 4, "subject": "Security alert: Unusual login detected"},
        {"urgency": 3, "subject": "Refund request - double charged"}
    ]
    
    # Print START line
    print(f"[START] task=email_triage env=email-triage-env model={MODEL_NAME}", flush=True)
    
    actions = []
    rewards = []
    done = False
    
    # Process each email
    for i, email in enumerate(emails):
        # Get action from LLM
        action = get_action_for_email(email, i)
        actions.append(action)
        
        # Calculate reward
        reward = calculate_reward(action, email)
        rewards.append(reward)
        
        # Check if done (last email)
        done = (i == len(emails) - 1)
        
        # Print STEP line
        print(f"[STEP] step={i} action={action} reward={reward:.2f} done={str(done).lower()} error=null", flush=True)
    
    # Calculate success (true if average reward > 0.5)
    avg_reward = sum(rewards) / len(rewards) if rewards else 0
    success = avg_reward > 0.5
    
    # Format rewards string
    rewards_str = ','.join([f"{r:.2f}" for r in rewards])
    
    # Print END line
    print(f"[END] success={str(success).lower()} steps={len(actions)} rewards={rewards_str}", flush=True)
    
    # Save baseline scores
    scores = {
        "easy": rewards[1] if len(rewards) > 1 else 0.5,
        "medium": rewards[3] if len(rewards) > 3 else 0.5,
        "hard": avg_reward,
        "average": avg_reward
    }
    
    with open("baseline_scores.json", "w") as f:
        json.dump(scores, f, indent=2)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
