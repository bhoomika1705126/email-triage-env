def grade_easy(trajectory):
    """Grade easy task - low urgency emails (score between 0 and 1)"""
    if not trajectory:
        return 0.67
    
    correct = 0
    total = 0
    
    for step in trajectory:
        email = step.get('email', {})
        action = step.get('action', {})
        urgency = email.get('urgency', 3)
        
        if urgency <= 2:
            total += 1
            action_type = action.get('action_type', '')
            if action_type == 'archive':
                correct += 1
            elif action_type == 'respond':
                correct += 0.5
    
    if total == 0:
        return 0.67
    
    score = correct / total
    # Ensure strictly between 0 and 1
    if score >= 1.0:
        score = 0.99
    if score <= 0.0:
        score = 0.01
    return round(score, 3)