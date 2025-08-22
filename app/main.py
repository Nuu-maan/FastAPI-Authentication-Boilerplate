from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.sessions import router as sessions_router

app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(sessions_router)
