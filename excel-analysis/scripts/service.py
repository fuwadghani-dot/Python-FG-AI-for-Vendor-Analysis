"""Start a lightweight FastAPI service that schedules recurring runs with APScheduler.

Endpoints:
 - POST /run  -> trigger a run immediately (body: {"workbook": "path"})
 - POST /schedule -> schedule recurring runs (body: {"workbook":"path","cron":"*/10 * * * *"} or interval minutes)
 - GET /status -> return last run status
 - GET /jobs -> list scheduled jobs
"""
from __future__ import annotations
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from excel_analysis.runner import ReportRunner, read_status
from excel_analysis import config
import logging

app = FastAPI()
log = logging.getLogger("uvicorn")
scheduler = BackgroundScheduler()
runner = ReportRunner()


import os

def _verify_token(authorization: Optional[str] = Header(None)) -> bool:
    """Verify incoming Authorization header against SERVICE_TOKEN when set.

    Reads SERVICE_TOKEN from environment at call time so tests can set it dynamically.
    """
    svc = os.getenv("SERVICE_TOKEN")
    if not svc:
        return True
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    if token != svc:
        raise HTTPException(status_code=403, detail="Invalid token")
    return True

class RunRequest(BaseModel):
    workbook: str

class ScheduleRequest(BaseModel):
    workbook: str
    minutes: Optional[int] = None
    cron: Optional[str] = None  # simple cron expression like '*/10 * * * *'

@app.on_event("startup")
def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        log.info("Scheduler started")

@app.on_event("shutdown")
def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        log.info("Scheduler shutdown")

@app.post("/run")
def run_once(req: RunRequest, _auth: bool = Depends(_verify_token)):
    try:
        out = runner.run_once(req.workbook)
        return {"status": "ok", "report": str(out)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule")
def schedule(req: ScheduleRequest, _auth: bool = Depends(_verify_token)):
    if req.minutes is None and req.cron is None:
        raise HTTPException(status_code=400, detail="Provide minutes or cron")

    job_id = f"report_{len(scheduler.get_jobs()) + 1}"
    if req.minutes is not None:
        trigger = IntervalTrigger(minutes=req.minutes)
    else:
        try:
            # very simple cron split (minute hour dom month dow)
            parts = req.cron.split()
            trigger = CronTrigger.from_crontab(req.cron)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid cron: {e}")

    scheduler.add_job(lambda: runner.run_once(req.workbook), trigger, id=job_id, replace_existing=True)
    return {"status": "scheduled", "job_id": job_id}

@app.get("/status")
def status():
    return read_status()

@app.get("/jobs")
def jobs():
    return {"jobs": [j.id for j in scheduler.get_jobs()]}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
