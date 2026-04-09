#!/usr/bin/env python
import json
import sys
import os
from openai import OpenAI

# Import grader
from tasks import run_grader

def main():
    # IMPORTANT: Must print with flush=True
    print("[START] task=email_triage", flush=True)
    
    # Get API credentials
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
    
    # Email dataset
    emails = [
        {"urgency": 5, "subject": "Account locked"},
        {"urgency": 2, "subject": "Billing question"},
        {"urgency": 1, "subject": "Feature suggestion"},
        {"urgency": 4, "subject": "Security alert"},
        {"urgency": 3, "subject": "Refund request"}
    ]
    
    actions = []
    trajectory = []
    
    # Initialize client
    client = None
    if api_key and api_key != "dummy-key":
        try:
            client = OpenAI(base_url=api_base_url, api_key=api_key, timeout=30)
        except:
            pass
    
    # Process emails
    for i, email in enumerate(emails):
        action = "respond"
        
        if client:
            try:
                prompt = f"Urgency {email['urgency']}/5. Choose: archive, respond, escalate"
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=10
                )
                action = response.choices[0].message.content.strip().lower()
                if "archive" in action:
                    action = "archive"
                elif "escalate" in action:
                    action = "escalate"
                else:
                    action = "respond"
            except:
                if email['urgency'] >= 4:
                    action = "escalate"
                elif email['urgency'] <= 2:
                    action = "archive"
                else:
                    action = "respond"
        else:
            if email['urgency'] >= 4:
                action = "escalate"
            elif email['urgency'] <= 2:
                action = "archive"
            else:
                action = "respond"
        
        actions.append(action)
        trajectory.append({
            "step": i,
            "email": {"urgency": email['urgency']},
            "action": {"action_type": action}
        })
        
        # IMPORTANT: Must print STEP with exact format
        print(f"[STEP] step={i} action={action}", flush=True)
    
    # Run all 3 graders
    easy_score = run_grader("easy", trajectory)
    medium_score = run_grader("medium", trajectory)
    hard_score = run_grader("hard", trajectory)
    avg_score = (easy_score + medium_score + hard_score) / 3
    
    # IMPORTANT: Must print TASK scores
    print(f"[TASK] easy score={easy_score:.3f}", flush=True)
    print(f"[TASK] medium score={medium_score:.3f}", flush=True)
    print(f"[TASK] hard score={hard_score:.3f}", flush=True)
    
    # IMPORTANT: Must print END with exact format
    print(f"[END] task=email_triage score={avg_score:.3f} steps={len(actions)}", flush=True)
    
    # Save scores
    with open("baseline_scores.json", "w") as f:
        json.dump({
            "easy": easy_score,
            "medium": medium_score,
            "hard": hard_score,
            "average": avg_score
        }, f, indent=2)
    
    sys.exit(0)

if __name__ == "__main__":
    main()