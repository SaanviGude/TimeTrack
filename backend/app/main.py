from fastapi import FastAPI
from .database import Base, engine
from .routes import user, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TimeTrack API", description="A time tracking application API")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["Users"])
