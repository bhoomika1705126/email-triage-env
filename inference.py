#!/usr/bin/env python
"""Inference script with API calls AND 3 task graders - Scores strictly between 0 and 1"""
import json
import sys
import os
from openai import OpenAI
from tasks import run_grader

def main():
    print("[START] task=email_triage")
    
    # Get API credentials
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
    
    # Email dataset with urgency levels
    emails = [
        {"subject": "URGENT: Account locked", "urgency": 5, "body": "Cannot access account"},
        {"subject": "Question about billing cycle", "urgency": 2, "body": "When does billing reset?"},
        {"subject": "Feature suggestion: Dark mode", "urgency": 1, "body": "Add dark mode please"},
        {"subject": "Security alert: Unusual login", "urgency": 4, "body": "Unknown device login"},
        {"subject": "Refund request - double charged", "urgency": 3, "body": "Charged twice"}
    ]
    
    actions = []
    trajectory = []
    
    # Initialize OpenAI client if API key is available
    client = None
    if api_key and api_key != "dummy-key":
        try:
            client = OpenAI(base_url=api_base_url, api_key=api_key, timeout=30)
        except:
            pass
    
    # Process each email
    for i, email in enumerate(emails):
        action = "respond"  # default
        
        # Try API call if client is available
        if client:
            try:
                prompt = f"""Email: {email['subject']}
Urgency: {email['urgency']}/5

Choose action: archive, respond, escalate, request_info, mark_urgent
Reply with ONLY the action name."""
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a customer support agent. Reply with ONLY the action name."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=10
                )
                action = response.choices[0].message.content.strip().lower()
                
                # Normalize action
                if "archive" in action:
                    action = "archive"
                elif "escalate" in action:
                    action = "escalate"
                elif "respond" in action:
                    action = "respond"
                elif "request" in action:
                    action = "request_info"
                elif "urgent" in action:
                    action = "mark_urgent"
                else:
                    action = "respond"
            except Exception as e:
                # Fallback based on urgency
                if email['urgency'] >= 4:
                    action = "escalate"
                elif email['urgency'] <= 2:
                    action = "archive"
                else:
                    action = "respond"
        else:
            # No API key - smart fallback
            if email['urgency'] >= 4:
                action = "escalate"
            elif email['urgency'] <= 2:
                action = "archive"
            else:
                action = "respond"
        
        actions.append(action)
        trajectory.append({
            "step": i,
            "email": {"subject": email['subject'], "urgency": email['urgency']},
            "action": {"action_type": action}
        })
        print(f"[STEP] step={i} action={action}")
    
    # Run all 3 task graders
    easy_score = run_grader("easy", trajectory)
    medium_score = run_grader("medium", trajectory)
    hard_score = run_grader("hard", trajectory)
    average_score = (easy_score + medium_score + hard_score) / 3
    
    print(f"[TASK] easy score={easy_score:.3f}")
    print(f"[TASK] medium score={medium_score:.3f}")
    print(f"[TASK] hard score={hard_score:.3f}")
    print(f"[END] task=email_triage score={average_score:.3f} steps={len(actions)}")
    
    # Save baseline scores
    scores = {
        "easy": easy_score,
        "medium": medium_score,
        "hard": hard_score,
        "average": average_score
    }
    
    with open("baseline_scores.json", "w") as f:
        json.dump(scores, f, indent=2)
    
    sys.exit(0)

if __name__ == "__main__":
    main()