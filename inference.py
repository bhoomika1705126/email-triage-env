#!/usr/bin/env python
"""Complete inference script for Email Triage Environment - Phase 2 Compliant"""
import json
import sys
import os
from openai import OpenAI


def create_trajectory(actions, emails):
    """Create trajectory dict from actions and emails"""
    trajectory = []
    for i, (email, action) in enumerate(zip(emails, actions)):
        trajectory.append({
            'step': i,
            'email': {
                'subject': email['subject'],
                'true_urgency': email['urgency']
            },
            'action': {
                'action_type': action,
                'response_text': None,
                'priority': None
            }
        })
    return trajectory


def main():
    print("[START] task=email_triage")
    
    # Get API credentials from environment
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
    
    if not api_key:
        print("[ERROR] No API_KEY found in environment variables")
        print("[END] task=email_triage score=0.0 steps=0")
        sys.exit(1)
    
    # Initialize OpenAI client
    try:
        client = OpenAI(base_url=api_base_url, api_key=api_key, timeout=30)
    except Exception as e:
        print(f"[ERROR] Failed to create client: {e}")
        print("[END] task=email_triage score=0.0 steps=0")
        sys.exit(1)
    
    # Email dataset
    emails = [
        {"subject": "URGENT: Account locked - can't access funds", "urgency": 5, "body": "Account access issue"},
        {"subject": "Question about billing cycle", "urgency": 2, "body": "Billing question"},
        {"subject": "Feature suggestion: Dark mode", "urgency": 1, "body": "Feature request"},
        {"subject": "Security alert: Unusual login detected", "urgency": 4, "body": "Security concern"},
        {"subject": "Refund request - double charged", "urgency": 3, "body": "Billing issue"}
    ]
    
    actions = []
    
    # Process each email
    for i, email in enumerate(emails):
        prompt = f"""Email: {email['subject']}
Urgency level: {email['urgency']}/5

Choose the best action from: archive, respond, escalate, request_info, mark_urgent
Reply with ONLY the action name."""
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a customer support agent. Reply with ONLY the action name, nothing else."},
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
            print(f"[WARN] API call failed for email {i}: {e}")
            action = "respond"
        
        actions.append(action)
        print(f"[STEP] step={i} action={action}")
    
    # Import grader
    from tasks.grader import run_grader
    
    # Create trajectory
    trajectory = create_trajectory(actions, emails)
    
    # Run all 3 task graders
    easy_score = run_grader('easy', trajectory)
    medium_score = run_grader('medium', trajectory)
    hard_score = run_grader('hard', trajectory)
    
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
    
    try:
        with open("baseline_scores.json", "w") as f:
            json.dump(scores, f, indent=2)
        print("[INFO] Saved baseline_scores.json")
    except Exception as e:
        print(f"[WARN] Could not save scores: {e}")
    
    sys.exit(0)


if __name__ == "__main__":
    main()