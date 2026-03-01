from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import ADMIN_SECRET

api_key_header = APIKeyHeader(name="X-Admin-Token", auto_error=True)

def verify_admin(api_key_header: str = Security(api_key_header)):
    if api_key_header != ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate admin credentials",
        )
    return True
