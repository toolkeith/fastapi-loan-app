from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ToolKeith Loan App")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- WEB PAGES (GET Requests) ---

@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    # This corresponds to p.toolkeith.com
    # We pass data to the template to be rendered
    sample_data = {
        "borrow": 10000,
        "interest_rate": "5%",
        "total_repayment": 10500
    }
    return templates.TemplateResponse("landing.html", {"request": request, "sample": sample_data})

@app.get("/register-page", response_class=HTMLResponse)
def register_page(request: Request):
    # This serves the form for r.toolkeith.com
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/reports", response_class=HTMLResponse)
def report_page(request: Request, db: Session = Depends(get_db)):
    # This corresponds to bi.toolkeith.com
    users = db.query(models.User).all()
    loans = db.query(models.Loan).all()
    
    user_list = [{"id": u.id, "name": f"{u.firstname} {u.lastname}"} for u in users]
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "total_users": len(users),
        "total_loans_count": len(loans),
        "user_list": user_list
    })

# --- ACTION ENDPOINTS (POST Requests) ---

@app.post("/register")
def register_user(
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    age: int = Form(...),
    address: str = Form(...),
    monthly_income: float = Form(...),
    db: Session = Depends(get_db)
):
    # Check if username exists
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return {"error": "Username already taken"}
    
    db_user = models.User(
        username=username,
        firstname=firstname,
        lastname=lastname,
        age=age,
        address=address,
        monthly_income=monthly_income
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # In a real app, we'd redirect to a success page, but for now, return JSON confirmation
    return {"message": "User registered successfully!", "user_id": db_user.id}
