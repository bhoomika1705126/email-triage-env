"""Task graders for Email Triage Environment"""

def run_grader(task_name, trajectory):
    """Return score between 0.0 and 1.0 for the given task"""
    if not trajectory:
        return 0.75
    
    if task_name == 'easy':
        # Check low urgency emails (urgency <= 2)
        correct = 0
        total = 0
        for step in trajectory:
            email = step.get('email', {})
            action = step.get('action', {})
            urgency = email.get('urgency', 3)
            if urgency <= 2:
                total += 1
                if action.get('action_type') == 'archive':
                    correct += 1
        if total == 0:
            return 0.75
        return round(correct / total, 3)
    
    elif task_name == 'medium':
        # Check high urgency emails (urgency >= 4)
        correct = 0
        total = 0
        for step in trajectory:
            email = step.get('email', {})
            action = step.get('action', {})
            urgency = email.get('urgency', 3)
            if urgency >= 4:
                total += 1
                if action.get('action_type') == 'escalate':
                    correct += 1
        if total == 0:
            return 0.75
        return round(correct / total, 3)
    
    elif task_name == 'hard':
        # Check all emails
        correct = 0
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
        total = len(trajectory)
        if total == 0:
            return 0.75
        return round(correct / total, 3)
    
    else:
        return 0.75
