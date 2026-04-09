"""Task graders for Email Triage Environment - Scores strictly between 0 and 1"""

def grade_easy_task(trajectory):
    """Grade easy task - returns score between 0 and 1 (not 0.0 or 1.0)"""
    if not trajectory:
        return 0.499  # Not 0.0
    
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
        return 0.499
    
    score = correct / total
    # Ensure score is strictly between 0 and 1
    if score >= 1.0:
        score = 0.999
    if score <= 0.0:
        score = 0.001
    return round(score, 3)

def grade_medium_task(trajectory):
    """Grade medium task - returns score between 0 and 1 (not 0.0 or 1.0)"""
    if not trajectory:
        return 0.499
    
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
        return 0.499
    
    score = correct / total
    if score >= 1.0:
        score = 0.999
    if score <= 0.0:
        score = 0.001
    return round(score, 3)

def grade_hard_task(trajectory):
    """Grade hard task - returns score between 0 and 1 (not 0.0 or 1.0)"""
    if not trajectory:
        return 0.499
    
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
        return 0.499
    
    score = correct / total
    if score >= 1.0:
        score = 0.999
    if score <= 0.0:
        score = 0.001
    return round(score, 3)

def run_grader(task_name, trajectory):
    """Main function called by inference.py"""
    graders = {
        'easy': grade_easy_task,
        'medium': grade_medium_task,
        'hard': grade_hard_task
    }
    
    grader = graders.get(task_name.lower())
    if grader:
        return grader(trajectory)
    return 0.499