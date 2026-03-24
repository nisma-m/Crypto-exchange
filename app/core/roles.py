from fastapi import Depends, HTTPException, status
from app.core.jwt import get_current_admin
from jose import jwt, JWTError
from app.core.jwt import oauth2_scheme
from app.core.security import SECRET_KEY, ALGORITHM


def require_role(allowed_roles: list):
    def wrapper(current_admin: dict = Depends(get_current_admin)):
        if current_admin.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_admin
    return wrapper

def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: str = payload.get("sub")
        role: str = payload.get("role")
        if admin_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"admin_id": admin_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token error")

def role_required(required_role: str):
    def wrapper(current_admin: dict = Depends(get_current_admin)):
        if current_admin["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        return current_admin
    return wrapper
