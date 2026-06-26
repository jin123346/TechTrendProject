from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.routers import pipeline_requests, pipeline_runs
from app.domain.exceptions import PipelineError


app = FastAPI(title="Tech Trend Pipeline", version="0.1.0")
app.include_router(pipeline_requests.router)
app.include_router(pipeline_runs.router)


@app.exception_handler(PipelineError)
def handle_pipeline_error(_request: Request, exc: PipelineError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": str(exc)},
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
