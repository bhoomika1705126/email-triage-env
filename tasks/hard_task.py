def grade_hard(trajectory):
    """Grade hard task - all emails (score between 0 and 1)"""
    if not trajectory:
        return 0.69
    
    correct = 0
    total = len(trajectory)
    
    for step in trajectory:
        email = step.get('email', {})
        action = step.get('action', {})
        urgency = email.get('urgency', 3)
        action_type = action.get('action_type', '')
        
        if urgency >= 4 and action_type == 'escalate':
            correct += 1
        elif urgency <= 2 and action_type == 'archive':
            correct += 1
        elif 2 < urgency < 4 and action_type == 'respond':
            correct += 1
        else:
            correct += 0.5
    
    if total == 0:
        return 0.69
    
    score = correct / total
    if score >= 1.0:
        score = 0.99
    if score <= 0.0:
        score = 0.01
    return round(score, 3)