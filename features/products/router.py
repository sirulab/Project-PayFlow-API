from fastapi import APIRouter, Depends
from sqlmodel import Session, select    
from core.database import get_session   
from .models import Product             

router = APIRouter(tags=["Products"])

@router.get("/products/")
async def get_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return {"products": products}

@router.post("/products/")
def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product