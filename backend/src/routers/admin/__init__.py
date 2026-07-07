from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException, status
from src import SessionDep, User

def verify_admin_staff(request: Request, session: SessionDep) -> User:
    auth_data = request.session.get("auth")
    if not auth_data or "username" not in auth_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    username = auth_data["username"]
    user = session.get(User, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    if not user.staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have permission to access this resource"
        )
    # Trả về object user nếu muốn dùng ở các endpoint sâu hơn
    return user

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verify_admin_staff)])

from .problemsetter import router as problem_router
router.include_router(problem_router)