# test_fixed.py - Quick test with fixed grader
from environment import EmailTriageEnv, Action
from tasks.grader import run_grader

print("Testing fixed grader...")

env = EmailTriageEnv()
obs = env.reset()
trajectory = []

# Simulate some actions
for i in range(3):
    action = Action(action_type="archive")
    obs, reward, done, info = env.step(action)
    
    trajectory.append({
        "step": i,
        "email": {
            "subject": obs.email_subject,
            "true_urgency": 2  # Explicitly set urgency
        },
        "action": {"action_type": "archive"}
    })

# Test grader
score = run_grader("easy", trajectory)
print(f"Easy task score: {score}")

if score >= 0:
    print("✓ Grader working correctly!")
else:
    print("✗ Grader still has issues")