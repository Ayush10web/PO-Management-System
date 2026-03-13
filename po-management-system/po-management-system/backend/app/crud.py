def calculate_total(db, po_create):
    total = 0.0
    for item in po_create.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        line_total = product.unit_price * item.quantity
        total += line_total
    return round(total * 1.05, 2)   # 5% tax