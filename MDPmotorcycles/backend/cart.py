from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas
from backend.database import get_db
from backend.auth import oauth2_scheme, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

cart_router = APIRouter()

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

@cart_router.get("/", response_model=List[schemas.CarritoItemOut])
def get_cart(user: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(models.Carrito).filter(models.Carrito.id_usuario == user.id).all()
    cart_items = []
    for item in items:
        if item.tipo_producto == "moto":
            product = db.query(models.Moto).filter(models.Moto.id == item.id_producto).first()
            if product:
                cart_items.append(schemas.CarritoItemOut(
                    id=item.id,
                    id_usuario=item.id_usuario,
                    id_producto=item.id_producto,
                    tipo_producto=item.tipo_producto,
                    cantidad=item.cantidad,
                    nombre=product.nombre,
                    precio=product.precio,
                    descripcion=None,
                    img_url=product.img_url
                ))
        elif item.tipo_producto == "accesorio":
            product = db.query(models.Accesorio).filter(models.Accesorio.id == item.id_producto).first()
            if product:
                cart_items.append(schemas.CarritoItemOut(
                    id=item.id,
                    id_usuario=item.id_usuario,
                    id_producto=item.id_producto,
                    tipo_producto=item.tipo_producto,
                    cantidad=item.cantidad,
                    nombre=product.nombre,
                    precio=product.precio,
                    descripcion=product.descripcion,
                    img_url=product.img_url
                ))
    return cart_items

@cart_router.post("/add", response_model=schemas.CarritoOut, status_code=201)
def add_to_cart(item: schemas.CarritoCreate, user: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    new_item = models.Carrito(
        id_usuario=user.id,
        id_producto=item.id_producto,
        tipo_producto=item.tipo_producto,
        cantidad=item.cantidad
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@cart_router.delete("/remove/{item_id}", status_code=204)
def remove_from_cart(item_id: int, user: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(models.Carrito).filter(models.Carrito.id == item_id, models.Carrito.id_usuario == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    db.delete(item)
    db.commit()
    return
