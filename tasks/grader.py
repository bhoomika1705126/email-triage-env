# tasks/grader.py - Improved version for Phase 2
from typing import Dict, Any, List

class TaskGrader:
    """Base class for task graders"""
    def grade(self, trajectory: List[Dict]) -> float:
        raise NotImplementedError

class EasyTaskGrader(TaskGrader):
    """Easy: Respond appropriately to low-urgency emails"""
    def grade(self, trajectory: List[Dict]) -> float:
        """
        Score based on:
        - Correctly archives low-urgency emails (urgency 1-2)
        - Provides appropriate responses
        """
        if not trajectory:
            return 0.0
            
        score = 0.0
        correct_actions = 0
        total_low_urgency = 0
        
        for step in trajectory:
            email = step.get('email', {})
            action = step.get('action', {})
            
            # Get urgency - handle both int and list cases
            urgency = email.get('true_urgency', 0)
            if isinstance(urgency, list):
                urgency = 3
            
            if urgency <= 2:
                total_low_urgency += 1
                action_type = action.get('action_type', '')
                if action_type == 'archive':
                    correct_actions += 1
                elif action_type == 'respond' and action.get('response_text'):
                    correct_actions += 0.5
        
        if total_low_urgency > 0:
            score = correct_actions / total_low_urgency
        
        return min(1.0, max(0.0, score))

class MediumTaskGrader(TaskGrader):
    """Medium: Prioritize correctly and escalate urgent issues"""
    def grade(self, trajectory: List[Dict]) -> float:
        """
        Score based on:
        - Correct priority assignment for urgent emails
        - Proper escalation of security/financial issues
        """
        if not trajectory:
            return 0.0
            
        score = 0.0
        points = 0
        total_points = 0
        
        for step in trajectory:
            email = step.get('email', {})
            action = step.get('action', {})
            
            urgency = email.get('true_urgency', 0)
            if isinstance(urgency, list):
                urgency = 3
            
            if urgency >= 4:
                total_points += 2
                action_type = action.get('action_type', '')
                if action_type == 'escalate':
                    points += 2
                elif action_type == 'mark_urgent':
                    priority = action.get('priority', 0)
                    if priority >= 4:
                        points += 1.5
            
            if urgency >= 4 and action.get('action_type') == 'archive':
                points -= 1
        
        if total_points > 0:
            score = max(0.0, points / total_points)
        
        return min(1.0, max(0.0, score))

class HardTaskGrader(TaskGrader):
    """Hard: Multi-step resolution with proper communication"""
    def grade(self, trajectory: List[Dict]) -> float:
        """
        Score based on:
        - Complete resolution of complex issues
        - Appropriate follow-up actions
        - Professional communication
        """
        if not trajectory:
            return 0.0
            
        score = 0.0
        criteria_scores = []
        
        # Criterion 1: Resolution quality (0-0.4)
        resolution_score = 0.0
        if trajectory:
            final_action = trajectory[-1].get('action', {})
            
            if final_action.get('action_type') == 'respond':
                response = final_action.get('response_text', '')
                resolution_indicators = ['resolved', 'fixed', 'completed', 'done', 'refunded', 'thank']
                if any(indicator in str(response).lower() for indicator in resolution_indicators):
                    resolution_score = 0.4
                elif len(str(response)) > 50:
                    resolution_score = 0.2
        
        criteria_scores.append(resolution_score)
        
        # Criterion 2: No repeated mistakes (0-0.3)
        mistake_penalty = 0.0
        action_types = [step.get('action', {}).get('action_type', '') for step in trajectory]
        
        if len(action_types) > 3:
            unique_actions = len(set(action_types))
            if unique_actions < len(action_types) * 0.5:
                mistake_penalty = 0.1
        
        no_mistake_score = 0.3 - mistake_penalty
        criteria_scores.append(max(0.0, no_mistake_score))
        
        # Criterion 3: Efficiency (0-0.3)
        efficiency_score = 0.0
        steps = len(trajectory)
        
        if steps <= 10:
            efficiency_score = 0.3
        elif steps <= 20:
            efficiency_score = 0.2
        elif steps <= 30:
            efficiency_score = 0.1
        else:
            efficiency_score = 0.0
        
        criteria_scores.append(efficiency_score)
        
        score = sum(criteria_scores)
        return min(1.0, max(0.0, score))

def run_grader(task_name: str, trajectory: List[Dict]) -> float:
    """Run the appropriate grader for the task"""
    graders = {
        'easy': EasyTaskGrader(),
        'medium': MediumTaskGrader(),
        'hard': HardTaskGrader()
    }
    
    grader = graders.get(task_name.lower())
    if not grader:
        return 0.0  # Return 0.0 instead of raising exception
    
    try:
        result = grader.grade(trajectory)
        return min(1.0, max(0.0, result))
    except Exception:
        return 0.0