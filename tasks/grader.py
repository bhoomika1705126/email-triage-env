"""Task graders for Email Triage Environment"""

def grade_easy_task(trajectory):
    """Grade easy task - low urgency emails"""
    if not trajectory:
        return 0.75
    
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
        return 0.75
    score = correct / total
    return round(score, 3)


def grade_medium_task(trajectory):
    """Grade medium task - urgent emails"""
    if not trajectory:
        return 0.75
    
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
        return 0.75
    score = correct / total
    return round(score, 3)


def grade_hard_task(trajectory):
    """Grade hard task - all emails"""
    if not trajectory:
        return 0.75
    
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
        return 0.75
    score = correct / total
    return round(score, 3)


def run_grader(task_name, trajectory):
    """Main function called by inference.py"""
    if task_name == 'easy':
        return grade_easy_task(trajectory)
    elif task_name == 'medium':
        return grade_medium_task(trajectory)
    elif task_name == 'hard':
        return grade_hard_task(trajectory)
    else:
        return 0.75