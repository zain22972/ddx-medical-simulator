import requests
from pydantic import BaseModel
from typing import List, Optional, Any

class DDxAction(BaseModel):
    type: str
    value: str

class DDxObservation(BaseModel):
    done: bool
    reward: Optional[float]
    chief_complaint: str
    symptoms_revealed: List[str]
    tests_done: List[str]
    last_result: str
    step_count: int
    steps_remaining: int
    prompt: str

class StepResult(BaseModel):
    observation: DDxObservation
    reward: float
    done: bool

class DDxEnvClient:
    def __init__(self, base_url="http://localhost:7860"):
        self.base_url = base_url.rstrip("/")

    def _parse(self, p):
        # We need to make sure 'reward' handles objects or lists in parsed json gracefully or fallback
        if "reward" in p and p["reward"] is None:
            p["reward"] = 0.0
        obs = DDxObservation(**p)
        return StepResult(observation=obs, reward=float(p.get("reward") or 0.0), done=p.get("done", False))

    def reset(self, task_id: Optional[int] = None):
        payload = {"task_id": task_id} if task_id is not None else {}
        return self._parse(requests.post(self.base_url + "/reset", json=payload).json())

    def step(self, action: DDxAction):
        return self._parse(requests.post(self.base_url + "/step", json=action.dict()).json())

    def health(self):
        try:
            return requests.get(self.base_url + "/health").json().get("status") == "healthy"
        except Exception:
            return False
