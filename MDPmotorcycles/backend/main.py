from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import auth_router
from backend.motos import motos_router
from backend.accesorios import accesorios_router
from backend.cart import cart_router
from backend.scraping import scrape_and_store_motos

app = FastAPI(title="MDPmotorcycles API")

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(motos_router, prefix="/motos", tags=["motos"])
app.include_router(accesorios_router, prefix="/accesorios", tags=["accesorios"])
app.include_router(cart_router, prefix="/cart", tags=["cart"])

@app.get("/")
async def root():
    return {"message": "Welcome to MDPmotorcycles API"}

@app.get("/scrape")
async def scrape_catalog():
    try:
        scrape_and_store_motos(headless=True)
        return {"message": "Scraping completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
