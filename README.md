# Purchase Order Management System - IV Innovations

## How to Run
1. `cd backend`
2. `uvicorn app.main:app --reload`
3. `cd ../frontend`
4. `python -m http.server 8080`
5. Open http://localhost:8080/index.html

## Features
- FastAPI + SQLite backend
- Dynamic "Add Product Row" with jQuery
- Automatic 5% tax calculation
- AI "Auto-Description" button
- Responsive Bootstrap UI
- Dashboard to view all POs

## Database Design
- Proper Primary & Foreign keys
- Total calculated in backend (business logic)

Submitted by: Ayush Raj