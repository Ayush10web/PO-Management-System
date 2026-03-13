from pydantic import BaseModel
from typing import List

class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class PurchaseOrderCreate(BaseModel):
    vendor_id: int
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderResponse(BaseModel):
    id: int
    reference_no: str
    total_amount: float
    status: str
