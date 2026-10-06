from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
import uuid
import asyncio
from typing import Dict, Any, List

from .websocket import event_bus
from ..models import TaskCreate, TaskStatus, AgentEvent, TaskState
from ..database import db

router = APIRouter()

@router.post("/repositories/analyze")
async def analyze_repository(repo_url: str, branch: str = "main"):
    repo_id = str(uuid.uuid4())
    return {"repo_id": repo_id, "status": "analyzed"}

@router.post("/tasks", response_model=TaskStatus)
async def create_task(task_in: TaskCreate):
    task_id = str(uuid.uuid4())
    db.create_task(task_id, task_in.repo_url, task_in.issue_description)
    task_data = db.get_task(task_id)
    return TaskStatus(**task_data)

async def mock_agent_workflow(task_id: str):
    db.update_task_state(task_id, TaskState.ANALYZING.value, 10.0, "Analyzing repository...")
    await event_bus.publish(task_id, AgentEvent(type="state_change", data={"state": "analyzing"}))
    await asyncio.sleep(2)
    db.update_task_state(task_id, TaskState.COMPLETED.value, 100.0, "Task completed successfully.")
    await event_bus.publish(task_id, AgentEvent(type="state_change", data={"state": "completed"}))

@router.post("/tasks/{task_id}/run")
async def run_task(task_id: str, background_tasks: BackgroundTasks):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    background_tasks.add_task(mock_agent_workflow, task_id)
    return {"message": "Task started"}

@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatus(**task)

@router.get("/tasks/{task_id}/events")
async def get_task_events(task_id: str):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    async def event_generator():
        queue = event_bus.subscribe(task_id)
        try:
            while True:
                data = await queue.get()
                yield f"data: {data}\n\n"
        except asyncio.CancelledError:
            event_bus.unsubscribe(task_id, queue)
            raise
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/tasks/{task_id}/diff")
async def get_task_diff(task_id: str):
    return {"diff": "--- a/file.py\n+++ b/file.py\n@@ -1,1 +1,1 @@\n-old\n+new"}

@router.get("/tasks/{task_id}/tests")
async def get_task_tests(task_id: str):
    return {"tests": []}

@router.get("/tasks/{task_id}/evidence")
async def get_task_evidence(task_id: str):
    return {"evidence": []}

@router.get("/tasks/{task_id}/impact")
async def get_task_impact(task_id: str):
    return {"impact_radius": []}

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/repositories/{repo_id}/graph")
async def get_repo_graph(repo_id: str):
    return {"nodes": [], "edges": []}

@router.get("/repositories/{repo_id}/files")
async def get_repo_files(repo_id: str):
    return {"files": []}
