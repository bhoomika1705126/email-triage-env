import os
import sys
import json
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
    
    # Convert keywords to string for searching
    keywords_str = ' '.join(keywords).lower()
    
    # High urgency keywords (5)
    high_urgency = ['urgent', 'locked', 'immediate', 'funds', 'wire']
    if any(kw in keywords_str for kw in high_urgency):
        return 5
    
    # Medium-high urgency keywords (4)
    med_high_urgency = ['security', 'alert', 'unusual', 'login']
    if any(kw in keywords_str for kw in med_high_urgency):
        return 4
    
    # Medium urgency keywords (3)
    medium_urgency = ['refund', 'charged', 'money', 'double']
    if any(kw in keywords_str for kw in medium_urgency):
        return 3
    
    # Low urgency keywords (2)
    low_urgency = ['billing', 'question', 'cycle']
    if any(kw in keywords_str for kw in low_urgency):
        return 2
    
    # Very low urgency (1)
    very_low = ['suggestion', 'feature', 'dark mode']
    if any(kw in keywords_str for kw in very_low):
        return 1
    
    # Default medium urgency
    return 3

def parse_model_action(response_text: str) -> dict:
    """Parse model response into action dict"""
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
        # Extract priority if mentioned
        priority = 3
        for i in range(1, 6):
            if str(i) in response_lower:
                priority = i
        return {"action_type": "mark_urgent", "priority": priority}
    else:
        # Default to respond
        return {"action_type": "respond", "response_text": "Thank you for your message. We'll look into this."}

def run_episode(env, model_name: str, api_base_url: str, api_key: str, task_name: str = "easy"):
    """Run one episode and return trajectory"""
    client = OpenAI(
        base_url=api_base_url,
        api_key=api_key
    )
    
    observation = env.reset()
    trajectory = []
    done = False
    step = 0
    max_steps = 50
    
    while not done and step < max_steps:
        # Prepare prompt
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
                max_tokens=200
            )
            response = completion.choices[0].message.content or ""
        except Exception as e:
            print(f"  API Error: {e}")
            response = "respond with: I'm looking into your issue."
        
        action_dict = parse_model_action(response)
        action = Action(**action_dict)
        
        # Calculate urgency from keywords for trajectory
        urgency_score = get_urgency_from_keywords(observation.urgency_keywords)
        
        # Record step with proper urgency value
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
        
        # Print STEP in required format
        print(f"STEP {step}: {action.action_type}")
        
        step += 1
    
    return trajectory

def main():
    # Print START as required by competition format
    print("START")
    
    # Read environment variables
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    # Also check for Groq/OpenRouter keys as fallback
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if api_key:
            api_base_url = "https://api.groq.com/openai/v1"
            model_name = "llama-3.3-70b-versatile"
    
    if not api_key:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if api_key:
            api_base_url = "https://openrouter.ai/api/v1"
            model_name = "x-ai/grok-beta"
    
    if not api_key:
        print("\n❌ ERROR: No API key found!")
        print("\nPlease set one of these environment variables:")
        print("  OPENAI_API_KEY - for OpenAI")
        print("  GROQ_API_KEY - for Groq (free)")
        print("  OPENROUTER_API_KEY - for OpenRouter (free)")
        sys.exit(1)
    
    # Import grader
    from tasks.grader import run_grader
    
    env = EmailTriageEnv()
    scores = {}
    
    # Run each task type
    for task_name in ['easy', 'medium', 'hard']:
        # Reset environment for each task
        env.reset()
        
        # Run episode
        trajectory = run_episode(env, model_name, api_base_url, api_key, task_name)
        
        # Grade trajectory
        try:
            score = run_grader(task_name, trajectory)
            scores[task_name] = score
        except Exception as e:
            print(f"Grader error for {task_name}: {e}")
            scores[task_name] = 0.0
    
    # Calculate average score
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        scores['average'] = avg_score
        scores['model'] = model_name
        scores['provider'] = api_base_url
    
    # Save results
    with open('baseline_scores.json', 'w') as f:
        json.dump(scores, f, indent=2)
    
    # Print END as required by competition format
    print("END")

if __name__ == "__main__":
    main()