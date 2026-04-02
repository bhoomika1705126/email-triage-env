# test_openenv.py
from environment import EmailTriageEnv
from tasks.grader import run_grader

print("Testing OpenEnv compliance...")

# Test 1: Environment creation
try:
    env = EmailTriageEnv()
    print("✓ Environment created successfully")
except Exception as e:
    print(f"✗ Failed to create environment: {e}")
    exit(1)

# Test 2: Reset
try:
    obs = env.reset()
    print(f"✓ Reset successful - First email: {obs.email_subject[:50]}...")
except Exception as e:
    print(f"✗ Reset failed: {e}")
    exit(1)

# Test 3: Step
try:
    from environment import Action
    action = Action(action_type="archive")
    obs, reward, done, info = env.step(action)
    print(f"✓ Step successful - Reward: {reward}, Done: {done}")
except Exception as e:
    print(f"✗ Step failed: {e}")
    exit(1)

# Test 4: State
try:
    state = env.state()
    print(f"✓ State method works - {state}")
except Exception as e:
    print(f"✗ State failed: {e}")
    exit(1)

print("\n✓ All OpenEnv basic tests passed!")