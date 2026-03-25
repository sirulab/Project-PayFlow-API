from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from core.database import get_session
from .models import Product

router = APIRouter(tags=["Products"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def index(request: Request, session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return templates.TemplateResponse("index.html", {"request": request, "products": products})

@router.post("/products/")
def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product