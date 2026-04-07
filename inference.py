import os
import sys
import json
import time
from openai import OpenAI
from environment import EmailTriageEnv, Action

SYSTEM_PROMPT = """You are an AI customer support agent handling email triage.
Your task is to process each email appropriately.

Actions available:
- respond: Send a response (requires response_text)
- escalate: Escalate to human agent (for urgent/security issues)
- archive: Archive low-priority email
- request_info: Ask customer for more information
- mark_urgent: Mark with priority 1-5 (requires priority)

Respond professionally and efficiently. Archive only truly low-priority emails."""

def get_urgency_from_keywords(keywords):
    """Convert keywords list to urgency score (1-5)"""
    if not keywords:
        return 3
    
    keywords_str = ' '.join(keywords).lower()
    
    high_urgency = ['urgent', 'locked', 'immediate', 'funds', 'wire']
    if any(kw in keywords_str for kw in high_urgency):
        return 5
    
    med_high_urgency = ['security', 'alert', 'unusual', 'login']
    if any(kw in keywords_str for kw in med_high_urgency):
        return 4
    
    medium_urgency = ['refund', 'charged', 'money', 'double']
    if any(kw in keywords_str for kw in medium_urgency):
        return 3
    
    low_urgency = ['billing', 'question', 'cycle']
    if any(kw in keywords_str for kw in low_urgency):
        return 2
    
    very_low = ['suggestion', 'feature', 'dark mode']
    if any(kw in keywords_str for kw in very_low):
        return 1
    
    return 3

def parse_model_action(response_text: str) -> dict:
    """Parse model response into action dict"""
    if not response_text:
        return {"action_type": "respond", "response_text": "Thank you for your message."}
    
    response_lower = response_text.lower()
    
    if "respond" in response_lower:
        return {"action_type": "respond", "response_text": response_text[:200]}
    elif "escalate" in response_lower:
        return {"action_type": "escalate"}
    elif "archive" in response_lower:
        return {"action_type": "archive"}
    elif "request info" in response_lower or "request_info" in response_lower:
        return {"action_type": "request_info"}
    elif "urgent" in response_lower:
        priority = 3
        for i in range(1, 6):
            if str(i) in response_lower:
                priority = i
        return {"action_type": "mark_urgent", "priority": priority}
    else:
        return {"action_type": "respond", "response_text": "Thank you for your message. We'll look into this."}

def run_episode(env, model_name: str, api_base_url: str, api_key: str, task_name: str = "easy"):
    """Run one episode and return trajectory"""
    try:
        client = OpenAI(
            base_url=api_base_url,
            api_key=api_key,
            timeout=30
        )
    except Exception as e:
        print(f"Failed to create OpenAI client: {e}")
        return []
    
    try:
        observation = env.reset()
    except Exception as e:
        print(f"Failed to reset environment: {e}")
        return []
    
    trajectory = []
    done = False
    step = 0
    max_steps = 20  # Reduced for faster validation
    
    while not done and step < max_steps:
        prompt = f"""Current email:
Subject: {observation.email_subject}
Body: {observation.email_body[:300]}
Sender: {observation.sender}
Queue size: {observation.current_queue_size}
Urgency keywords: {', '.join(observation.urgency_keywords)}

Last action result: {observation.last_action_result}

Choose an action and respond in natural language (e.g., 'respond with: [response]' or 'escalate'):"""
        
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            response = completion.choices[0].message.content or ""
        except Exception as e:
            print(f"API Error: {e}")
            response = "respond with: I'm looking into your issue."
        
        try:
            action_dict = parse_model_action(response)
            action = Action(**action_dict)
            
            urgency_score = get_urgency_from_keywords(observation.urgency_keywords)
            
            trajectory.append({
                "step": step,
                "email": {
                    "subject": observation.email_subject,
                    "body": observation.email_body[:200],
                    "sender": observation.sender,
                    "true_urgency": urgency_score
                },
                "action": action_dict,
                "response": response
            })
            
            observation, reward, done, info = env.step(action)
            print(f"STEP {step}: {action.action_type}")
            
        except Exception as e:
            print(f"Step {step} failed: {e}")
            done = True
        
        step += 1
    
    return trajectory

def main():
    print("START")
    
    # Read environment variables with safe defaults
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    # Fallback to Groq
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if api_key:
            api_base_url = "https://api.groq.com/openai/v1"
            model_name = "llama-3.3-70b-versatile"
            print("Using Groq API")
    
    # Fallback to OpenRouter
    if not api_key:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if api_key:
            api_base_url = "https://openrouter.ai/api/v1"
            model_name = "x-ai/grok-beta"
            print("Using OpenRouter API")
    
    if not api_key:
        print("ERROR: No API key found!")
        print("Set OPENAI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY")
        print("END")
        sys.exit(1)
    
    print(f"Using API: {api_base_url}")
    print(f"Model: {model_name}")
    
    try:
        from tasks.grader import run_grader
    except ImportError as e:
        print(f"Failed to import grader: {e}")
        print("END")
        sys.exit(1)
    
    try:
        env = EmailTriageEnv()
    except Exception as e:
        print(f"Failed to create environment: {e}")
        print("END")
        sys.exit(1)
    
    scores = {}
    
    for task_name in ['easy', 'medium', 'hard']:
        print(f"\n=== Running {task_name.upper()} task ===")
        
        try:
            env.reset()
            trajectory = run_episode(env, model_name, api_base_url, api_key, task_name)
            
            if not trajectory:
                print(f"Warning: No trajectory generated for {task_name}")
                scores[task_name] = 0.0
            else:
                score = run_grader(task_name, trajectory)
                scores[task_name] = score
                print(f"Score: {score:.3f}")
        except Exception as e:
            print(f"Task {task_name} failed: {e}")
            scores[task_name] = 0.0
    
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        scores['average'] = avg_score
        scores['model'] = model_name
    
    try:
        with open('baseline_scores.json', 'w') as f:
            json.dump(scores, f, indent=2)
        print("\nScores saved to baseline_scores.json")
    except Exception as e:
        print(f"Failed to save scores: {e}")
    
    print("\nFINAL RESULTS:")
    for task, score in scores.items():
        if task not in ['model', 'provider']:
            print(f"  {task.upper()}: {score:.3f}")
    
    print("END")

if __name__ == "__main__":
    main()