import os
from fastapi import FastAPI
import gradio as gr
from typing import Optional
from pydantic import BaseModel
from .environment import DDxEnvironment
from .ui import build_ui

task_id = int(os.environ.get("DDX_TASK_ID", "1"))
env = DDxEnvironment(task_id=task_id)
app = FastAPI(title="DDx RL Environment", version="0.1.0")

class ActionRequest(BaseModel):
    type: str
    value: str

class ResetRequest(BaseModel):
    task_id: Optional[int] = None

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset(req: ResetRequest = None):
    global env
    if req and req.task_id is not None:
        env = DDxEnvironment(task_id=req.task_id)
    return env.reset()

@app.post("/step")
def step(action: ActionRequest):
    return env.step(action.type, action.value)

@app.get("/state")
def state():
    return env.state()

ui = build_ui(env)
app = gr.mount_gradio_app(app, ui, path="/")
