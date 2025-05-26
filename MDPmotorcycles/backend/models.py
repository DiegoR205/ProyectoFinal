from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hashed = Column(String(255), nullable=False)
    rol = Column(String(20), default="usuario")  # usuario or admin

    carrito_items = relationship("Carrito", back_populates="usuario")

class Moto(Base):
    __tablename__ = "motos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    marca = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    img_url = Column(String(255), nullable=True)

class Accesorio(Base):
    __tablename__ = "accesorios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    descripcion = Column(String(255), nullable=True)
    img_url = Column(String(255), nullable=True)

class Carrito(Base):
    __tablename__ = "carrito"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_producto = Column(Integer, nullable=False)
    tipo_producto = Column(String(20), nullable=False)  # 'moto' or 'accesorio'
    cantidad = Column(Integer, default=1, nullable=False)

    usuario = relationship("Usuario", back_populates="carrito_items")
