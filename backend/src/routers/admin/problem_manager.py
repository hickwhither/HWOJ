import os
import zipfile
import shutil

from fastapi import APIRouter, Request, HTTPException, UploadFile, Path, Depends
from pydantic import BaseModel
from sqlmodel import select

router = APIRouter(prefix="/admin/problem", tags=["admin.problem_manager"])

os.makedirs(os.getenv('PROBLEMS_DIR'), exist_ok=True)

# -- MODELS --
from src import SessionDep, User, Problem
from src.database_public import ProblemPublic, ProblemCreate

def verify_access(
    request: Request, 
    session: SessionDep
) -> User:
    auth_data = request.session.get("auth")
    if not auth_data or "username" not in auth_data:
        raise HTTPException(401, "Not authenticated")
        
    username = auth_data["username"]
    user = session.get(User, username)
    if not user: 
        raise HTTPException(404, "User not found")

    if not user.superuser:
        if "admin.problem_manager" not in user.permissions:
            raise HTTPException(403, "You do not have permission to manage problems.")
            
    return user


# -- ROUTERS --
@router.post("/create", response_model=ProblemPublic)
@router.post("/edit/{problem_code}", response_model=ProblemPublic)
def create_problem(
    problem: ProblemCreate,
    problem_code: str, 
    session: SessionDep, 
    current_user: User = Depends(verify_access)
):
    if problem_code:
        db_problem = session.get(Problem, db_problem.code)
    problem_data = problem.model_dump()
    db_problem = Problem.model_validate(problem_data)
    db_problem.authors.append(current_user)
    if session.get(Problem, db_problem.code):
        raise HTTPException(400, "Problem exists")
    
    session.add(db_problem)
    session.commit()
    session.refresh(db_problem)
    return db_problem


@router.post("/{problem_code}/zip")
def problem_upload_zip(
    problem_code: str, 
    upload: UploadFile,
    current_user: User = Depends(verify_access)
):
    if not upload.filename.endswith('.zip'):
        raise HTTPException(400, "Only ZIP files are allowed.")
    target_dir = os.path.join(os.getenv('PROBLEMS_DIR'), problem_code)
    os.makedirs(target_dir, exist_ok=True)
    temp_zip_path = os.path.join(target_dir, f"temp_{problem_code}.zip")
    
    try:
        with open(temp_zip_path, "wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                # os.path.abspath sẽ làm sạch các đường dẫn dạng '../../'
                # Đảm bảo file giải nén ra PHẢI nằm HOÀN TOÀN bên trong target_dir
                target_path = os.path.abspath(os.path.join(target_dir, member))
                if not target_path.startswith(os.path.abspath(target_dir)):
                    raise HTTPException(400, f"Malicious file path detected in ZIP: {member}")

            # Trước khi giải nén mới, bạn có thể cân nhắc xóa sạch thư mục cũ để tránh file rác tồn đọng
            # shutil.rmtree(target_dir); os.makedirs(target_dir, exist_ok=True)
            zip_ref.extractall(target_dir)

    except zipfile.BadZipFile:
        raise HTTPException(400, "Invalid or corrupted ZIP file.")
    finally:
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)  
    return


@router.delete("/{problem_code}/zip")
def problem_clear_files(
    problem_code: str, 
    current_user: User = Depends(verify_access)
):
    target_dir = os.path.join(os.getenv('PROBLEMS_DIR'), problem_code)
    if not os.path.exists(target_dir):
        raise HTTPException(404, "Problem directory not exists.")
    try:
        shutil.rmtree(target_dir)
        os.makedirs(target_dir, exist_ok=True)
    except Exception as e:
        raise HTTPException(500, f"Failed to clear files: {str(e)}")
    return