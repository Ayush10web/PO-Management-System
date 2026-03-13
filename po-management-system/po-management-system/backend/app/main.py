from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import datetime
import random

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PO Management System")

# === CORS FIX ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === AUTO SEED SAMPLE DATA (no more curl needed) ===
@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    try:
        if db.query(models.Vendor).count() == 0:
            db.add(models.Vendor(name="ABC Suppliers"))
            db.add(models.Vendor(name="XYZ Traders"))
            db.add(models.Vendor(name="Global Parts"))
            db.commit()

        if db.query(models.Product).count() == 0:
            db.add(models.Product(name="Laptop", sku="SKU-1001", unit_price=45000))
            db.add(models.Product(name="Mouse", sku="SKU-1002", unit_price=800))
            db.add(models.Product(name="Keyboard", sku="SKU-1003", unit_price=1200))
            db.add(models.Product(name="Monitor", sku="SKU-1004", unit_price=15000))
            db.commit()
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "✅ Backend is LIVE!"}

@app.get("/vendors")
def get_vendors(db: Session = Depends(get_db)):
    return db.query(models.Vendor).all()

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/generate-desc")
def generate_desc(name: str):
    return {"description": f"{name} is a premium quality product designed for reliability and performance. Ideal for businesses looking for durability and value in every purchase."}

@app.post("/purchase-orders/", response_model=schemas.PurchaseOrderResponse)
def create_po(po: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    total = crud.calculate_total(db, po.items)
    ref_no = f"PO-{datetime.date.today().year}-{random.randint(1000,9999)}"
    new_po = models.PurchaseOrder(
        reference_no=ref_no,
        vendor_id=po.vendor_id,
        total_amount=total,
        status="Draft"
    )
    db.add(new_po)
    db.commit()
    db.refresh(new_po)
    return new_po
