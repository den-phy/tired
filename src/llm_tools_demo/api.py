import logging
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from llm_tools_demo.database import get_db
from llm_tools_demo.repository import TodoRepository

DatabaseSession = Annotated[Session, Depends(get_db)]


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str
    details: list[dict[str, object]] | None = None


class TodoCreate(BaseModel):
    title: str


class TodoRead(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = ConfigDict(from_attributes=True)


app = FastAPI(title="LLM Todo API")


@app.exception_handler(Exception)
async def handle_unexpected_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = request.state.request_id
    elapsed_ms = (perf_counter() - request.state.started_at) * 1000

    logger.error(
        "request_id=%s method=%s path=%s status_code=500 elapsed_ms=%.2f error=%s",
        request_id,
        request.method,
        request.url.path,
        elapsed_ms,
        type(exc).__name__,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    error = ErrorResponse(
        code="internal_server_error",
        message="服务器内部错误",
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error.model_dump(exclude_none=True),
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    error_codes = {
        status.HTTP_400_BAD_REQUEST: "bad_request",
        status.HTTP_404_NOT_FOUND: "not_found",
    }

    error = ErrorResponse(
        code=error_codes.get(exc.status_code, "http_error"),
        message=str(exc.detail),
        request_id=request.state.request_id,
    )

    return JSONResponse(status_code=exc.status_code, content=error.model_dump(exclude_none=True))


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    error = ErrorResponse(
        code="validation_error",
        message="请求参数校验失败",
        request_id=request.state.request_id,
        details=exc.errors(),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error.model_dump(exclude_none=True),
    )


logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_request(
    request: Request,
    call_next,
) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    started_at = perf_counter()
    request.state.started_at = started_at
    response = await call_next(request)

    elapsed_ms = (perf_counter() - started_at) * 1000
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_id=%s method=%s path=%s status_code=%s elapsed_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )

    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/todos")
def list_todos(session: DatabaseSession) -> list[TodoRead]:
    repository = TodoRepository(session)
    return repository.list_all()


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(
    data: TodoCreate,
    session: DatabaseSession,
) -> TodoRead:
    repository = TodoRepository(session)
    try:
        todo_model = repository.add(data.title)
        return TodoRead.model_validate(todo_model)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.patch("/todos/{todo_id}/complete")
def complete_todo(todo_id: int, session: DatabaseSession) -> TodoRead:
    repository = TodoRepository(session)
    try:
        todo_model = repository.complete(todo_id)
        return TodoRead.model_validate(todo_model)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: DatabaseSession) -> None:
    repository = TodoRepository(session)
    try:
        return repository.delete(todo_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get("/db-health")
def database_health(session: DatabaseSession) -> dict[str, str]:
    database_name = session.execute(text("SELECT current_database()")).scalar_one()

    return {"database": database_name}
