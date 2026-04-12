"""Task graders for Email Triage Environment"""

def grade_easy(trajectory):
    """Grade easy task - low urgency emails (score strictly between 0 and 1)"""
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
    if score >= 1.0:
        score = 0.99
    if score <= 0.0:
        score = 0.01
    return round(score, 3)


def grade_medium(trajectory):
    """Grade medium task - high urgency emails (score strictly between 0 and 1)"""
    if not trajectory:
        return 0.68
    
    correct = 0
    total = 0
    
    for step in trajectory:
        email = step.get('email', {})
        action = step.get('action', {})
        urgency = email.get('urgency', 3)
        
        if urgency >= 4:
            total += 1
            action_type = action.get('action_type', '')
            if action_type == 'escalate':
                correct += 1
            elif action_type == 'mark_urgent':
                correct += 0.5
    
    if total == 0:
        return 0.68
    
    score = correct / total
    if score >= 1.0:
        score = 0.99
    if score <= 0.0:
        score = 0.01
    return round(score, 3)


def grade_hard(trajectory):
    """Grade hard task - all emails (score strictly between 0 and 1)"""
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


def run_grader(task_name, trajectory):
    """Main function called by inference.py"""
    if task_name == 'easy':
        return grade_easy(trajectory)
    elif task_name == 'medium':
        return grade_medium(trajectory)
    elif task_name == 'hard':
        return grade_hard(trajectory)
    return 0.50
