from sqlalchemy.orm import Session
from .models import Product

def calculate_total(db: Session, items):
    total = 0.0
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            total += product.unit_price * item.quantity
    return round(total * 1.05, 2)
