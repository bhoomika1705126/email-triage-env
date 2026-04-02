# server.py (in root directory, not in server folder)
import sys
import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment import EmailTriageEnv, Action, Observation

# Create FastAPI app
app = FastAPI(title="Email Triage Environment", version="1.0.0")

# Global environment instance
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
    info: Dict[str, Any]

@app.get("/")
async def root():
    return {
        "name": "Email Triage Environment",
        "version": "1.0.0",
        "description": "Email triage for AI agents",
        "endpoints": ["/reset", "/step", "/state", "/health"]
    }

@app.get("/reset")
async def reset():
    """Reset environment to initial state"""
    env = get_env()
    obs = env.reset()
    return {"observation": obs.dict()}

@app.post("/step")
async def step(request: StepRequest):
    """Execute an action in the environment"""
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
    """Get current environment state"""
    env = get_env()
    return env.state()

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": "email-triage-env",
        "ready": True
    }

def main():
    """Main entry point for the server"""
    print("Starting Email Triage Environment Server...")
    print("Server running at http://0.0.0.0:7860")
    print("Health check: http://0.0.0.0:7860/health")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=7860,
        log_level="info"
    )

if __name__ == "__main__":
    main()