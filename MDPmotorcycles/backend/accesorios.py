from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas
from backend.database import get_db

accesorios_router = APIRouter()

@accesorios_router.get("/", response_model=List[schemas.AccesorioOut])
def get_accesorios(db: Session = Depends(get_db)):
    accesorios = db.query(models.Accesorio).all()
    return accesorios

@accesorios_router.post("/", response_model=schemas.AccesorioOut, status_code=status.HTTP_201_CREATED)
def create_accesorio(accesorio: schemas.AccesorioCreate, db: Session = Depends(get_db)):
    db_accesorio = models.Accesorio(
        nombre=accesorio.nombre,
        precio=accesorio.precio,
        descripcion=accesorio.descripcion,
        img_url=accesorio.img_url
    )
    db.add(db_accesorio)
    db.commit()
    db.refresh(db_accesorio)
    return db_accesorio
