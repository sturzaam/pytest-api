from fastapi import FastAPI
from pydantic import BaseModel

from pytest_api import ASGIMiddleware

app = FastAPI()
spec = ASGIMiddleware

app.add_middleware(spec)

app.openapi = spec.openapi_behaviors(app)


@app.get("/")
def default_route():
    return {"message": "OK"}


@app.get("/health-check/")
def health_check():
    return {"message": "OK"}


class Behavior(BaseModel):
    name: str


@app.post("/behavior-example/")
async def example_body(behavior: Behavior):
    return {"message": "OK"}
