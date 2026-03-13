from sqlalchemy import Column, Integer, String, Float, ForeignKey
from .database import Base

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String)
    rating = Column(Float, default=4.0)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True)
    unit_price = Column(Float, nullable=False)
    stock_level = Column(Integer, default=0)
    category = Column(String, default="General")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    reference_no = Column(String, unique=True, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    total_amount = Column(Float, default=0.0)
    status = Column(String, default="Draft")
