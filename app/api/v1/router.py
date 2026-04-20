from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, notes, tags

api_router = APIRouter()


@api_router.get("/", tags=["System"])
async def get_api_v1_root():
    return {"version": "1.0", "docs": "/docs", "status": "running"}


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
