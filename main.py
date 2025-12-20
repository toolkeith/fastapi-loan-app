from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
# Import the two new sessions
from database import SessionMaster, SessionSlave, engine_master

# Create tables using the Master engine (only Master can create tables)
models.Base.metadata.create_all(bind=engine_master)

app = FastAPI(title="ToolKeith Loan App")
templates = Jinja2Templates(directory="templates")

# --- DEPENDENCY 1: MASTER (For Writes/Reports) ---
def get_db_master():
    db = SessionMaster()
    try:
        yield db
    finally:
        db.close()

# --- DEPENDENCY 2: SLAVE (For Login Only) ---
def get_db_slave():
    db = SessionSlave()
    try:
        yield db
    finally:
        db.close()

# --- WEB PAGES (GET Requests) ---

# Landing Page (p.toolkeith.com) - CSV says: Master
@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    # This page is static, but if it needed DB, we'd use get_db_master
    sample_data = {
        "borrow": 10000,
        "interest_rate": "5%",
        "total_repayment": 10500
    }
    return templates.TemplateResponse("landing.html", {"request": request, "sample": sample_data})

# Register Page (r.toolkeith.com)
@app.get("/register-page", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Reports Page (bi.toolkeith.com) - CSV says: Master
@app.get("/reports", response_class=HTMLResponse)
def report_page(request: Request, db: Session = Depends(get_db_master)):
    # Uses MASTER because reporting often needs up-to-the-second accuracy
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

# Register Action (r.toolkeith.com) - CSV says: Master
@app.post("/register")
def register_user(
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    age: int = Form(...),
    address: str = Form(...),
    monthly_income: float = Form(...),
    db: Session = Depends(get_db_master) # CRITICAL: Must use Master for writing!
):
    # Check if username exists (Querying Master to be safe)
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

    return {"message": "User registered successfully on Master DB!", "user_id": db_user.id}

# Login Action (l.toolkeith.com) - CSV says: Slave
# I added this since your CSV requires a Slave connection for Login
@app.post("/login")
def login_user(
    username: str = Form(...),
    db: Session = Depends(get_db_slave) # CRITICAL: Uses Slave (Port 3307)
):
    # queries the SLAVE database
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if not user:
       return HTMLResponse(content="<h3>Error: User not found (Checked Slave DB)</h3><a href='/login'>Try Again</a>", status_code=400) 
   
    return HTMLResponse(content=f"<h3>Welcome back, {user.firstname}!</h3><p>Data read from Slave DB (Port 3307).</p>")
