import uuid
from .cases import TASKS

MAX_STEPS = 10

class DDxEnvironment:
    def __init__(self, task_id=1):
        self.task_id = task_id
        self.task = TASKS[task_id]
        self._episode_id = None
        self._symptoms_revealed = []
        self._tests_done = []
        self._step_count = 0
        self._done = False

    def reset(self):
        self.task = TASKS[self.task_id]
        self._episode_id = str(uuid.uuid4())[:8]
        self._symptoms_revealed = [self.task["chief_complaint"]]
        self._tests_done = []
        self._step_count = 0
        self._done = False
        return self._build_obs(None, "")

    def step(self, action_type, action_value):
        if self._done:
            return self._build_obs(0.0, "Episode already done.")
        self._step_count += 1
        reward = -0.05
        last_result = ""
        key = action_value.lower().strip()
        if action_type == "ask_symptom":
            matches = [v for k, v in self.task["symptoms"].items() if len(key) > 2 and (key in k or k in key or key in v.lower())]
            if matches:
                if matches[0] not in self._symptoms_revealed:
                    self._symptoms_revealed.append(matches[0])
                    reward += 0.10
                last_result = matches[0]
            else:
                last_result = "No finding."
        elif action_type == "order_test":
            matches = [v for k, v in self.task["tests"].items() if len(key) > 2 and (key in k or k in key or key in v.lower())]
            if matches:
                if matches[0] not in self._tests_done:
                    self._tests_done.append(matches[0])
                    reward += 0.15
                last_result = matches[0]
            else:
                last_result = "Test not available."
        elif action_type == "submit_diagnosis":
            clean = action_value.strip().lower()
            valid = [self.task["diagnosis"]] + self.task.get("aliases", [])
            if any(clean == v.lower() for v in valid):
                reward = round(0.8 + 0.2 * (1 - self._step_count / MAX_STEPS), 3)
            else:
                reward = 0.0
            last_result = "Submitted: " + action_value
            self._done = True
        if self._step_count >= MAX_STEPS:
            self._done = True
        return self._build_obs(round(reward, 3), last_result)

    def state(self):
        return {
            "episode_id": self._episode_id,
            "step_count": self._step_count,
            "task_id": self.task_id,
            "task_difficulty": self.task["difficulty"],
        }

    def _build_obs(self, reward, last_result):
        lines = ["Chief complaint: " + self.task["chief_complaint"], "Symptoms known:"]
        for s in self._symptoms_revealed:
            lines.append("  - " + s)
        if self._tests_done:
            lines.append("Tests done:")
            for t in self._tests_done:
                lines.append("  - " + t)
        if last_result:
            lines.append("Last result: " + last_result)
        lines.append("Step " + str(self._step_count) + "/" + str(MAX_STEPS))
        return {
            "done": self._done,
            "reward": reward,
            "chief_complaint": self.task["chief_complaint"],
            "symptoms_revealed": list(self._symptoms_revealed),
            "tests_done": list(self._tests_done),
            "last_result": last_result,
            "step_count": self._step_count,
            "steps_remaining": MAX_STEPS - self._step_count,
            "prompt": "\n".join(lines),
        }
