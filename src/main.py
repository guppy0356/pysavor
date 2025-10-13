from fastapi import FastAPI

from src.api.routers import user
from src.api.routers import auth

app = FastAPI(title="pysavor")

app.include_router(user.router, prefix="/api/v1/users")
app.include_router(auth.router, prefix="/api/v1/auth")


@app.get("/")
def read_root():
    return {"message": "The architect is in the building."}

