from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bootstrap import BootstrapState, initialize_database
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bootstrap = initialize_database(settings.database_path)
    yield


app = FastAPI(lifespan=lifespan)


def _get_bootstrap_state() -> BootstrapState:
    bootstrap = getattr(app.state, "bootstrap", None)
    if isinstance(bootstrap, BootstrapState):
        return bootstrap
    return BootstrapState(
        database_path=settings.database_path,
        initialized=False,
    )


@app.get("/api/health")
def health() -> dict[str, object]:
    bootstrap = _get_bootstrap_state()
    status = "ok" if bootstrap.initialized else "starting"
    return {
        "status": status,
        "database_path": settings.database_path_label,
        "initialized": bootstrap.initialized,
    }
