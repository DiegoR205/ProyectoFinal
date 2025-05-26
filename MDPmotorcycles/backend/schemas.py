from pydantic import BaseModel, EmailStr
from typing import Optional

# User schemas
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioOut(UsuarioBase):
    id: int
    rol: str

    class Config:
        orm_mode = True

# Moto schemas
class MotoBase(BaseModel):
    nombre: str
    marca: str
    precio: float
    img_url: Optional[str] = None

class MotoCreate(MotoBase):
    pass

class MotoOut(MotoBase):
    id: int

    class Config:
        orm_mode = True

# Accesorio schemas
class AccesorioBase(BaseModel):
    nombre: str
    precio: float
    descripcion: Optional[str] = None
    img_url: Optional[str] = None

class AccesorioCreate(AccesorioBase):
    pass

class AccesorioOut(AccesorioBase):
    id: int

    class Config:
        orm_mode = True

# Carrito schemas
class CarritoBase(BaseModel):
    id_producto: int
    tipo_producto: str  # 'moto' or 'accesorio'
    cantidad: int = 1

class CarritoCreate(CarritoBase):
    pass

class CarritoOut(CarritoBase):
    id: int
    id_usuario: int

    class Config:
        orm_mode = True

class CarritoItemOut(BaseModel):
    id: int
    id_usuario: int
    id_producto: int
    tipo_producto: str
    cantidad: int
    nombre: str
    precio: float
    descripcion: str = None
    img_url: str = None

    class Config:
        orm_mode = True
