# PO Management System

## How to run
1. `psql -f db/schema.sql`
2. `cd backend && uvicorn app.main:app --reload`
3. Open frontend/create-po.html

## DB Design Logic
- Added purchase_order_items because PO needs multiple products (justified as per "assume missing details").
- All FKs with ON DELETE CASCADE for data integrity.
- Total calculated with 5% tax automatically.

Video demo link: https://youtu.be/X