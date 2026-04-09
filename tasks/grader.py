"""Task graders for Email Triage Environment - 3 tasks with proper scoring"""

def grade_easy_task(trajectory):
    """
    Easy Task: Handle low-urgency emails correctly
    Expected: Archive or appropriate response for urgency 1-2 emails
    Returns: Score between 0.0 and 1.0
    """
    if not trajectory:
        return 0.0
    
    total_low_urgency = 0
    correct_actions = 0
    
    for step in trajectory:
        email = step.get('email', {})
        action = step.get('action', {})
        
        # Get urgency (handle both int and dict cases)
        urgency = email.get('true_urgency', 3)
        if isinstance(urgency, dict):
            urgency = urgency.get('value', 3)
        
        # Low urgency emails (1-2)
        if urgency <= 2:
            total_low_urgency += 1
            action_type = action.get('action_type', '')
            
            if action_type == 'archive':
                correct_actions += 1
            elif action_type == 'respond':
                correct_actions += 0.5
    
    if total_low_urgency == 0:
        return 0.5
    
    score = correct_actions / total_low_urgency
    return min(1.0, max(0.0, score))


def grade_medium_task(trajectory):
    """
    Medium Task: Handle urgent emails correctly
    Expected: Escalate or mark urgent for urgency 4-5 emails
    Returns: Score between 0.0 and 1.0
    """
    if not trajectory:
        return 0.0
    
    total_high_urgency = 0
    correct_actions = 0
    
    for step in trajectory:
        email = step.get('email', {})
        action = step.get('action', {})
        
        # Get urgency
        urgency = email.get('true_urgency', 3)
        if isinstance(urgency, dict):
            urgency = urgency.get('value', 3)
        
        # High urgency emails (4-5)
        if urgency >= 4:
            total_high_urgency += 1
            action_type = action.get('action_type', '')
            
            if action_type == 'escalate':
                correct_actions += 1
            elif action_type == 'mark_urgent':
                correct_actions += 0.5
    
    if total_high_urgency == 0:
        return 0.5
    
    score = correct_actions / total_high_urgency
    return min(1.0, max(0.0, score))


def grade_hard_task(trajectory):
    """
    Hard Task: Handle all emails with appropriate actions
    Returns: Score between 0.0 and 1.0
    """
    if not trajectory:
        return 0.0
    
    total_emails = len(trajectory)
    correct_actions = 0
    
    for step in trajectory:
        email = step.get('email', {})
        action = step.get('action', {})
        
        # Get urgency
        urgency = email.get('true_urgency', 3)
        if isinstance(urgency, dict):
            urgency = urgency.get('value', 3)
        
        action_type = action.get('action_type', '')
        
        # Check if action is appropriate for urgency
        if urgency >= 4 and action_type == 'escalate':
            correct_actions += 1
        elif urgency <= 2 and action_type == 'archive':
            correct_actions += 1
        elif 2 < urgency < 4 and action_type == 'respond':
            correct_actions += 1
        elif action_type in ['respond', 'archive', 'escalate', 'request_info', 'mark_urgent']:
            correct_actions += 0.5
    
    if total_emails == 0:
        return 0.0
    
    score = correct_actions / total_emails
    return min(1.0, max(0.0, score))


def run_grader(task_name, trajectory):
    """Main function that runs the appropriate grader"""
    graders = {
        'easy': grade_easy_task,
        'medium': grade_medium_task,
        'hard': grade_hard_task
    }
    
    grader = graders.get(task_name.lower())
    if grader is None:
        return 0.0
    
    try:
        score = grader(trajectory)
        return min(1.0, max(0.0, float(score)))
    except Exception:
        return 0.0