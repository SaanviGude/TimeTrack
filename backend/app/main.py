from fastapi import FastAPI
from .database import Base, engine
from .routes import auth, user, workspace, project, task, time_entry

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TimeTrack API", description="A time tracking application API")

# Authentication routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User management routes
app.include_router(user.router, prefix="/users", tags=["Users"])

# Workspace management routes
app.include_router(workspace.router, prefix="/workspaces", tags=["Workspaces"])

# Project management routes
app.include_router(project.router, prefix="/projects", tags=["Projects"])

# Task management routes
app.include_router(task.router, prefix="/tasks", tags=["Tasks"])

# Time tracking routes
app.include_router(time_entry.router, prefix="/time-entries", tags=["Time Tracking"])
