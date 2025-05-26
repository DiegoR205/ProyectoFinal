from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas
from backend.database import get_db
from backend.auth import verify_password, get_password_hash  # For role check, import auth dependencies
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Header

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

motos_router = APIRouter()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def admin_required(user: models.Usuario = Depends(get_current_user)):
    if user.rol != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

@motos_router.get("/", response_model=List[schemas.MotoOut])
def get_motos(db: Session = Depends(get_db)):
    motos = db.query(models.Moto).all()
    return motos

@motos_router.post("/", response_model=schemas.MotoOut, status_code=201)
def create_moto(moto: schemas.MotoCreate, db: Session = Depends(get_db), user: models.Usuario = Depends(admin_required)):
    new_moto = models.Moto(
        nombre=moto.nombre,
        marca=moto.marca,
        precio=moto.precio,
        img_url=moto.img_url
    )
    db.add(new_moto)
    db.commit()
    db.refresh(new_moto)
    return new_moto
