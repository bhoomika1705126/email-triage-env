from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel
import random
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
import uvicorn

# Define OpenEnv models
class Observation(BaseModel):
    email_subject: str
    email_body: str
    sender: str
    urgency_keywords: List[str]
    current_queue_size: int
    last_action_result: str = ""

class Action(BaseModel):
    action_type: str  # respond, escalate, archive, request_info, mark_urgent
    response_text: Optional[str] = None
    priority: Optional[int] = None

class Reward(BaseModel):
    value: float

class EmailTriageEnv:
    def __init__(self):
        self.reset()
        
    def reset(self) -> Observation:
        """Reset environment and return initial observation"""
        # Email database
        self.emails = [
            {
                "subject": "URGENT: Account locked - can't access funds",
                "body": "I've been locked out of my account for 3 hours. Need immediate access for a wire transfer!",
                "sender": "john.doe@example.com",
                "true_urgency": 5,
                "keywords": ["urgent", "locked", "immediate", "funds"]
            },
            {
                "subject": "Question about billing cycle",
                "body": "When does my monthly billing cycle reset? I'm on the basic plan.",
                "sender": "sarah@company.com",
                "true_urgency": 2,
                "keywords": ["billing", "question", "cycle"]
            },
            {
                "subject": "Feature suggestion: Dark mode",
                "body": "Would love to see dark mode in the mobile app. Just a suggestion!",
                "sender": "dev@user.net",
                "true_urgency": 1,
                "keywords": ["suggestion", "feature", "dark mode"]
            },
            {
                "subject": "Security alert: Unusual login detected",
                "body": "I received an alert about a login from a new device. Please verify my account security.",
                "sender": "security@customer.com",
                "true_urgency": 4,
                "keywords": ["security", "alert", "unusual", "login"]
            },
            {
                "subject": "Refund request - double charged",
                "body": "I was charged twice for my subscription this month. Need refund for $49.99.",
                "sender": "refund@example.com",
                "true_urgency": 3,
                "keywords": ["refund", "charged", "money", "double"]
            }
        ]
        
        self.current_email_idx = 0
        self.step_count = 0
        self.max_steps = 50
        self.queue_size = len(self.emails)
        self.trajectory = []  # Store trajectory for grading
        
        return self._get_observation()
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        """Execute action and return next state, reward, done, info"""
        self.step_count += 1
        
        # Get current email
        email = self.emails[self.current_email_idx]
        true_urgency = email["true_urgency"]
        
        # Store step in trajectory
        self.trajectory.append({
            "email": email,
            "action": action.dict() if hasattr(action, 'dict') else action,
            "step": self.step_count
        })
        
        # Calculate reward based on action quality
        reward = 0.0
        
        # Action validation and reward calculation
        if action.action_type == "respond":
            if action.response_text and len(action.response_text) > 10:
                # Good response with proper length
                if true_urgency >= 4:
                    reward = 0.9  # High urgency needs quick response
                elif true_urgency <= 2:
                    reward = 0.5  # Low urgency, response is fine but not critical
                else:
                    reward = 0.7
                result_msg = f"Responded to email with {len(action.response_text)} chars"
            else:
                reward = 0.1  # Poor response
                result_msg = "Response too short or missing"
                
        elif action.action_type == "escalate":
            if true_urgency >= 4:
                reward = 0.8  # Correct escalation of high-urgency issue
                result_msg = "Correctly escalated urgent issue"
            else:
                reward = 0.2  # Escalated low-priority issue unnecessarily
                result_msg = "Unnecessary escalation"
                
        elif action.action_type == "archive":
            if true_urgency <= 2:
                reward = 0.9  # Correctly archived low-priority email
                result_msg = "Correctly archived low-priority email"
            else:
                reward = 0.0  # Archived important email - bad!
                result_msg = "ERROR: Archived important email"
                
        elif action.action_type == "request_info":
            if true_urgency >= 3:
                reward = 0.3  # Asking for info delays resolution
                result_msg = "Requested info instead of acting"
            else:
                reward = 0.6  # Fine for low-priority emails
                result_msg = "Requested additional information"
                
        elif action.action_type == "mark_urgent":
            if action.priority:
                accuracy = 1 - abs(action.priority - true_urgency) / 5
                reward = 0.5 * accuracy
                result_msg = f"Marked urgency as {action.priority}/5"
            else:
                reward = 0.2
                result_msg = "Marked urgent without priority"
        else:
            reward = 0.0
            result_msg = "Invalid action"
        
        # Progress reward (moving through queue)
        progress_reward = 0.1
        reward += progress_reward
        
        # Penalty for taking too long
        if self.step_count > 30:
            reward -= 0.05
        
        # Move to next email or done
        done = False
        if self.current_email_idx >= len(self.emails) - 1:
            done = True
            # Bonus for completing all emails
            if self.step_count <= 40:
                reward += 0.5
        else:
            self.current_email_idx += 1
        
        # Clip reward between 0 and 1
        reward = max(0.0, min(1.0, reward))
        
        observation = self._get_observation()
        observation.last_action_result = result_msg
        
        info = {
            "step": self.step_count,
            "queue_progress": f"{self.current_email_idx + 1}/{len(self.emails)}",
            "action_taken": action.action_type
        }
        
        return observation, reward, done, info
    
    def _get_observation(self) -> Observation:
        """Get current observation"""
        email = self.emails[self.current_email_idx]
        return Observation(
            email_subject=email["subject"],
            email_body=email["body"],
            sender=email["sender"],
            urgency_keywords=email["keywords"],
            current_queue_size=self.queue_size - self.current_email_idx
        )
    
    def get_trajectory(self) -> List[Dict]:
        """Return trajectory for grading"""
        return self.trajectory
    
    def state(self) -> Dict[str, Any]:
        """Return current state for debugging"""
        return {
            "current_email": self.current_email_idx,
            "total_emails": len(self.emails),
            "step_count": self.step_count,
            "queue_size": self.queue_size - self.current_email_idx
        }
    
    def close(self):
        """Clean up resources"""
        pass

# FastAPI app for HF Spaces
app = FastAPI(title="Email Triage Environment")

# Singleton environment instance
_env = None

def get_env():
    global _env
    if _env is None:
        _env = EmailTriageEnv()
    return _env

class StepRequest(BaseModel):
    action: Action

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict

@app.get("/reset")
async def reset():
    """Reset the environment"""
    env = get_env()
    obs = env.reset()
    return {"observation": obs.dict()}

@app.post("/step")
async def step(request: StepRequest):
    """Take a step in the environment"""
    env = get_env()
    obs, reward, done, info = env.step(request.action)
    return StepResponse(
        observation=obs,
        reward=reward,
        done=done,
        info=info
    )

@app.get("/state")
async def get_state():
    """Get current state"""
    env = get_env()
    return env.state()

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "environment": "email-triage-env"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Email Triage Environment",
        "version": "1.0.0",
        "endpoints": ["/reset", "/step", "/state", "/health"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)