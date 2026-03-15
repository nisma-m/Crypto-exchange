from fastapi import Depends, HTTPException, status
from app.core.jwt import get_current_admin

def require_role(allowed_roles: list):
    def wrapper(current_admin: dict = Depends(get_current_admin)):
        if current_admin.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_admin
    return wrapper