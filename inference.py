#!/usr/bin/env python
"""Inference script that runs 3 tasks with graders - Phase 2 Compliant"""
import json
import sys
import os
from openai import OpenAI

# ============================================
# TASK GRADERS (built-in)
# ============================================

def grade_easy_task(actions, emails):
    """Grade easy task: correctly archive low-urgency emails"""
    if not actions:
        return 0.0
    
    correct = 0
    total = 0
    for i, (email, action) in enumerate(zip(emails, actions)):
        urgency = email.get('urgency', 3)
        if urgency <= 2:  # Low urgency emails
            total += 1
            if action == 'archive':
                correct += 1
            elif action == 'respond':
                correct += 0.5
    
    if total == 0:
        return 0.5
    return correct / total

def grade_medium_task(actions, emails):
    """Grade medium task: correctly escalate urgent issues"""
    if not actions:
        return 0.0
    
    correct = 0
    total = 0
    for i, (email, action) in enumerate(zip(emails, actions)):
        urgency = email.get('urgency', 3)
        if urgency >= 4:  # High urgency emails
            total += 1
            if action == 'escalate':
                correct += 1
            elif action == 'mark_urgent':
                correct += 0.5
    
    if total == 0:
        return 0.5
    return correct / total

def grade_hard_task(actions, emails):
    """Grade hard task: appropriate responses for all emails"""
    if not actions:
        return 0.0
    
    correct = 0
    for i, (email, action) in enumerate(zip(emails, actions)):
        urgency = email.get('urgency', 3)
        
        if urgency >= 4 and action == 'escalate':
            correct += 1
        elif urgency <= 2 and action == 'archive':
            correct += 1
        elif 2 < urgency < 4 and action == 'respond':
            correct += 1
        elif action in ['respond', 'archive', 'escalate', 'request_info', 'mark_urgent']:
            correct += 0.5
    
    return correct / len(emails)

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print("[START] task=email_triage")
    
    # Get API credentials
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
    
    if not api_key:
        print("[ERROR] No API_KEY found")
        print("[END] task=email_triage score=0.0 steps=0")
        sys.exit(1)
    
    client = OpenAI(base_url=api_base_url, api_key=api_key)
    
    # Email dataset
    emails = [
        {"subject": "URGENT: Account locked - can't access funds", "urgency": 5},
        {"subject": "Question about billing cycle", "urgency": 2},
        {"subject": "Feature suggestion: Dark mode", "urgency": 1},
        {"subject": "Security alert: Unusual login detected", "urgency": 4},
        {"subject": "Refund request - double charged", "urgency": 3}
    ]
    
    # Run inference to get actions
    actions = []
    
    for i, email in enumerate(emails):
        prompt = f"""Email: {email['subject']}
Urgency: {email['urgency']}/5

Choose action (archive/respond/escalate/request_info/mark_urgent):"""
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a customer support agent. Reply with ONLY the action name."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=20
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
            print(f"[ERROR] API call failed: {e}")
            action = "respond"
        
        actions.append(action)
        print(f"[STEP] step={i} action={action}")
    
    # Run all 3 task graders
    easy_score = grade_easy_task(actions, emails)
    medium_score = grade_medium_task(actions, emails)
    hard_score = grade_hard_task(actions, emails)
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