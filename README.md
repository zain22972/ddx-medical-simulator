---
title: DDx RL Environment
emoji: 🏥
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
tags: [openenv, reinforcement-learning, medical, differential-diagnosis]
---

# 🏥 DDx-Env: Medical Differential Diagnosis Environment

**DDx-Env** is an interactive, fully [OpenEnv](https://github.com/openenv)-compliant reinforcement learning environment that simulates a highly complex real-world task: **Medical Differential Diagnosis**. 

Instead of toy games or simple web-clicking, agents placed in this environment must actively interview a "patient", order specific laboratory tests/imaging, interpret clinical results, and definitively diagnose the underlying condition before the step limit expires.

---

## 🎯 Functional Hackathon Compliance

This project was built from the ground up to meet all strict evaluation constraints:

### 1. Real-World Task Simulation
Algorithms and AI models today struggle with multi-step logical deduction. This environment forces agents to simulate the role of a physician doing triage and diagnosis (clinical reasoning), which is a critical, high-value real-world task.

### 2. OpenEnv Spec Compliance
- **Typed Models:** Exposes strictly typed Pydantic models (`DDxObservation`, `DDxAction`, `StepResult`) ensuring predictable parsing.
- **Protocol Endpoints:** Standardized `/reset`, `/step`, and `/state` REST API routes exposed via Python FastAPI.
- Validated via `openenv validate`.

### 3. Programmatic Graders (3+ Tasks)
The environment dynamically loads distinct clinical scenarios. A rigid Python grader maps the AI's fuzzy LLM outputs to the internal state logic to evaluate performance. The tasks scale in difficulty:
* **Task 1 (Easy):** STEMI (Myocardial Infarction)
* **Task 2 (Medium):** Pulmonary Embolism (PE) 
* **Task 3 (Hard):** Addison's Disease (Primary Adrenal Insufficiency)

### 4. Meaningful Reward Function
Sparse 1.0 / 0.0 rewards are difficult for RL to learn from. Our reward function is dense and actively tracks the full trajectory:
* **Progress Rewards:** `+0.10` for successfully uncovering a relevant symptom.
* **Investigation Rewards:** `+0.15` for correctly ordering an available diagnostic test.
* **Undesirable Behavior Penalty:** `-0.05` applied to *every single step taken*, mathematically heavily penalizing infinite loops, guessing, and wasting time.
* **Final Thresholding:** The final grading metric safely strictly bounds the cumulative episode sum to the `[0.0, 1.0]` range.

---

## 💻 Baseline Inference Script `inference.py`

Located in the root directory, `inference.py` serves as the mandatory automated validation script. It initializes an OpenAI-compatible client, iterates through Tasks 1, 2, and 3, and emits strict `[START]`, `[STEP]`, and `[END]` evaluation logs formatted to exactly 2 decimal places.

**To run the validation on the deployed Hub server:**
```bash
# Provide your Hugging Face or OpenAI token
export HF_TOKEN="hf_your_token_here"

# (Optional) Override the default model
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"

# Run the strict baseline tests
python inference.py
```

---

## 🎨 Interactive Evaluation UI (Gradio)

While automated agents interact with the FastAPI `/docs` specification, human evaluators can manually play through the environment to verify grading logic!

A **Gradio** web UI is mounted directly onto the `root (/)` of this Space. 
1. Click **Reset Episode**.
2. Select an Action Type (e.g. `ask_symptom`).
3. Enter an Action Value (e.g. `shortness of breath`) and hit **Step (Submit Action)**!
