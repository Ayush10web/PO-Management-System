from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pymongo import MongoClient
from datetime import datetime
import random

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PO Management System - Delete Products & Vendors")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

client = MongoClient(os.getenv("MONGODB_URL"))
mongo_db = client["po_system"]
ai_logs = mongo_db["ai_descriptions"]
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    try:
        if db.query(models.Vendor).count() == 0:
            db.add_all([models.Vendor(name=n) for n in ["ABC Suppliers", "XYZ Traders", "Global Parts"]])
            db.commit()
        if db.query(models.Product).count() == 0:
            db.add_all([models.Product(name=n, sku=f"SKU-{i}", unit_price=p) 
                        for i, (n, p) in enumerate([("Laptop",45000), ("Mouse",800), ("Keyboard",1200), ("Monitor",15000)])])
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# ====================== ADD ======================
@app.post("/products")
def create_product(name: str, unit_price: float, sku: str = None, db: Session = Depends(get_db)):
    if sku is None: sku = f"SKU-{random.randint(10000,99999)}"
    product = models.Product(name=name, sku=sku, unit_price=unit_price)
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"message": f"✅ Product '{name}' added!", "id": product.id}

@app.post("/vendors")
def create_vendor(name: str, db: Session = Depends(get_db)):
    vendor = models.Vendor(name=name)
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return {"message": f"✅ Vendor '{name}' added!", "id": vendor.id}

# ====================== DELETE ======================
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": f"✅ Product ID {product_id} deleted successfully!"}

@app.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(vendor)
    db.commit()
    return {"message": f"✅ Vendor ID {vendor_id} deleted successfully!"}

# ====================== GET ======================
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/vendors")
def get_vendors(db: Session = Depends(get_db)):
    return db.query(models.Vendor).all()

@app.post("/purchase-orders/", response_model=schemas.PurchaseOrderResponse)
def create_po(po: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    total = crud.calculate_total(db, po.items)
    ref_no = f"PO-{datetime.date.today().year}-{random.randint(1000,9999)}"
    new_po = models.PurchaseOrder(reference_no=ref_no, vendor_id=po.vendor_id, total_amount=total, status="Draft")
    db.add(new_po)
    db.commit()
    db.refresh(new_po)
    return new_po

@app.get("/generate-desc")
def generate_desc(name: str):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Write a professional 2-sentence marketing description for product: {name}")
        desc = response.text.strip()
        ai_logs.insert_one({"product_name": name, "description": desc, "timestamp": datetime.utcnow()})
        return {"description": desc}
    except:
        return {"description": f"{name} is a premium quality product."}
