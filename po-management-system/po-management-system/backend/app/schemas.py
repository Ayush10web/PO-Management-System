from pydantic import BaseModel
from typing import List

class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class PurchaseOrderCreate(BaseModel):
    vendor_id: int
    items: List[PurchaseOrderItemCreate]