from fastapi import FastAPI

from src.api.routers import user

app = FastAPI(title="pysavor")

app.include_router(user.router, prefix="/api/v1/users")


@app.get("/")
def read_root():
    return {"message": "The architect is in the building."}

