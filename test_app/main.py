from pprint import pprint
from fastapi import FastAPI
from pytest_api import SpecificationMiddleware

app = FastAPI()
spec = SpecificationMiddleware

app.add_middleware(spec)

app.openapi = SpecificationMiddleware.get_openapi_behaviors(app)

@app.get("/")
def default_route():
    return {"message": "OK"}


@app.get("/health-check/")
def health_check():
    return {"message": "OK"}
