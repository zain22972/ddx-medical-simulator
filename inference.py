import os
import json
from typing import List, Optional
from openai import OpenAI

# Add src/ to path so local imports work correctly for clients
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from envs.ddx_env.client import DDxAction, DDxEnvClient

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"

BENCHMARK = "ddx-medical"
MAX_STEPS = 10
TEMPERATURE = 0.1
MAX_TOKENS = 150
SUCCESS_SCORE_THRESHOLD = 0.5  # normalized score in [0, 1]

SYSTEM_PROMPT = """You are a physician. Perform differential diagnosis via JSON actions only:
  {"type": "ask_symptom", "value": "<symptom>"}
  {"type": "order_test",   "value": "<test>"}
  {"type": "submit_diagnosis", "value": "<diagnosis>"}
Respond ONLY with valid JSON. No text, no markdown prefixes."""

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def build_user_prompt(step: int, obs) -> str:
    return f"Patient Observation:\nPrompt: {obs.prompt}\nChief Complaint: {obs.chief_complaint}\nSymptoms Known: {','.join(obs.symptoms_revealed)}\nTests Done: {','.join(obs.tests_done)}\nLast Result: {obs.last_result}\nStep: {step}\nSelect your next diagnostic action as JSON."

def get_model_action(client: OpenAI, step: int, obs) -> DDxAction:
    user_prompt = build_user_prompt(step, obs)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = completion.choices[0].message.content.strip()
        # Clean potential markdown
        text = text.replace("```json", "").replace("```", "").strip()
        
        parsed = json.loads(text)
        return DDxAction(type=parsed["type"], value=parsed["value"])
    except Exception as exc:
        print(f"[DEBUG] Model request failed or parsing failed: {exc}", flush=True)
        return DDxAction(type="ask_symptom", value="unknown")

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    # Set directly to your live Hugging Face deployment
    env_url = os.getenv("DDX_ENV_URL", "https://niaz9246-ddx-env.hf.space")
    env = DDxEnvClient(base_url=env_url)

    tasks = [1, 2, 3]
    for task_id in tasks:
        task_name = f"ddx-task-{task_id}"
        log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)
        
        rewards: List[float] = []
        steps_taken = 0
        score = 0.0
        success = False
        
        try:
            result = env.reset(task_id=task_id)
            if not result or not result.observation:
                 print("[DEBUG] Could not reset environment API.", flush=True)
                 continue
                 
            obs = result.observation
            
            for step in range(1, MAX_STEPS + 1):
                if result.done:
                    break
                    
                action = get_model_action(client, step, obs)
                
                # Format action string for stdout log
                action_str = f"{action.type}('{action.value}')"
                
                result = env.step(action)
                obs = result.observation
                
                reward = result.reward or 0.0
                done = result.done
                error = None
                
                rewards.append(reward)
                steps_taken = step
                
                log_step(step=step, action=action_str, reward=reward, done=done, error=error)
                
                if done:
                    break
                    
            # Calculate final score and firmly CLAMP it to [0.0, 1.0] for exact grad criteria
            score = sum(rewards)
            score = min(max(score, 0.0), 1.0)
            success = score >= SUCCESS_SCORE_THRESHOLD
            
        except Exception as e:
            print(f"[DEBUG] env error: {e}", flush=True)
            
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    main()
