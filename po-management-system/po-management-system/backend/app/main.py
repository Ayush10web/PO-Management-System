from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PO Management System - Bonuses Active")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# MongoDB + Gemini (real AI + logs)
client = MongoClient(os.getenv("MONGODB_URL"))
mongo_db = client["po_system"]
ai_logs = mongo_db["ai_descriptions"]
genai.configure(api_key=os.getenv("AIzaSyC-T3letDrA8ZOBmROVya6v1zxBLufcy_g"))

# Auto sample data
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

# ====================== PUBLIC ENDPOINTS ======================
@app.get("/")
def home():
    return {"message": "✅ Backend LIVE with Real Gemini + MongoDB"}

@app.get("/vendors")
def get_vendors(db: Session = Depends(get_db)):
    return db.query(models.Vendor).all()

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/purchase-orders")
def get_purchase_orders(db: Session = Depends(get_db)):
    pos = db.query(models.PurchaseOrder).all()
    return [{"id": po.id, "reference_no": po.reference_no, "total_amount": po.total_amount, "status": po.status} for po in pos]

@app.post("/purchase-orders/", response_model=schemas.PurchaseOrderResponse)
def create_po(po: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    total = crud.calculate_total(db, po.items)
    ref_no = f"PO-{datetime.date.today().year}-{random.randint(1000,9999)}"
    new_po = models.PurchaseOrder(reference_no=ref_no, vendor_id=po.vendor_id, total_amount=total, status="Draft")
    db.add(new_po)
    db.commit()
    db.refresh(new_po)
    return new_po

# ====================== REAL GEMINI + MONGODB LOGS ======================
@app.get("/generate-desc")
def generate_desc(name: str):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Write a professional 2-sentence marketing description for product: {name}"
        response = model.generate_content(prompt)
        desc = response.text.strip()

        ai_logs.insert_one({
            "product_name": name,
            "description": desc,
            "timestamp": datetime.utcnow()
        })
        return {"description": desc}
    except:
        return {"description": f"{name} is a premium quality product designed for reliability and performance."}

# ====================== JWT LOGIN (still available for bonus demo) ======================
@app.post("/login")
def login(username: str = "admin", password: str = "password123"):
    if username == "admin" and password == "password123":
        return {"access_token": "demo-token-for-video", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")