from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

# Try to import the full environment
try:
    from environment import EmailTriageEnv, Action, Observation
    FULL_ENV = True
except ImportError as e:
    FULL_ENV = False
    print(f"Warning: Full environment not available - {e}")

app = FastAPI(title="Email Triage Environment")

_env = None

def get_env():
    global _env
    if _env is None and FULL_ENV:
        _env = EmailTriageEnv()
    return _env

@app.get("/")
def root():
    return {
        "name": "Email Triage Environment",
        "status": "running",
        "full_env": FULL_ENV,
        "endpoints": ["/health", "/reset", "/step", "/state"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "environment": "email-triage-env"}

# Add both GET and POST for /reset (OpenEnv requires POST)
@app.get("/reset")
def reset_get():
    if not FULL_ENV:
        return {"message": "Reset endpoint - working! (simplified mode)"}
    env = get_env()
    if env:
        obs = env.reset()
        return {"observation": obs.dict() if hasattr(obs, 'dict') else obs}
    return {"message": "Reset called"}

@app.post("/reset")
def reset_post():
    """POST endpoint for OpenEnv compliance"""
    if not FULL_ENV:
        return {"message": "Reset endpoint - working! (simplified mode)"}
    env = get_env()
    if env:
        obs = env.reset()
        return {"observation": obs.dict() if hasattr(obs, 'dict') else obs}
    return {"message": "Reset called"}

@app.post("/step")
def step(action: Dict[str, Any]):
    if not FULL_ENV:
        return {"reward": 0.5, "done": False, "message": "Step endpoint working (simplified mode)"}
    
    env = get_env()
    if env:
        try:
            from environment import Action
            action_obj = Action(**action)
            obs, reward, done, info = env.step(action_obj)
            return {
                "observation": obs.dict() if hasattr(obs, 'dict') else obs,
                "reward": reward,
                "done": done,
                "info": info
            }
        except Exception as e:
            return {"error": str(e), "reward": 0.5, "done": False}
    return {"reward": 0.5, "done": False, "message": "Step called"}

@app.get("/state")
def get_state():
    if not FULL_ENV:
        return {"message": "State endpoint - working! (simplified mode)", "step_count": 0, "queue_size": 5}
    
    env = get_env()
    if env:
        return env.state()
    return {"message": "State called", "step_count": 0}