"""Task graders for Email Triage Environment - Enhanced Scoring"""

def grade_easy(trajectory):
    """
    Grade easy task - low urgency emails (urgency 1-2)
    Tests: Agent should archive or respond appropriately
    """
    if not trajectory:
        return 0.67
    
    total_score = 0
    total_emails = 0
    
    for step in trajectory:
        email = step.get('email', {})
        action = step.get('action', {})
        urgency = email.get('urgency', 3)
        
        # Only grade low urgency emails
        if urgency <= 2:
            total_emails += 1
            action_type = action.get('action_type', '')
            
            # Perfect: archive
            if action_type == 'archive':
                total_score += 1.0
            # Good: respond (acceptable but not optimal)
            elif action_type == 'respond':
                total_score += 0.7
            # Bad: escalate or request_info (wastes time)
            elif action_type in ['escalate', 'request_info']:
                total_score += 0.2
            # Worst: mark_urgent (completely wrong)
            elif action_type == 'mark_urgent':
                total_score += 0.0
            else:
                total_score += 0.3
    
    if total_emails == 0:
        return 0.67
    
    score = total_score / total_emails
    # Ensure strictly between 0 and 1
    return max(0.01, min(0.99, round(score, 3)))


def grade_medium(trajectory):
    """
    Grade medium task - high urgency emails (urgency 4-5)
    Tests: Agent should escalate or mark urgent appropriately
    """
    if not trajectory:
        return 0.68
    
    total_score = 0
    total_emails = 0
    
    for step in trajectory:
        email = step.get('email', {})
        action = step.get('action', {})
        urgency = email.get('urgency', 3)
        
        # Only grade high urgency emails
        if urgency >= 4:
            total_emails += 1
            action_type = action.get('action_type', '')
            
            # Perfect: escalate
            if action_type == 'escalate':
                total_score += 1.0
            # Good: mark_urgent (acknowledges urgency)
            elif action_type == 'mark_urgent':
                priority = action.get('priority', 0)
                # Bonus for correct priority level
                if priority == urgency:
                    total_score += 0.9
                else:
                    total_score += 0.7
            # Acceptable: respond (but not ideal)
            elif action_type == 'respond':
                total_score += 0.4
            # Bad: archive (ignores urgency)
            elif action_type == 'archive':
                total_score += 0.0
            else:
                total_score += 0.3
    
    if total_emails == 0:
        return 0.68
    
    score = total_score / total_emails
    return max(0.01, min(0.99, round(score, 3)))


def grade_hard(trajectory):
    """
    Grade hard task - all emails with efficiency bonus
    Tests: Appropriate actions for all emails + speed
    """
    if not trajectory:
        return 0.69
    
    total_score = 0
    total_emails = len(trajectory)
    
    for step in trajectory:
        email = step.get('email', {})
        action = step.get('action', {})
        urgency = email.get('urgency', 3)
        action_type = action.get('action_type', '')
        
        # Score based on action appropriateness
        if urgency >= 4:
            if action_type == 'escalate':
                total_score += 1.0
            elif action_type == 'mark_urgent':
                total_score += 0.8
            elif action_type == 'respond':
                total_score += 0.4
            elif action_type == 'archive':
                total_score += 0.0
            else:
                total_score += 0.5
                
        elif urgency <= 2:
            if action_type == 'archive':
                total_score += 1.0
            elif action_type == 'respond':
                total_score += 0.7
            elif action_type == 'escalate':
                total_score += 0.3
            else:
                total_score += 0.5
                
        else:  # urgency 3 (medium)
            if action_type == 'respond':
                total_score += 1.0
            elif action_type == 'request_info':
                total_score += 0.8
            elif action_type == 'escalate':
                total_score += 0.5
            elif action_type == 'archive':
                total_score += 0.3
            else:
                total_score += 0.6
    
    # Efficiency bonus: faster is better
    base_score = total_score / total_emails
    
    # Bonus for completing in fewer steps (max 5 emails)
    steps_taken = len(trajectory)
    if steps_taken <= 5:
        efficiency_bonus = 0.10
    elif steps_taken <= 7:
        efficiency_bonus = 0.05
    elif steps_taken <= 10:
        efficiency_bonus = 0.02
    else:
        efficiency_bonus = 0.00
    
    final_score = base_score + efficiency_bonus
    return max(0.01, min(0.99, round(final_score, 3)))


def run_grader(task_name, trajectory):
    """Main function called by inference.py"""
    graders = {
        'easy': grade_easy,
        'medium': grade_medium,
        'hard': grade_hard
    }
    
    grader = graders.get(task_name.lower())
    if grader:
        score = grader(trajectory)
        # Ensure strictly between 0 and 1
        return max(0.01, min(0.99, score))
    return 0.50
