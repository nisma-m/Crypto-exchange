from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.admin import AdminCreate
from app.services.admin_auth_service import create_admin, login_admin

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])

@router.post("/create")
async def create_admin_route(admin: AdminCreate):
    result = await create_admin(admin)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/login")
async def login_admin_route(form_data: OAuth2PasswordRequestForm = Depends()):
    token = await login_admin(form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return {"access_token": token, "token_type": "bearer"}